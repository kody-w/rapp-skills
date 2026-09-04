#!/usr/bin/env python3
"""rapp-skills: the seam between Agent Skills and RAPP single-file agents.

A RAPP agent is ``metadata`` (name, description, JSON-schema parameters) plus
``perform(**kwargs)``. An Agent Skill is ``SKILL.md`` plus optional ``scripts/``.
They are the same capability seen from two sides. This file converts between
them losslessly and never asks a host to learn anything beyond the open
Agent Skills standard (https://agentskills.io/specification).

Commands
  toast     agent.py  -> <skills-dir>/<name>/SKILL.md + scripts/agent.py + scripts/run.py
  compile   <skill>   -> <name>_agent.py   (script-backed: byte-identical; hand-written: playbook agent)
  verify    <skill>   -> exit 1 with the list of problems
  roundtrip <path>    -> proves compile(toast(x)) == x  or  toast(compile(skill)) == skill
  run       <skill> --json '{...}'  -> executes the skill's agent locally
  manifests [--check] -> writes every host-specific manifest from plugin.json, hosts/*.json, agents/*.md

Standard library only. Python 3.11+.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import types
from pathlib import Path

VERSION = "1.0.0"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DEFAULT_PARAMETERS = {
    "type": "object",
    "properties": {
        "request": {
            "type": "string",
            "description": "What the user wants from this skill, in their own words.",
        }
    },
    "required": ["request"],
}

# --------------------------------------------------------------------------- shim
# Everything a RAPP agent may import when it runs outside a Brainstem. This exact
# text is also written into every toasted skill as the head of scripts/run.py, so
# the converter and the runner can never disagree about the contract.

SHIM_SOURCE = r'''
import json as _json, os as _os, sys as _sys, types as _types
from pathlib import Path as _Path


class BasicAgent:
    """BasicAgent contract: name, metadata, perform(**kwargs), to_tool()."""

    def __init__(self, name=None, metadata=None):
        if name is not None:
            self.name = name
        elif not hasattr(self, "name"):
            self.name = "BasicAgent"
        if metadata is not None:
            self.metadata = metadata
        elif not hasattr(self, "metadata"):
            self.metadata = {
                "name": self.name,
                "description": "Base agent -- override this.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            }

    def perform(self, **kwargs):
        return "Not implemented."

    def system_context(self):
        return None

    def to_tool(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.metadata.get("description", ""),
                "parameters": self.metadata.get("parameters", {"type": "object", "properties": {}}),
            },
        }


class AzureFileStorageManager:
    """Local stand-in for the cloud storage helper some agents import.

    Files live under $AGENT_STORAGE (default ~/.agent-storage).
    """

    def __init__(self, share_name=None, **kwargs):
        root = _os.environ.get("AGENT_STORAGE") or str(_Path.home() / ".agent-storage")
        self.root = _Path(root) / (share_name or "default")
        self.root.mkdir(parents=True, exist_ok=True)
        self._context = ""

    def set_memory_context(self, user_guid=None):
        self._context = user_guid or ""

    def _path(self, file_path):
        p = self.root / self._context / (file_path or "memory.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def read_json(self, file_path=None):
        p = self._path(file_path)
        return _json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    def write_json(self, data, file_path=None):
        self._path(file_path).write_text(_json.dumps(data, indent=2), encoding="utf-8")
        return True

    def update_json(self, update_fn, file_path=None):
        data = update_fn(self.read_json(file_path))
        self.write_json(data, file_path)
        return data

    def read_file(self, file_path):
        p = self._path(file_path)
        return p.read_text(encoding="utf-8") if p.exists() else None

    def write_file(self, file_path, content):
        self._path(file_path).write_text(content, encoding="utf-8")
        return True

    def list_files(self, directory=""):
        d = self.root / self._context / directory
        return [x.name for x in d.iterdir()] if d.exists() else []

    def delete_file(self, file_path):
        p = self._path(file_path)
        if p.exists():
            p.unlink()
            return True
        return False

    def file_exists(self, file_path):
        return self._path(file_path).exists()


def install_shims():
    """Make `agents.basic_agent` and `utils.azure_file_storage` importable."""
    if "agents.basic_agent" not in _sys.modules:
        agents_mod = _types.ModuleType("agents")
        agents_mod.__path__ = []
        ba_mod = _types.ModuleType("agents.basic_agent")
        ba_mod.BasicAgent = BasicAgent
        agents_mod.basic_agent = ba_mod
        _sys.modules.setdefault("agents", agents_mod)
        _sys.modules["agents.basic_agent"] = ba_mod
    if "utils.azure_file_storage" not in _sys.modules:
        utils_mod = _sys.modules.get("utils") or _types.ModuleType("utils")
        if not hasattr(utils_mod, "__path__"):
            utils_mod.__path__ = []
        st_mod = _types.ModuleType("utils.azure_file_storage")
        st_mod.AzureFileStorageManager = AzureFileStorageManager
        utils_mod.azure_file_storage = st_mod
        _sys.modules.setdefault("utils", utils_mod)
        _sys.modules["utils.azure_file_storage"] = st_mod


def load_agent(path):
    """Import an agent file by path and return (module, agent instance)."""
    install_shims()
    path = _Path(path).resolve()
    spec = __import__("importlib.util").util.spec_from_file_location("skill_agent_" + path.stem, path)
    module = __import__("importlib.util").util.module_from_spec(spec)
    _sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    base = _sys.modules["agents.basic_agent"].BasicAgent
    candidates = [
        obj for obj in vars(module).values()
        if isinstance(obj, type) and issubclass(obj, base) and obj is not base
        and obj.__module__ == module.__name__
    ]
    if not candidates:
        raise RuntimeError(f"{path.name}: no BasicAgent subclass found")
    return module, candidates[-1]()
'''

RUN_PY = SHIM_SOURCE + r'''

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Run this skill's agent locally.")
    ap.add_argument("--json", default=None, help="arguments as a JSON object")
    ap.add_argument("--describe", action="store_true", help="print the agent's tool definition")
    ap.add_argument("pairs", nargs="*", help="key=value arguments (alternative to --json)")
    args = ap.parse_args(argv)
    here = _Path(__file__).resolve().parent
    module, agent = load_agent(here / "agent.py")
    if args.describe:
        print(_json.dumps(agent.to_tool(), indent=2))
        return 0
    kwargs = _json.loads(args.json) if args.json else {}
    for pair in args.pairs:
        key, _, value = pair.partition("=")
        kwargs[key] = value
    result = agent.perform(**kwargs)
    if isinstance(result, (dict, list)):
        print(_json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result if result is not None else "")
    return 0


if __name__ == "__main__":
    _sys.exit(main())
'''

_shim_ns: dict = {}


def _shim():
    if not _shim_ns:
        exec(compile(SHIM_SOURCE, "<rapp-skills-shim>", "exec"), _shim_ns)
        _shim_ns["install_shims"]()
    return _shim_ns


def load_agent(path: Path):
    return _shim()["load_agent"](path)


# --------------------------------------------------------------------- frontmatter


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Flat YAML frontmatter: scalars plus one-level maps. Returns (fields, body)."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with a '---' frontmatter block")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    block, body = text[4:end], text[end + 5:]
    fields: dict = {}
    current: str | None = None
    for raw in block.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") and current is not None:
            key, _, value = raw.strip().partition(":")
            if not _:
                raise ValueError(f"bad frontmatter line: {raw!r}")
            fields[current][key.strip()] = _unquote(value.strip())
            continue
        key, sep, value = raw.partition(":")
        if not sep or raw.startswith(" "):
            raise ValueError(f"bad frontmatter line: {raw!r}")
        key = key.strip()
        value = value.strip()
        if value == "":
            fields[key] = {}
            current = key
        else:
            fields[key] = _unquote(value)
            current = None
    return fields, body


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        if value[0] == '"':
            return json.loads(value)
        return inner
    return value


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def dump_frontmatter(fields: dict) -> str:
    out = ["---"]
    for key, value in fields.items():
        if isinstance(value, dict):
            out.append(f"{key}:")
            for k, v in value.items():
                out.append(f"  {k}: {_quote(str(v))}")
        else:
            out.append(f"{key}: {_quote(str(value))}")
    out.append("---")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- names


def kebab(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    s = re.sub(r"-+", "-", s)
    if s.endswith("-agent"):
        s = s[: -len("-agent")]
    return s[:64].strip("-") or "skill"


def snake(name: str) -> str:
    return kebab(name).replace("-", "_")


def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in kebab(name).split("-"))


def display(name: str) -> str:
    return " ".join(part.capitalize() for part in kebab(name).split("-"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> str:
    """Byte-exact read: never let the platform translate newlines."""
    return Path(path).read_bytes().decode("utf-8")


def write_text(path: Path, text: str) -> None:
    """Byte-exact write: LF stays LF on every platform."""
    Path(path).write_bytes(text.encode("utf-8"))


AGENT_OPEN = "<!-- agent sha256={sha} -->"
AGENT_CLOSE = "<!-- /agent -->"
RUNNER_OPEN = "<!-- runner -->"
RUNNER_CLOSE = "<!-- /runner -->"


def _fence_for(text: str) -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return fence


def embed_block(source: str, open_marker: str, close_marker: str) -> str:
    fence = _fence_for(source)
    body = source if source.endswith("\n") else source + "\n"
    return f"{open_marker}\n{fence}python\n{body}{fence}\n{close_marker}"


def extract_agent(text: str) -> bytes | None:
    """The embedded agent, byte-exact, verified against the sha in its marker."""
    m = re.search(r"<!-- agent sha256=([0-9a-f]{64}) -->\n(`{3,})python\n(.*?)\n\2\n<!-- /agent -->", text, re.S)
    if not m:
        return None
    expected, inner = m.group(1), m.group(3)
    for candidate in (inner + "\n", inner):
        data = candidate.encode("utf-8")
        if sha256(data) == expected:
            return data
    raise ValueError(f"embedded agent does not match its sha256 {expected[:12]}")


# --------------------------------------------------------------------------- toast



def toast(agent_path: Path, skills_dir: Path, origin: str | None = None,
          license_name: str | None = None) -> Path:
    """agent.py -> skills_dir/<name>/ (SKILL.md, scripts/agent.py, scripts/run.py)."""
    agent_path = Path(agent_path)
    module, agent = load_agent(agent_path)
    skill_md = getattr(module, "SKILL_MD", None)
    if isinstance(skill_md, str) and getattr(module, "__rapp_skills__", {}).get("kind") == "playbook":
        fields, _ = parse_frontmatter(skill_md)
        out = Path(skills_dir) / fields["name"]
        out.mkdir(parents=True, exist_ok=True)
        write_text(out / "SKILL.md", skill_md)
        return out

    meta = dict(agent.metadata)
    tool_name = str(meta.get("name") or agent.name)
    name = kebab(tool_name)
    description = str(meta.get("description") or "").strip() or f"{display(name)} agent."
    parameters = meta.get("parameters") or {"type": "object", "properties": {}, "required": []}
    manifest = getattr(module, "__manifest__", {}) or {}
    agent_bytes = agent_path.read_bytes()

    short = description if len(description) <= 1024 else description[:1000].rstrip() + " ..."
    env_keys = manifest.get("requires_env") or []
    compat = "Requires python3 (3.11+)."
    if env_keys:
        compat += " Environment: " + ", ".join(env_keys) + "."
    metadata = {
        "source": "agent.py",
        "tool-name": tool_name,
        "agent-sha256": sha256(agent_bytes),
    }
    for key in ("version", "author"):
        if manifest.get(key):
            metadata[key] = str(manifest[key])
    if manifest.get("tags"):
        metadata["tags"] = ", ".join(str(t) for t in manifest["tags"])
    if origin:
        metadata["origin"] = origin
    fields = {"name": name, "description": short}
    lic = license_name or manifest.get("license")
    if lic and str(lic).lower() not in ("unverified", "unknown", ""):
        fields["license"] = str(lic)
    fields["compatibility"] = compat
    fields["metadata"] = metadata

    example = {}
    for key, spec in (parameters.get("properties") or {}).items():
        example[key] = f"<{spec.get('type', 'value')}>"
    try:
        agent_text = agent_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{agent_path}: agent must be UTF-8 text to embed in SKILL.md ({exc})") from exc
    runner_text = RUN_PY.lstrip("\n")
    body = [
        f"# {display(name)}",
        "",
        description,
        "",
        "## Parameters",
        "",
        "```json",
        json.dumps(parameters, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Run",
        "",
        "Pass the arguments as one JSON object. This file is self-contained: everything",
        "needed to run it is below.",
        "",
        "1. If `scripts/run.py` exists beside this file, run from this skill's directory:",
        "",
        "   ```bash",
        f"   python3 scripts/run.py --json '{json.dumps(example, ensure_ascii=False)}'",
        "   ```",
        "",
        "2. Otherwise save the **Agent** block below as `agent.py` and the **Runner** block as",
        "   `run.py` in one directory, then run `python3 run.py --json '...'` there.",
        "3. If Python is unavailable, read the Agent block and carry out its `perform`",
        "   method yourself; it is the exact specification of this skill.",
        "",
        "Return the printed output to the user as the result.",
        "",
        "## Agent",
        "",
        "The agent, unmodified from its source. Its sha256 is in the marker.",
        "",
        embed_block(agent_text, AGENT_OPEN.format(sha=sha256(agent_bytes)), AGENT_CLOSE),
        "",
        "## Runner",
        "",
        "Loads the agent above and calls `perform` with your JSON arguments.",
        "",
        embed_block(runner_text, RUNNER_OPEN, RUNNER_CLOSE),
        "",
    ]
    out = Path(skills_dir) / name
    (out / "scripts").mkdir(parents=True, exist_ok=True)
    write_text(out / "SKILL.md", dump_frontmatter(fields) + "\n" + "\n".join(body))
    (out / "scripts" / "agent.py").write_bytes(agent_bytes)
    write_text(out / "scripts" / "run.py", runner_text)
    return out


# ------------------------------------------------------------------------- compile


def _parameters_block(body: str) -> dict | None:
    m = re.search(r"## Parameters\s*\n+```json\n(.*?)\n```", body, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def _skill_md(path: Path) -> tuple[Path, Path]:
    """Accept a skill directory or a SKILL.md path; return (skill_dir, SKILL.md)."""
    path = Path(path)
    return (path.parent, path) if path.is_file() else (path, path / "SKILL.md")


def compile_skill(skill_dir: Path, out_dir: Path) -> Path:
    """<skill>/ or SKILL.md -> out_dir/<snake>_agent.py."""
    skill_dir, md = _skill_md(skill_dir)
    text = read_text(md)
    fields, body = parse_frontmatter(text)
    name = fields["name"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = verify(md)
    if problems:
        raise RuntimeError("refusing to compile a skill that does not verify:\n  " + "\n  ".join(problems))
    script = skill_dir / "scripts" / "agent.py"
    agent_bytes = script.read_bytes() if script.is_file() else extract_agent(text)
    if agent_bytes is not None:
        target = out_dir / f"{snake(name)}_agent.py"
        target.write_bytes(agent_bytes)
        return target

    parameters = _parameters_block(body) or DEFAULT_PARAMETERS
    class_name = pascal(name) + "Agent"
    tool_name = snake(name)
    source = f'''"""{display(name)} -- playbook agent compiled by rapp-skills {VERSION} from SKILL.md.

The skill text is the specification. perform() returns it, rendered with the
caller's inputs, for the host model to carry out. No network, no dependencies.
"""

__rapp_skills__ = {{"kind": "playbook", "skill": {name!r}, "version": {VERSION!r}}}

SKILL_MD = {text!r}

import json

try:
    from agents.basic_agent import BasicAgent
except ModuleNotFoundError:  # running outside a Brainstem
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name = name or "BasicAgent"
            self.metadata = metadata or {{}}

        def to_tool(self):
            return {{"type": "function", "function": {{"name": self.name,
                    "description": self.metadata.get("description", ""),
                    "parameters": self.metadata.get("parameters", {{"type": "object", "properties": {{}}}})}}}}


def _skill_body():
    end = SKILL_MD.find("\\n---\\n", 4)
    return SKILL_MD[end + 5:].strip() if SKILL_MD.startswith("---\\n") and end > 0 else SKILL_MD.strip()


class {class_name}(BasicAgent):
    def __init__(self):
        self.name = {tool_name!r}
        self.metadata = {{
            "name": self.name,
            "description": {fields.get("description", "")!r},
            "parameters": {json.dumps(parameters, ensure_ascii=False)},
        }}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        inputs = json.dumps(kwargs, indent=2, sort_keys=True, ensure_ascii=False)
        return (
            "Carry out the following skill exactly as written, using the inputs.\\n\\n"
            + _skill_body()
            + "\\n\\n## Inputs\\n\\n```json\\n" + inputs + "\\n```"
        )
'''
    target = out_dir / f"{tool_name}_agent.py"
    target
    return target


# -------------------------------------------------------------------------- verify


def verify(skill_dir: Path) -> list[str]:
    """Return problems (empty list = the skill is valid and self-consistent)."""
    skill_dir, md = _skill_md(skill_dir)
    problems: list[str] = []
    if not md.is_file():
        return [f"{skill_dir}: no SKILL.md"]
    text = read_text(md)
    try:
        fields, body = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{md}: {exc}"]
    name = fields.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        problems.append(f"{md}: name must be 1-64 chars, lowercase letters, digits and single hyphens (got {name!r})")
    elif name != skill_dir.name:
        problems.append(f"{md}: name {name!r} must equal the directory name {skill_dir.name!r}")
    desc = fields.get("description")
    if not isinstance(desc, str) or not 1 <= len(desc) <= 1024:
        problems.append(f"{md}: description must be 1-1024 characters")
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    extra = set(fields) - allowed
    if extra:
        problems.append(f"{md}: non-standard frontmatter keys {sorted(extra)} (only the six Agent Skills fields are allowed)")
    meta = fields.get("metadata")
    if meta is not None and (not isinstance(meta, dict) or any(not isinstance(v, str) for v in meta.values())):
        problems.append(f"{md}: metadata must be a flat map of strings")
    params = None
    try:
        params = _parameters_block(body)
    except json.JSONDecodeError as exc:
        problems.append(f"{md}: Parameters block is not valid JSON ({exc})")
    if params is not None and params.get("type") != "object":
        problems.append(f"{md}: Parameters schema must have type object")

    try:
        embedded = extract_agent(text)
    except ValueError as exc:
        problems.append(f"{md}: {exc}")
        embedded = None
    script = skill_dir / "scripts" / "agent.py"
    if script.is_file() and embedded is not None and script.read_bytes() != embedded:
        problems.append(f"{script}: differs from the agent embedded in SKILL.md")
    if (meta or {}).get("source") == "agent.py" and embedded is None and not script.is_file():
        problems.append(f"{md}: metadata says source agent.py but no agent is embedded or bundled")
    if script.is_file() or embedded is not None:
        data = script.read_bytes() if script.is_file() else embedded
        expected = (meta or {}).get("agent-sha256")
        if expected and expected != sha256(data):
            problems.append(f"{md}: agent sha256 {sha256(data)[:12]} does not match metadata.agent-sha256 {expected[:12]}")
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            probe = Path(tmp) / "agent.py"
            probe.write_bytes(data)
            try:
                _, agent = load_agent(probe)
            except Exception as exc:  # noqa: BLE001 - report, never crash
                problems.append(f"{md}: agent does not load ({exc.__class__.__name__}: {exc})")
                agent = None
        if agent is not None:
            if not callable(getattr(agent, "perform", None)):
                problems.append(f"{md}: agent has no perform()")
            tool = (meta or {}).get("tool-name")
            if tool and str(agent.metadata.get("name") or agent.name) != tool:
                problems.append(f"{md}: agent metadata.name {agent.metadata.get('name')!r} != frontmatter tool-name {tool!r}")
            if params is not None and agent.metadata.get("parameters") != params:
                problems.append(f"{md}: agent parameters differ from the Parameters block")
        if script.is_file() and not (skill_dir / "scripts" / "run.py").is_file():
            problems.append(f"{skill_dir}: scripts/run.py missing (re-toast to regenerate)")
    return problems


# ------------------------------------------------------------------------ roundtrip


def roundtrip(path: Path, tmp: Path) -> tuple[bool, str]:
    path = Path(path)
    tmp = Path(tmp)
    if path.is_dir() or path.name == "SKILL.md":
        if path.is_file():
            path = path.parent
        compiled = compile_skill(path, tmp / "agents")
        toasted = toast(compiled, tmp / "skills")
        a = (path / "SKILL.md").read_bytes()
        b = (toasted / "SKILL.md").read_bytes()
        script = path / "scripts" / "agent.py"
        if script.is_file():
            same = script.read_bytes() == (toasted / "scripts" / "agent.py").read_bytes()
            return same, "scripts/agent.py survived compile->toast" if same else "scripts/agent.py changed"
        return a == b, "SKILL.md byte-identical after compile->toast" if a == b else "SKILL.md changed after compile->toast"
    toasted = toast(path, tmp / "skills")
    compiled = compile_skill(toasted, tmp / "agents")
    same = path.read_bytes() == compiled.read_bytes()
    return same, f"{path.name} byte-identical after toast->compile" if same else f"{path.name} changed after toast->compile"


# ------------------------------------------------------------------------ manifests


def _load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def _dump_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def render_manifests(root: Path) -> dict[str, str]:
    """Every generated file as {relative path: content}, from the sources of truth."""
    root = Path(root)
    plugin = _load_json(root / "plugin.json")
    hosts = {p.stem: _load_json(p) for p in sorted((root / "hosts").glob("*.json"))}
    files: dict[str, str] = {}
    marketplace = {
        "name": plugin["name"],
        "owner": plugin["author"],
        "metadata": {"description": plugin["description"], "version": plugin["version"]},
        "plugins": [
            {
                "name": plugin["name"],
                "description": plugin["description"],
                "version": plugin["version"],
                "source": "./",
                "category": plugin.get("category", "productivity"),
                "tags": plugin.get("keywords", []),
            }
        ],
    }
    for host in hosts.values():
        files[host["plugin_manifest"]] = _dump_json(plugin)
        files[host["marketplace"]] = _dump_json(marketplace)
    files["plugin.json"] = _dump_json(plugin)

    for src in sorted((root / "agents").glob("*.md")):
        fields, body = parse_frontmatter(read_text(src))
        for host in hosts.values():
            spec = host["agents"]
            if spec["dir"] == "agents" and spec["suffix"] == ".md":
                continue  # the source file already is this host's format
            projected = {k: fields[k] for k in spec["frontmatter"] if k in fields}
            files[f"{spec['dir']}/{src.stem}{spec['suffix']}"] = dump_frontmatter(projected) + body

    hosts_md = ["# Hosts", "", "Each host is one JSON adapter in `hosts/`. Adding an ecosystem is adding a file.", "",
                "| Host | Verified version | Verified on | Skills read from | Plugin manifest | Marketplace | Agents |", "|---|---|---|---|---|---|---|"]
    for key, host in hosts.items():
        v = host.get("verified", {})
        hosts_md.append(
            f"| {host['display']} | {v.get('version', '-')} | {v.get('date', '-')} | "
            + ", ".join(f"`{d}`" for d in host["skill_dirs"]) + f" | `{host['plugin_manifest']}` | `{host['marketplace']}` | "
            + f"`{host['agents']['dir']}/*{host['agents']['suffix']}` |"
        )
    hosts_md += ["", "## Install", ""]
    for key, host in hosts.items():
        hosts_md.append(f"**{host['display']}**")
        hosts_md.append("")
        hosts_md.append("```")
        hosts_md.extend(host["install"])
        hosts_md.append("```")
        hosts_md.append("")
        hosts_md.append(f"Skill invocation: `{host['skill_invocation']}`. Instruction files read: "
                        + ", ".join(f"`{f}`" for f in host["instruction_files"]) + f". Docs: {host['docs']}")
        if host.get("evidence"):
            hosts_md.append("")
            hosts_md.append(f"Verified: {host['evidence']}")
        hosts_md.append("")
    files["HOSTS.md"] = "\n".join(hosts_md).rstrip("\n") + "\n"
    return files


def manifests(root: Path, check: bool = False) -> list[str]:
    root = Path(root)
    drift: list[str] = []
    for rel, content in render_manifests(root).items():
        target = root / rel
        if check:
            if not target.is_file() or read_text(target) != content:
                drift.append(rel)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            write_text(target, content)
    return drift


# ------------------------------------------------------------------------------ cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="rapp-skills", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("toast", help="agent.py -> skill directory")
    p.add_argument("agent")
    p.add_argument("--out", default="skills", help="skills directory (default: skills)")
    p.add_argument("--origin", default=None, help="URL of the agent's source, recorded in metadata")
    p.add_argument("--license", default=None)
    p = sub.add_parser("compile", help="skill directory -> <name>_agent.py")
    p.add_argument("skill")
    p.add_argument("--out", default="agents")
    p = sub.add_parser("verify", help="validate one or more skill directories")
    p.add_argument("skills", nargs="+")
    p = sub.add_parser("roundtrip", help="prove the conversion is lossless for a path")
    p.add_argument("path")
    p = sub.add_parser("run", help="run a skill's agent locally")
    p.add_argument("skill")
    p.add_argument("--json", default="{}")
    p = sub.add_parser("manifests", help="write (or --check) every host manifest from the sources of truth")
    p.add_argument("--root", default=".")
    p.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.cmd == "toast":
        out = toast(Path(args.agent), Path(args.out), origin=args.origin, license_name=args.license)
        problems = verify(out)
        print(f"toasted {args.agent} -> {out}")
        if problems:
            print("\n".join(problems))
            return 1
        return 0
    if args.cmd == "compile":
        print(compile_skill(Path(args.skill), Path(args.out)))
        return 0
    if args.cmd == "verify":
        rc = 0
        for s in args.skills:
            problems = verify(Path(s))
            print(f"{'ok  ' if not problems else 'FAIL'} {s}")
            for line in problems:
                print("     " + line)
            rc |= 1 if problems else 0
        return rc
    if args.cmd == "roundtrip":
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ok, msg = roundtrip(Path(args.path), Path(tmp))
        print(("PASS " if ok else "FAIL ") + msg)
        return 0 if ok else 1
    if args.cmd == "run":
        runner = Path(args.skill) / "scripts" / "run.py"
        if not runner.is_file():
            print("this skill has no scripts/run.py; it is a playbook for the host model", file=sys.stderr)
            return 2
        return subprocess.call([sys.executable, str(runner), "--json", args.json])
    if args.cmd == "manifests":
        drift = manifests(Path(args.root), check=args.check)
        if args.check:
            if drift:
                print("manifest drift (run `rapp_skills.py manifests`):\n  " + "\n  ".join(drift))
                return 1
            print("manifests current")
        else:
            print("manifests written")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
