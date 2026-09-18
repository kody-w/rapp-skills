#!/usr/bin/env python3
"""rapp-skills: the seam between Agent Skills and RAPP single-file agents.

A RAPP agent is ``metadata`` (name, description, JSON-schema parameters) plus
``perform(**kwargs)``. An Agent Skill is ``SKILL.md`` plus optional ``scripts/``.
They are the same capability seen from two sides. This file converts between
them losslessly and never asks a host to learn anything beyond the open
Agent Skills standard (https://agentskills.io/specification).

Commands (plain verbs; no concepts to learn)
  to-skill  agent.py  -> <skills-dir>/<name>/SKILL.md (+ scripts/): a skill anyone can use
  to-agent  <skill>   -> <name>_agent.py: the same capability as one Python file for a server
  check     <skill>   -> exit 1 with the list of problems
  prove     <path>    -> shows nothing is lost going there and back
  run       <skill> --json '{...}'  -> runs the skill's code here
  sync      [--check] -> rewrites host files and verifies pinned sources from the repository records

Standard library only. Python 3.11+.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path, PurePosixPath
from typing import Any

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
# What an agent means when its metadata has no usable "parameters" (key missing, or empty).
EMPTY_PARAMETERS = {"type": "object", "properties": {}, "required": []}

# --------------------------------------------------------------------------- shim
# Everything a RAPP agent may import when it runs outside a Brainstem. This exact
# text is also written into every toasted skill as the head of scripts/run.py, so
# the converter and the runner can never disagree about the contract.

SHIM_SOURCE = r'''
import hashlib as _hashlib, json as _json, os as _os, sys as _sys, types as _types
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

    Used only if the agent itself saves something. Everything goes under one
    folder, $AGENT_STORAGE (default ~/.agent-storage); delete it to erase all of it.
    Nothing can be read or written outside that folder: a path that would leave it
    (".." or an absolute path) is refused, the same as on a real server. A share
    name never becomes a path either: each named share gets its own folder under
    shares/, named by the sha256 of the name (lower-cased, trimmed), as on a server.
    """

    DEFAULT_MARKER_GUID = "c0p110t0-aaaa-bbbb-cccc-123456789abc"
    _RESERVED_STEMS = {"CON", "PRN", "AUX", "NUL", *("COM%d" % i for i in range(1, 10)), *("LPT%d" % i for i in range(1, 10))}

    def __init__(self, share_name=None, **kwargs):
        root = _os.environ.get("AGENT_STORAGE") or str(_Path.home() / ".agent-storage")
        self.base = _Path(root)
        share = str(share_name or "").strip().lower()
        self.share_name = share or None
        if share:
            self.root = self.base / "shares" / _hashlib.sha256(share.encode("utf-8")).hexdigest()
        else:
            self.root = self.base / "default"
        self.root.mkdir(parents=True, exist_ok=True)
        # What agents read off the helper, named as on a server: the share's folder,
        # the shared memory folder, the memory file name, and the current context.
        self.storage_root = self.root
        self.shared_memory_path = self.root
        self.default_file_name = "memory.json"
        self.current_guid = None
        self.current_memory_path = self.shared_memory_path

    def set_memory_context(self, user_guid=None):
        """One sub-folder per user. None, "" or the marker guid means the shared folder. Returns True."""
        if user_guid is None or user_guid == "" or user_guid == self.DEFAULT_MARKER_GUID:
            self.current_guid = None
            self.current_memory_path = self.shared_memory_path
            return True
        self._folder_name(user_guid)
        self.current_guid = user_guid
        self.current_memory_path = self.root / user_guid
        return True

    def _folder_name(self, user_guid):
        """user_guid when it is one literal folder name; ValueError otherwise (the server's rule)."""
        if not isinstance(user_guid, str):
            raise ValueError("user_guid must be a string")
        if (user_guid in ("", ".", "..") or user_guid.endswith((".", " "))
                or any(ch in '<>:"/\\|?*' or ord(ch) < 32 for ch in user_guid)
                or user_guid.split(".", 1)[0].upper() in self._RESERVED_STEMS):
            raise ValueError("user_guid must be a single path component")
        return user_guid

    def _inside(self, *parts):
        """The resolved path of root/parts; refuses anything that leaves this share's folder.

        The folder checked against is always a fixed child of self.base (the
        $AGENT_STORAGE folder), never anything a caller chose, so nothing an agent
        passes in can move the boundary.
        """
        base = self.root.resolve()
        p = self.root.joinpath(*parts).resolve()
        if p != base and base not in p.parents:
            raise ValueError("path escapes data directory: " + "/".join(str(x) for x in parts if str(x)))
        return p

    def _path(self, file_path):
        p = self._inside(self.current_guid or "", file_path or self.default_file_name)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def ensure_directory_exists(self, directory_path=""):
        """Create a folder inside the store, under the current memory context, and return its path."""
        d = self._inside(self.current_guid or "", directory_path or "")
        d.mkdir(parents=True, exist_ok=True)
        return d

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
        d = self._inside(self.current_guid or "", directory)
        return [x.name for x in d.iterdir()] if d.exists() else []

    def delete_file(self, file_path):
        p = self._path(file_path)
        if p.exists():
            p.unlink()
            return True
        return False

    def file_exists(self, file_path):
        return self._path(file_path).exists()


def get_storage_manager(*args, **kwargs):
    """What utils.storage_factory hands out on a server: the one storage helper."""
    return AzureFileStorageManager(*args, **kwargs)


# Every module name a RAPP agent may import, and what each must hold. This is
# exactly what a server exposes: BasicAgent under three names (a bare import works
# there because the agents folder is on sys.path), and one local storage helper
# under the three names cloud agents use for it.
_BASIC_AGENT_ALIASES = ("basic_agent", "agents.basic_agent", "openrappter.agents.basic_agent")
_STORAGE_ALIASES = {
    "utils.azure_file_storage": {"AzureFileStorageManager": AzureFileStorageManager},
    "utils.dynamics_storage": {"DynamicsStorageManager": AzureFileStorageManager},
    "utils.storage_factory": {"get_storage_manager": get_storage_manager},
}


def _shim_table():
    """{module name: {attribute: value}} for install_shims, from the alias tables above.

    Every BasicAgent alias exposes one class: the one an already-present alias
    holds (a real server's, when running inside one), else the stand-in above.
    """
    base = BasicAgent
    for name in _BASIC_AGENT_ALIASES:
        present = _sys.modules.get(name)
        if isinstance(getattr(present, "BasicAgent", None), type):
            base = present.BasicAgent
            break
    table = {name: {"BasicAgent": base} for name in _BASIC_AGENT_ALIASES}
    table.update(_STORAGE_ALIASES)
    return table


def _register_module(dotted, attrs):
    """Put a module holding attrs in sys.modules under dotted, creating parent packages as needed.

    A module already present under any of those names is left exactly as it is;
    a parent only gains a __path__ (so it counts as a package) and an attribute
    for the child when it has neither.
    """
    parts = dotted.split(".")
    parent = None
    for depth in range(1, len(parts) + 1):
        name = ".".join(parts[:depth])
        module = _sys.modules.get(name)
        if module is None:
            module = _types.ModuleType(name)
            if depth == len(parts):
                for attr, value in attrs.items():
                    setattr(module, attr, value)
            _sys.modules[name] = module
        if depth < len(parts) and not hasattr(module, "__path__"):
            module.__path__ = []
        if parent is not None and not hasattr(parent, parts[depth - 1]):
            setattr(parent, parts[depth - 1], module)
        parent = module


def install_shims():
    """Make every module name in the alias tables importable; never replace one already imported."""
    for dotted, attrs in _shim_table().items():
        _register_module(dotted, attrs)


def _import_agent_module(path):
    install_shims()
    path = _Path(path).resolve()
    util = __import__("importlib.util").util
    spec = util.spec_from_file_location("skill_agent_" + path.stem, path)
    module = util.module_from_spec(spec)
    _sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _agent_name(agent):
    return str(agent.metadata.get("name") or agent.name)


def _agents_in(module):
    """[(attribute name, instance), ...] for every agent the module defines, in definition order.

    An agent is a class defined in that module that subclasses BasicAgent (not
    BasicAgent itself), has a callable perform, and whose name does not start
    with "_". This is what a server serves from the file, so it is what a skill
    sees too.
    """
    base = _sys.modules["agents.basic_agent"].BasicAgent
    agents = []
    for attr, obj in list(vars(module).items()):
        if attr.startswith("_") or not isinstance(obj, type):
            continue
        if obj is base or not issubclass(obj, base) or obj.__module__ != module.__name__:
            continue
        if not callable(getattr(obj, "perform", None)):
            continue
        agents.append((attr, obj()))
    return agents


def load_agents(path):
    """Import an agent file by path and return [(attribute name, agent instance), ...]."""
    agents = _agents_in(_import_agent_module(path))
    if not agents:
        raise RuntimeError(f"{_Path(path).name}: no BasicAgent subclass found")
    return agents


def load_agent(path, tool_name=None):
    """Import an agent file by path and return (module, agent instance).

    The file's only agent when it defines one. When it defines several, the one
    whose tool name equals tool_name; without a match, an error naming them all.
    """
    module = _import_agent_module(path)
    agents = _agents_in(module)
    if not agents:
        raise RuntimeError(f"{_Path(path).name}: no BasicAgent subclass found")
    if len(agents) == 1:
        return module, agents[0][1]
    names = [_agent_name(agent) for _, agent in agents]
    if tool_name is not None:
        for name, (_, agent) in zip(names, agents):
            if name == tool_name:
                return module, agent
        raise RuntimeError(f"{_Path(path).name} has no agent named {tool_name!r}; it defines: {', '.join(names)}")
    raise RuntimeError(f"{_Path(path).name} defines {len(agents)} agents ({', '.join(names)}); choose one by its tool name")
'''

RUN_PY = SHIM_SOURCE + r'''

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Run this skill's agent locally.")
    ap.add_argument("--json", default=None, help="arguments as a JSON object")
    ap.add_argument("--tool", default=None, help="which agent to run when agent.py defines several (its tool name)")
    ap.add_argument("--describe", action="store_true", help="print the agent's tool definition")
    ap.add_argument("pairs", nargs="*", help="key=value arguments (alternative to --json)")
    args = ap.parse_args(argv)
    here = _Path(__file__).resolve().parent
    try:
        module, agent = load_agent(here / "agent.py", args.tool)
    except RuntimeError as exc:
        hint = " (run again with --tool <name>)" if args.tool is None and "choose one" in str(exc) else ""
        print(f"error: {exc}{hint}", file=_sys.stderr)
        return 2
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
        exec(  # noqa: S102 - execute the converter's fixed bundled shim
            compile(SHIM_SOURCE, "<rapp-skills-shim>", "exec"),
            _shim_ns,
        )
        _shim_ns["install_shims"]()
    return _shim_ns


def load_agent(path: Path, tool_name: str | None = None):
    return _shim()["load_agent"](path, tool_name)


def load_agents(path: Path) -> list:
    return _shim()["load_agents"](path)


def _load_module_and_agents(path: Path):
    """(module, [(attribute name, instance), ...]) for an agent file; error if it has no agent."""
    shim = _shim()
    module = shim["_import_agent_module"](path)
    agents = shim["_agents_in"](module)
    if not agents:
        raise RuntimeError(f"{Path(path).name}: no BasicAgent subclass found")
    return module, agents


def _agent_name(agent) -> str:
    return str(agent.metadata.get("name") or agent.name)


def _agent_parameters(agent) -> dict:
    """The agent's parameters exactly as the 'What it needs' block will show them.

    Missing or empty parameters become the empty object schema; a pass through
    JSON turns tuples into lists, so to-skill and check see the same thing.
    """
    return json.loads(json.dumps(agent.metadata.get("parameters") or EMPTY_PARAMETERS, ensure_ascii=False))


# --------------------------------------------------------------------- frontmatter


def unwrap_sealed(text: str) -> str:
    """A sealed skill wraps a plain skill between RAW-SKILL markers with its sha256.

    Returns the plain skill inside after checking the seal; returns text unchanged
    when it is not sealed. Raises when the seal does not match.
    """
    begin = re.search(r"<!-- RAW-SKILL-BEGIN sha256=([0-9a-f]{64}) -->\n", text)
    if not begin:
        return text
    expected = begin.group(1)
    # The inner text may itself contain an END marker line (a skill that documents
    # sealing, or a sealed skill sealed again), so the seal, not the first marker,
    # decides where the inner text ends: every END marker is tried against the sha.
    rest = text[begin.end():]
    ends = [m.start() for m in re.finditer(r"\n<!-- RAW-SKILL-END -->", rest)]
    if not ends:
        return text
    for end in ends:
        inner = rest[:end]
        for candidate in (inner + "\n", inner):
            if sha256(candidate.encode("utf-8")) == expected:
                return candidate
    raise ValueError("sealed skill: the seal does not match the contents")


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
    s = s.removesuffix("-agent")
    return s[:64].strip("-") or "skill"


def snake(name: str) -> str:
    return kebab(name).replace("-", "_")


def pascal(name: str) -> str:
    name = "".join(part.capitalize() for part in kebab(name).split("-"))
    # A class name cannot start with a digit; "3d-print" becomes Skill3dPrint.
    return ("Skill" + name) if name[:1].isdigit() else name


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


def load_skill_text(path: Path) -> str:
    """A SKILL.md as it was written, less what a platform added on the way.

    A leading UTF-8 byte-order mark and uniform CRLF line endings are the signature
    of an editor or a checkout translating the file (Notepad, PowerShell 5,
    core.autocrlf). Both are undone here, and this is the only way the converter
    reads a skill, so the frontmatter, the seal, and the embedded code's sha256 all
    read as written. A file with mixed endings is left byte-exact: that is content.
    """
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8")
    crlf = text.count("\r\n")
    if crlf and crlf == text.count("\n"):
        text = text.replace("\r\n", "\n")
    return text


AGENT_OPEN = "<!-- agent sha256={sha} -->"
AGENT_CLOSE = "<!-- /agent -->"
RUNNER_OPEN = "<!-- runner sha256={sha} -->"
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


def extract_runner(text: str) -> tuple[str | None, str | None]:
    """The embedded launcher and the sha256 its marker claims (None for the older bare marker)."""
    m = re.search(r"<!-- runner(?: sha256=([0-9a-f]{64}))? -->\n(`{3,})python\n(.*?)\n\2\n<!-- /runner -->", text, re.DOTALL)
    if not m:
        return None, None
    return m.group(3) + "\n", m.group(1)


def extract_agent(text: str) -> bytes | None:
    """The embedded agent, byte-exact, verified against the sha in its marker."""
    m = re.search(r"<!-- agent sha256=([0-9a-f]{64}) -->\n(`{3,})python\n(.*?)\n\2\n<!-- /agent -->", text, re.DOTALL)
    if not m:
        return None
    expected, inner = m.group(1), m.group(3)
    for candidate in (inner + "\n", inner):
        data = candidate.encode("utf-8")
        if sha256(data) == expected:
            return data
    raise ValueError(f"embedded agent does not match its sha256 {expected[:12]}")


# --------------------------------------------------------------------------- toast



def toast_all(agent_path: Path, skills_dir: Path, origin: str | None = None,
              license_name: str | None = None, tool_name: str | None = None,
              seen: dict[str, Path] | None = None) -> list[Path]:
    """agent.py -> skills_dir/<name>/ (SKILL.md, scripts/agent.py, scripts/run.py) per agent.

    A file usually defines one agent and yields one skill. A file that defines
    several yields one skill per agent, each naming its own tool and carrying the
    same code; tool_name limits that to one of them.
    """
    return _toast(Path(agent_path), Path(skills_dir), origin, license_name, tool_name, require_one=False, seen=seen)


def toast(agent_path: Path, skills_dir: Path, origin: str | None = None,
          license_name: str | None = None, tool_name: str | None = None) -> Path:
    """agent.py -> one skill folder: the file's only agent, or the one named tool_name."""
    return _toast(Path(agent_path), Path(skills_dir), origin, license_name, tool_name, require_one=True)[0]


def _toast(agent_path: Path, skills_dir: Path, origin: str | None, license_name: str | None,
           tool_name: str | None, require_one: bool, seen: dict[str, Path] | None = None) -> list[Path]:
    """seen maps skill name -> source file across one whole run, so two files whose tools
    would become the same skill are refused instead of the second silently replacing the first."""
    module, agents = _load_module_and_agents(agent_path)
    skill_md = getattr(module, "SKILL_MD", None)
    if isinstance(skill_md, str) and getattr(module, "__rapp_skills__", {}).get("kind") == "playbook":
        fields, _ = parse_frontmatter(skill_md)
        out = skills_dir / fields["name"]
        out.mkdir(parents=True, exist_ok=True)
        write_text(out / "SKILL.md", skill_md)
        return [out]

    several = len(agents) > 1
    names = [_agent_name(agent) for _, agent in agents]
    chosen = [agent for _, agent in agents]
    if tool_name is not None:
        chosen = [agent for name, agent in zip(names, chosen) if name == tool_name]
        if not chosen:
            raise RuntimeError(f"{agent_path.name} has no agent named {tool_name!r}; it defines: {', '.join(names)}")
    elif require_one and several:
        raise RuntimeError(f"{agent_path.name} defines {len(agents)} agents ({', '.join(names)}); choose one by its tool name")
    by_skill: dict[str, object] = {}
    for agent in chosen:
        skill = kebab(_agent_name(agent))
        if skill in by_skill:
            raise RuntimeError(f"{agent_path.name}: agents {_agent_name(by_skill[skill])!r} and {_agent_name(agent)!r} would both become the skill {skill!r}")
        if seen is not None and skill in seen and seen[skill] != agent_path:
            raise RuntimeError(f"{agent_path.name} and {seen[skill].name} would both become the skill {skill!r}; rename one tool")
        by_skill[skill] = agent
    if seen is not None:
        for skill in by_skill:
            seen[skill] = agent_path
    return [_toast_one(module, agent, agent_path, skills_dir, origin, license_name, several) for agent in by_skill.values()]


def _toast_one(module, agent, agent_path: Path, skills_dir: Path, origin: str | None,
               license_name: str | None, several: bool) -> Path:
    meta = dict(agent.metadata)
    tool_name = _agent_name(agent)
    name = kebab(tool_name)
    description = str(meta.get("description") or "").strip() or f"{display(name)} agent."
    parameters = _agent_parameters(agent)
    manifest = getattr(module, "__manifest__", {}) or {}
    agent_bytes = agent_path.read_bytes()

    short = description if len(description) <= 1024 else description[:1000].rstrip() + " ..."
    env_keys = manifest.get("requires_env") or []
    compat = "Requires python3 (3.11+)."
    if env_keys:
        compat += " Environment: " + ", ".join(env_keys) + "."
    metadata = {
        "source": "agent.py",
        "file": agent_path.name,
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
    tool_flag = f"--tool {tool_name} " if several else ""
    body = [
        f"# {display(name)}",
        "",
        description,
        "",
        "## What it needs",
        "",
        "```json",
        json.dumps(parameters, indent=2, ensure_ascii=False),
        "```",
        "",
        "## How to run it",
        "",
        "Pass what it needs as one JSON object. This file is complete on its own: everything",
        "needed to run it is below.",
        "",
        "1. If `scripts/run.py` exists beside this file, run from this skill's directory:",
        "",
        "   ```bash",
        f"   python3 scripts/run.py {tool_flag}--json '{json.dumps(example, ensure_ascii=False)}'",
        "   ```",
        "",
        "2. Otherwise save the **code** block below as `agent.py` and the **launcher** block as",
        f"   `run.py` in one directory, then run `python3 run.py {tool_flag}--json '...'` there.",
        "3. If Python is unavailable, read the code block and do what its `perform`",
        "   method does yourself; it is the exact description of this skill.",
        *([
            "",
            f"The code defines more than one tool; this skill is `{tool_name}`, so use that class",
            "(the launcher needs `--tool` to know which one you mean).",
        ] if several else []),
        "",
        "Return the printed output to the user as the result.",
        "",
        "## The code",
        "",
        "The code that does the work, unmodified from its source. Its sha256 is in the marker.",
        "",
        embed_block(agent_text, AGENT_OPEN.format(sha=sha256(agent_bytes)), AGENT_CLOSE),
        "",
        "## The launcher",
        "",
        "Loads the code above and calls `perform` with your JSON input.",
        "",
        embed_block(runner_text, RUNNER_OPEN.format(sha=sha256(runner_text.encode("utf-8"))), RUNNER_CLOSE),
        "",
    ]
    out = skills_dir / name
    _refuse_to_replace_another_source(out, agent_path)
    (out / "scripts").mkdir(parents=True, exist_ok=True)
    write_text(out / "SKILL.md", dump_frontmatter(fields) + "\n" + "\n".join(body))
    (out / "scripts" / "agent.py").write_bytes(agent_bytes)
    write_text(out / "scripts" / "run.py", runner_text)
    return out


def _refuse_to_replace_another_source(out: Path, agent_path: Path) -> None:
    """A skill folder written from one source file is never overwritten from another."""
    existing = out / "SKILL.md"
    if not existing.is_file():
        return
    try:
        fields, _ = parse_frontmatter(unwrap_sealed(load_skill_text(existing)))
    except ValueError:
        return
    meta = fields.get("metadata") if isinstance(fields.get("metadata"), dict) else {}
    previous = meta.get("file")
    if previous and previous != agent_path.name:
        raise RuntimeError(f"{out} already holds the skill made from {previous}; {agent_path.name} would replace it. Rename one tool")


SOURCE_FILE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*_agent\.py")


def restored_file_name(fields: dict) -> str:
    """The file a compiled skill is written to: the file it came from, when the skill
    says and it is a plain *_agent.py name a server would load; else one from its name."""
    meta = fields.get("metadata") if isinstance(fields.get("metadata"), dict) else {}
    recorded = meta.get("file")
    if isinstance(recorded, str) and SOURCE_FILE_RE.fullmatch(recorded):
        return recorded
    return f"{snake(fields['name'])}_agent.py"


# ------------------------------------------------------------------------- compile


PARAMETERS_HEADING_RE = re.compile(r"^##[ \t]+(?:What it needs|Parameters)[ \t]*:?[ \t]*\r?$", re.MULTILINE | re.IGNORECASE)
NEXT_HEADING_RE = re.compile(r"^#{1,2}[ \t]", re.MULTILINE)
FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[ \t]*[^`\r\n]*\r?$", re.MULTILINE)


def _parameters_section(body: str) -> str | None:
    """The text under the 'What it needs' (or 'Parameters') heading, or None when there is no such heading.

    The heading may carry a trailing colon and CRLF line ends; the section runs to
    the next level-1 or level-2 heading, or the end of the file.
    """
    m = PARAMETERS_HEADING_RE.search(body)
    if not m:
        return None
    end = NEXT_HEADING_RE.search(body, m.end())
    return body[m.end():end.start() if end else len(body)]


def _first_fenced_block(section: str) -> str | None:
    """The inside of the first fenced code block in section (3+ backticks or tildes, any tag), or None."""
    m = FENCE_OPEN_RE.search(section)
    if not m:
        return None
    marker = m.group(1)
    close = re.compile(r"^[ \t]{0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*\r?$", re.MULTILINE)
    c = close.search(section, m.end())
    return section[m.end():c.start() if c else len(section)]


def _parameters_block(body: str) -> dict | None:
    """The JSON-schema object in the 'What it needs' section.

    Three outcomes, so a skill can never get a schema it did not write: the schema
    when the section holds a JSON object (in its first fenced block, or bare on a
    line of its own); None when there is no such section; ValueError when the
    section exists but holds nothing that parses as a JSON object.
    """
    section = _parameters_section(body)
    if section is None:
        return None
    fenced = _first_fenced_block(section)
    if fenced is not None:
        try:
            schema = json.loads(fenced)
        except json.JSONDecodeError as exc:
            raise ValueError(f"the 'What it needs' JSON block is not valid JSON ({exc})") from exc
    else:
        m = re.search(r"^[ \t]*\{", section, re.MULTILINE)
        if not m:
            raise ValueError("the 'What it needs' section has no JSON object in it (put the schema in a ```json block)")
        try:
            schema, _ = json.JSONDecoder().raw_decode(section, m.end() - 1)
        except json.JSONDecodeError as exc:
            raise ValueError(f"the 'What it needs' JSON object is not valid JSON ({exc})") from exc
    if not isinstance(schema, dict):
        raise ValueError(  # noqa: TRY004 - malformed document content
            f"the 'What it needs' block must be a JSON object, not {type(schema).__name__}"
        )
    return schema


def _skill_md(path: Path) -> tuple[Path, Path]:
    """Accept a skill directory or a SKILL.md path; return (skill_dir, SKILL.md)."""
    path = Path(path)
    return (path.parent, path) if path.is_file() else (path, path / "SKILL.md")


def compile_skill(skill_dir: Path, out_dir: Path) -> Path:
    """<skill>/ or SKILL.md -> out_dir/<snake>_agent.py."""
    skill_dir, md = _skill_md(skill_dir)
    text = unwrap_sealed(load_skill_text(md))
    fields, body = parse_frontmatter(text)
    name = fields["name"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = verify(md, launcher=False)
    if problems:
        raise RuntimeError("refusing to compile a skill that does not verify:\n  " + "\n  ".join(problems))
    script = skill_dir / "scripts" / "agent.py"
    agent_bytes = script.read_bytes() if script.is_file() else extract_agent(text)
    if agent_bytes is not None:
        target = out_dir / restored_file_name(fields)
        target.write_bytes(agent_bytes)
        return target

    parameters = _parameters_block(body)  # verify passed, so this is the schema or None
    if parameters is None:
        parameters = DEFAULT_PARAMETERS
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
            "parameters": json.loads({json.dumps(parameters, ensure_ascii=False)!r}),
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
    # Never ship a file that cannot load: try it the way a server would, first.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "agent.py"
        write_text(probe, source)
        try:
            load_agent(probe)
        except Exception as exc:
            raise RuntimeError(f"{md}: the generated agent does not load ({exc.__class__.__name__}: {exc}); {target.name} not written") from exc
    write_text(target, source)
    return target


# -------------------------------------------------------------------------- verify


def verify(skill_dir: Path, launcher: bool = True) -> list[str]:
    """Return problems (empty list = the skill is valid and self-consistent).

    launcher=False skips the check that the launcher is the current one: restoring
    the code a skill carries never depends on how old its launcher is.
    """
    skill_dir, md = _skill_md(skill_dir)
    problems: list[str] = []
    if not md.is_file():
        return [f"{skill_dir}: no SKILL.md"]
    try:
        text = unwrap_sealed(load_skill_text(md))
        fields, body = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{md}: {exc}"]
    problems.extend(_skill_lock_problems(skill_dir))
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
    if isinstance(meta, dict) and meta.get("locked"):
        if not re.search(r"<!-- locked -->\n```text\n.*?\n```\n<!-- /locked -->", body, re.DOTALL):
            problems.append(f"{md}: metadata says locked but no locked block is present")
        return problems
    params = None
    try:
        params = _parameters_block(body)
    except ValueError as exc:
        problems.append(f"{md}: {exc}")
    if params is not None and params.get("type") != "object":
        problems.append(f"{md}: the 'What it needs' schema must have type object")

    code_match = re.search(r"<!-- code sha256=([0-9a-f]{64}) -->\n(`{3,})python\n(.*?)\n\2\n<!-- /code -->", text, re.DOTALL)
    if code_match:
        expected, inner = code_match.group(1), code_match.group(3)
        if not any(sha256(c.encode("utf-8")) == expected for c in (inner + "\n", inner)):
            problems.append(f"{md}: embedded code does not match its sha256 {expected[:12]}")
        bundled = skill_dir / "scripts" / "rapp_skills.py"
        if bundled.is_file() and sha256(bundled.read_bytes()) != expected:
            problems.append(f"{bundled}: differs from the code embedded in SKILL.md (run sync)")
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
                agents = load_agents(probe)
            except Exception as exc:  # noqa: BLE001 - report any load failure
                problems.append(f"{md}: agent does not load ({exc.__class__.__name__}: {exc})")
                agents = []
        tool = (meta or {}).get("tool-name")
        agent = None
        if len(agents) == 1:
            agent = agents[0][1]
        elif agents:
            # Several agents in one file: this skill is the one its tool-name names.
            names = [_agent_name(a) for _, a in agents]
            if tool in names:
                agent = agents[names.index(tool)][1]
            else:
                problems.append(f"{md}: the code defines {len(agents)} agents ({', '.join(names)}); metadata.tool-name must name one of them (got {tool!r})")
        if agent is not None:
            if not callable(getattr(agent, "perform", None)):
                problems.append(f"{md}: agent has no perform()")
            if tool and _agent_name(agent) != tool:
                problems.append(f"{md}: agent metadata.name {agent.metadata.get('name')!r} != frontmatter tool-name {tool!r}")
            if params is not None:
                try:
                    code_params = _agent_parameters(agent)
                except (TypeError, ValueError) as exc:
                    problems.append(f"{md}: the code's parameters cannot be written as JSON ({exc})")
                else:
                    if code_params != params:
                        problems.append(f"{md}: the code's parameters differ from the 'What it needs' block")
        if script.is_file() and not (skill_dir / "scripts" / "run.py").is_file():
            problems.append(f"{skill_dir}: scripts/run.py missing (run to-skill again to regenerate)")
        if launcher:
            problems.extend(_launcher_problems(skill_dir, md, text))
    return problems


def _skill_lock_relative(raw: object) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw or ":" in raw:
        raise ValueError("path must be a non-empty relative POSIX path")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError("path must not be absolute or traverse")
    return Path(*pure.parts)


LOCK_ACTIVE_SUFFIXES = frozenset({
    ".bat", ".cmd", ".com", ".dll", ".dylib", ".egg", ".exe", ".fish",
    ".jar", ".node", ".php", ".phtml", ".pl", ".ps1", ".pth", ".py",
    ".pyc", ".pyd", ".pyo", ".pyw", ".rb", ".sh", ".so", ".wasm",
    ".whl", ".zip", ".zsh",
})
MAX_LOCK_TREE_ENTRIES = 10_000
RAPP_SKILL_LOCK_SCHEMA = "rapp-skill-lock/1"
HIVE_HUB_SKILL_LOCK_SCHEMA = "hive-hub-agent-lock/1"
HIVE_HUB_LOCK_MAX_FILE_BYTES = 8 * 1024 * 1024
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_WINDOWS_FILE_API: Any | None = None


class _ByHandleFileInformation(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", wintypes.FILETIME),
        ("ftLastAccessTime", wintypes.FILETIME),
        ("ftLastWriteTime", wintypes.FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]


def _is_windows() -> bool:
    return os.name == "nt"


def _windows_error(operation: str, path: str | None = None) -> OSError:
    get_last_error: Any = getattr(ctypes, "get_last_error", None)
    code = int(get_last_error()) if callable(get_last_error) else 0
    message = f"{operation} failed"
    if path is None:
        return OSError(code or errno.EIO, message)
    return OSError(code or errno.EIO, message, path)


def _windows_file_api() -> Any:
    global _WINDOWS_FILE_API
    if _WINDOWS_FILE_API is not None:
        return _WINDOWS_FILE_API
    loader: Any = getattr(ctypes, "WinDLL", None)
    if loader is None:
        raise OSError(errno.ENOSYS, "Windows file metadata is unavailable")
    api = loader("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    api.CreateFileW.restype = wintypes.HANDLE
    api.GetFileInformationByHandle.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ByHandleFileInformation),
    ]
    api.GetFileInformationByHandle.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    _WINDOWS_FILE_API = api
    return api


def _windows_file_metadata(path: Path) -> tuple[int, int]:
    absolute = os.path.abspath(os.fspath(path))
    api = _windows_file_api()
    handle = api.CreateFileW(
        absolute,
        0,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if handle is None or handle == _INVALID_HANDLE_VALUE:
        raise _windows_error("CreateFileW", absolute)
    information = _ByHandleFileInformation()
    try:
        if not api.GetFileInformationByHandle(handle, ctypes.byref(information)):
            raise _windows_error("GetFileInformationByHandle", absolute)
    except Exception:
        api.CloseHandle(handle)
        raise
    if not api.CloseHandle(handle):
        raise _windows_error("CloseHandle", absolute)
    return int(information.nNumberOfLinks), int(information.dwFileAttributes)


def _has_single_file_link(path: Path, information: os.stat_result) -> bool:
    if not _is_windows():
        return information.st_nlink == 1
    try:
        number_of_links, attributes = _windows_file_metadata(path)
    except OSError:
        return False
    return (
        number_of_links == 1
        and not attributes & FILE_ATTRIBUTE_REPARSE_POINT
    )


def _skill_lock_active(path: Path, mode: int) -> bool:
    return path.suffix.casefold() in LOCK_ACTIVE_SUFFIXES or bool(
        mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    )


def _skill_lock_tree(skill_dir: Path):
    stack: list[tuple[Path, Path]] = [(skill_dir, Path())]
    count = 0
    while stack:
        directory, relative_directory = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise ValueError(f"cannot inspect locked skill folder {directory}") from exc
        for entry in entries:
            count += 1
            if count > MAX_LOCK_TREE_ENTRIES:
                raise ValueError("locked skill folder contains too many entries")
            relative = relative_directory / entry.name
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ValueError(
                    f"cannot inspect locked skill path {relative.as_posix()}"
                ) from exc
            if stat.S_ISLNK(info.st_mode):
                yield relative, info, "symlink"
            elif stat.S_ISDIR(info.st_mode):
                stack.append((Path(entry.path), relative))
            elif stat.S_ISREG(info.st_mode):
                yield relative, info, "file"
            else:
                yield relative, info, "special"


def _skill_lock_inventory_problems(
    skill_dir: Path, listed: set[str]
) -> list[str]:
    problems: list[str] = []
    allowed = listed | {"agent.lock"}
    try:
        entries = _skill_lock_tree(skill_dir)
        for relative, info, kind in entries:
            name = relative.as_posix()
            if name in allowed:
                continue
            if kind == "symlink":
                problems.append(f"agent.lock does not allow unlisted symlink {name!r}")
            elif kind != "file":
                problems.append(
                    f"agent.lock does not allow unlisted special file {name!r}"
                )
            elif not _has_single_file_link(skill_dir / relative, info):
                problems.append(
                    f"agent.lock requires {name!r} to have exactly one filesystem link"
                )
            elif _skill_lock_active(relative, info.st_mode):
                problems.append(
                    "agent.lock does not list executable or importable file "
                    + repr(name)
                )
    except ValueError as exc:
        problems.append(str(exc))
    return problems


def _skill_lock_complete_inventory_problems(
    skill_dir: Path, listed: set[str]
) -> list[str]:
    problems: list[str] = []
    actual: set[str] = set()
    try:
        for relative, info, kind in _skill_lock_tree(skill_dir):
            name = relative.as_posix()
            if name == "agent.lock":
                continue
            if kind == "symlink":
                problems.append(f"agent.lock does not allow symlink {name!r}")
            elif kind != "file":
                problems.append(f"agent.lock does not allow special file {name!r}")
            else:
                actual.add(name)
                if not _has_single_file_link(skill_dir / relative, info):
                    problems.append(
                        f"agent.lock requires {name!r} to have exactly one filesystem link"
                    )
    except ValueError as exc:
        problems.append(str(exc))
        return problems
    for name in sorted(actual - listed):
        problems.append(f"agent.lock does not list file {name!r}")
    return problems


def _skill_lock_problems(skill_dir: Path) -> list[str]:
    lock_path = skill_dir / "agent.lock"
    if not lock_path.exists() and not lock_path.is_symlink():
        return []
    problems: list[str] = []
    if lock_path.is_symlink() or not lock_path.is_file():
        return [f"{lock_path}: must be a regular non-symlink file"]
    if not _has_single_file_link(lock_path, os.lstat(lock_path)):
        return [f"{lock_path}: must have exactly one filesystem link"]
    try:
        lock = json.loads(read_text(lock_path))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"{lock_path}: invalid JSON ({exc})"]
    if not isinstance(lock, dict):
        return [f"{lock_path}: must contain a JSON object"]
    schema = lock.get("schema")
    if schema not in {RAPP_SKILL_LOCK_SCHEMA, HIVE_HUB_SKILL_LOCK_SCHEMA}:
        problems.append(
            f"{lock_path}: schema must be {RAPP_SKILL_LOCK_SCHEMA} "
            f"or {HIVE_HUB_SKILL_LOCK_SCHEMA}"
        )
    source_owned = schema == HIVE_HUB_SKILL_LOCK_SCHEMA
    entry_fields = (
        {"path", "bytes", "sha256"}
        if source_owned
        else {"path", "sha256"}
    )
    if lock.get("name") != skill_dir.name:
        problems.append(f"{lock_path}: name must equal the skill directory name {skill_dir.name!r}")
    if not isinstance(lock.get("version"), str) or not lock["version"]:
        problems.append(f"{lock_path}: version must be a non-empty string")
    entries = lock.get("files")
    if not isinstance(entries, list) or not entries:
        problems.append(f"{lock_path}: files must be a non-empty array")
        return problems
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != entry_fields:
            names = ", ".join(sorted(entry_fields))
            problems.append(
                f"{lock_path}: files[{index}] must contain only {names}"
            )
            continue
        try:
            relative = _skill_lock_relative(entry["path"])
        except ValueError as exc:
            problems.append(f"{lock_path}: files[{index}].path {exc}")
            continue
        rel = relative.as_posix()
        if rel == "agent.lock":
            problems.append(f"{lock_path}: cannot hash itself")
            continue
        if rel in seen:
            problems.append(f"{lock_path}: duplicate locked path {rel!r}")
            continue
        seen.add(rel)
        expected = entry["sha256"]
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            problems.append(f"{lock_path}: files[{index}].sha256 must be a full lowercase SHA-256")
            continue
        expected_bytes = entry.get("bytes")
        if source_owned and (
            type(expected_bytes) is not int
            or not 0 <= expected_bytes <= HIVE_HUB_LOCK_MAX_FILE_BYTES
        ):
            problems.append(
                f"{lock_path}: files[{index}].bytes must be an integer from 0 "
                f"through {HIVE_HUB_LOCK_MAX_FILE_BYTES}"
            )
            continue
        target = skill_dir / relative
        current = skill_dir
        unsafe = skill_dir.is_symlink()
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                unsafe = True
                break
        if unsafe or not target.is_file():
            problems.append(f"{lock_path}: locked path {rel!r} must be a regular non-symlink file")
            continue
        if not _has_single_file_link(target, os.lstat(target)):
            problems.append(
                f"{lock_path}: locked path {rel!r} must have exactly one filesystem link"
            )
            continue
        data = target.read_bytes()
        if source_owned and len(data) != expected_bytes:
            problems.append(
                f"{lock_path}: locked path {rel!r} has {len(data)} bytes, "
                f"expected {expected_bytes}"
            )
        actual = sha256(data)
        if actual != expected:
            problems.append(f"{lock_path}: locked path {rel!r} has sha256 {actual}, expected {expected}")
    inventory = (
        _skill_lock_complete_inventory_problems(skill_dir, seen)
        if source_owned
        else _skill_lock_inventory_problems(skill_dir, seen)
    )
    problems.extend(f"{lock_path}: {problem}" for problem in inventory)
    return problems


def _launcher_problems(skill_dir: Path, md: Path, text: str) -> list[str]:
    """The launcher a skill carries must be the one this converter would write today.

    Every fix to the launcher reaches only skills converted since, so a skill keeps
    running whatever launcher it was born with unless something compares. This does:
    the block in SKILL.md against its own marker, and both the block and
    scripts/run.py against the current launcher.
    """
    problems: list[str] = []
    current = RUN_PY.lstrip("\n")
    block, claimed = extract_runner(text)
    if block is not None and claimed and sha256(block.encode("utf-8")) != claimed:
        problems.append(f"{md}: the launcher block does not match its sha256 {claimed[:12]}")
    stale = []
    if block is not None and block != current:
        stale.append("the launcher block in SKILL.md")
    run_py = skill_dir / "scripts" / "run.py"
    if run_py.is_file() and read_text(run_py) != current:
        stale.append("scripts/run.py")
    if stale:
        problems.append(f"{md}: {' and '.join(stale)} come from an older converter; run to-skill again to refresh them")
    return problems


# ---------------------------------------------------------------------------- lock

LOCK_ITERATIONS = 200000
LOCK_METHOD = f"aes-256-cbc pbkdf2 sha256 iterations={LOCK_ITERATIONS}"
LOCK_HINT = " (Locked by its owner: ask them for the passphrase.)"


def _openssl(args: list[str], data: bytes, passphrase: str) -> bytes:
    env = dict(os.environ, SKILL_PASSPHRASE=passphrase)
    proc = subprocess.run(["openssl", "enc", *args, "-aes-256-cbc", "-pbkdf2", "-iter", str(LOCK_ITERATIONS), "-md", "sha256", "-salt", "-pass", "env:SKILL_PASSPHRASE"],
                          input=data, capture_output=True, env=env, check=False)
    if proc.returncode != 0:
        raise RuntimeError("openssl failed: " + proc.stderr.decode("utf-8", "replace").strip()[:200])
    return proc.stdout


def lock_skill(skill_dir: Path, out_dir: Path, passphrase: str) -> Path:
    """Lock a skill: header stays readable, body is encrypted. Needs the openssl command."""
    import base64
    skill_dir, md = _skill_md(skill_dir)
    fields, body = parse_frontmatter(load_skill_text(md))
    if isinstance(fields.get("metadata"), dict) and fields["metadata"].get("locked"):
        raise RuntimeError(f"{md} is already locked")
    plain = body.encode("utf-8")
    b64 = base64.b64encode(_openssl(["-e"], plain, passphrase)).decode("ascii")
    lines = [b64[i:i + 76] for i in range(0, len(b64), 76)]
    meta = dict(fields.get("metadata") or {})
    meta["locked"] = LOCK_METHOD
    meta["locked-sha256"] = sha256(plain)
    fields = dict(fields)
    description = str(fields.get("description", "")).rstrip()
    # The hint is for people; metadata.locked is the real marker. Never let the hint
    # push a long description past the 1024-character limit a skill must respect.
    if len(description) + len(LOCK_HINT) <= 1024:
        description += LOCK_HINT
    fields["description"] = description
    fields["metadata"] = meta
    locked_body = "\n".join([
        "# Locked", "",
        "This file is locked by its owner. Everything it says is inside the block below, encrypted",
        "with a passphrase only they know. Ask them for it, then unlock:", "",
        "```bash", "SKILL_PASSPHRASE='...' python3 rapp_skills.py unlock SKILL.md --out unlocked", "```", "",
        "Or with openssl alone, saving the block below as `body.b64`:", "",
        "```bash", f"openssl enc -d -aes-256-cbc -pbkdf2 -iter {LOCK_ITERATIONS} -md sha256 -a -in body.b64 -out body.md", "```", "",
        "Never guess the passphrase, never try passphrases in bulk, and never keep an unlocked copy",
        "anywhere the owner did not ask for it. Without the passphrase, treat this file as empty.", "",
        "<!-- locked -->", "```text", *lines, "```", "<!-- /locked -->", "",
    ])
    out = Path(out_dir) / skill_dir.name
    out.mkdir(parents=True, exist_ok=True)
    write_text(out / "SKILL.md", dump_frontmatter(fields) + "\n" + locked_body)
    return out


def unlock_skill(skill_dir: Path, out_dir: Path, passphrase: str) -> Path:
    import base64
    skill_dir, md = _skill_md(skill_dir)
    fields, body = parse_frontmatter(load_skill_text(md))
    meta = fields.get("metadata") or {}
    if not meta.get("locked"):
        raise RuntimeError(f"{md} is not locked")
    m = re.search(r"<!-- locked -->\n```text\n(.*?)\n```\n<!-- /locked -->", body, re.DOTALL)
    if not m:
        raise RuntimeError(f"{md}: locked block not found")
    try:
        plain = _openssl(["-d"], base64.b64decode("".join(m.group(1).split())), passphrase)
    except RuntimeError as exc:
        raise RuntimeError("wrong passphrase, or the file was altered") from exc
    if sha256(plain) != meta.get("locked-sha256"):
        raise RuntimeError("wrong passphrase, or the file was altered")
    fields = dict(fields)
    fields["description"] = str(fields.get("description", "")).replace(LOCK_HINT, "")
    meta = dict(meta)
    meta.pop("locked", None)
    meta.pop("locked-sha256", None)
    fields["metadata"] = meta
    out = Path(out_dir) / skill_dir.name
    out.mkdir(parents=True, exist_ok=True)
    write_text(out / "SKILL.md", dump_frontmatter(fields) + plain.decode("utf-8"))
    return out


# ------------------------------------------------------------------------ roundtrip


def roundtrip(path: Path, tmp: Path) -> tuple[bool, str]:
    path = Path(path)
    tmp = Path(tmp)
    if path.is_dir() or path.name == "SKILL.md":
        if path.is_file():
            path = path.parent
        # A sealed skill is judged by the plain skill inside its seal, and the way back
        # must carry what to-skill was told the first time: origin, license, tool name.
        source = unwrap_sealed(load_skill_text(path / "SKILL.md"))
        fields, _ = parse_frontmatter(source)
        meta = fields.get("metadata") if isinstance(fields.get("metadata"), dict) else {}
        license_name = fields.get("license") if isinstance(fields.get("license"), str) else None
        compiled = compile_skill(path, tmp / "agents")
        toasted = toast(compiled, tmp / "skills", origin=meta.get("origin") or None,
                        license_name=license_name, tool_name=meta.get("tool-name"))
        a = source.encode("utf-8")
        b = (toasted / "SKILL.md").read_bytes()
        script = path / "scripts" / "agent.py"
        if script.is_file():
            same = script.read_bytes() == (toasted / "scripts" / "agent.py").read_bytes()
            return same, "the code came back unchanged" if same else "the code changed on the way back"
        return a == b, "SKILL.md came back byte-identical" if a == b else "SKILL.md changed on the way back"
    # A file with several agents becomes several skills; each must give the file back.
    same = all(path.read_bytes() == compile_skill(skill, tmp / "agents").read_bytes()
               for skill in toast_all(path, tmp / "skills"))
    return same, f"{path.name} came back byte-identical" if same else f"{path.name} changed on the way back"


# ------------------------------------------------------------------------ manifests


def _load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def _dump_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


SOURCE_MANIFEST_SCHEMA = "rapp-skill-source/1"
SOURCE_MANIFEST_FIELDS = {
    "schema",
    "name",
    "repository",
    "ref",
    "commit",
    "path",
    "git_tree",
    "folder_sha256",
    "files",
}
SOURCE_FILE_FIELDS = {
    "path",
    "mode",
    "bytes",
    "sha256",
    "git_blob",
}
GIT_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _git_object_sha1(kind: str, data: bytes) -> str:
    payload = f"{kind} {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(payload, usedforsecurity=False).hexdigest()


def _source_folder_sha256(entries: list[dict]) -> str:
    inventory = [
        {
            "path": entry["path"],
            "bytes": entry["bytes"],
            "sha256": entry["sha256"],
        }
        for entry in entries
    ]
    encoded = json.dumps(
        inventory,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded)


def _source_git_tree(entries: list[dict]) -> str:
    root: dict[str, object] = {}
    for entry in entries:
        relative = _skill_lock_relative(entry["path"])
        node = root
        for part in relative.parts[:-1]:
            child = node.get(part)
            if child is None:
                child = {}
                node[part] = child
            if not isinstance(child, dict):
                raise TypeError(f"source path collision at {relative.as_posix()!r}")
            node = child
        leaf = relative.parts[-1]
        if leaf in node:
            raise ValueError(f"duplicate source path {relative.as_posix()!r}")
        node[leaf] = ("file", entry)

    def tree_digest(node: dict[str, object]) -> str:
        records: list[tuple[bytes, bytes]] = []
        for name, value in node.items():
            name_bytes = name.encode("utf-8")
            if isinstance(value, dict):
                mode = b"40000"
                object_id = tree_digest(value)
                sort_name = name_bytes + b"/"
            else:
                _, entry = value
                mode = str(entry["mode"]).encode("ascii")
                object_id = str(entry["git_blob"])
                sort_name = name_bytes
            record = (
                mode
                + b" "
                + name_bytes
                + b"\0"
                + bytes.fromhex(object_id)
            )
            records.append((sort_name, record))
        return _git_object_sha1(
            "tree",
            b"".join(record for _, record in sorted(records)),
        )

    return tree_digest(root)


def _source_manifest_problems(root: Path, manifest_path: Path) -> list[str]:
    root = Path(root)
    manifest_path = Path(manifest_path)
    problems: list[str] = []
    if manifest_path.is_symlink() or not manifest_path.is_file():
        return [f"{manifest_path}: must be a regular non-symlink file"]
    if not _has_single_file_link(manifest_path, os.lstat(manifest_path)):
        return [f"{manifest_path}: must have exactly one filesystem link"]
    try:
        source = _load_json(manifest_path)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"{manifest_path}: invalid JSON ({exc})"]
    if not isinstance(source, dict):
        return [f"{manifest_path}: must contain a JSON object"]
    if set(source) != SOURCE_MANIFEST_FIELDS:
        problems.append(
            f"{manifest_path}: fields must be exactly "
            + ", ".join(sorted(SOURCE_MANIFEST_FIELDS))
        )
        return problems
    if source["schema"] != SOURCE_MANIFEST_SCHEMA:
        problems.append(
            f"{manifest_path}: schema must be {SOURCE_MANIFEST_SCHEMA}"
        )
    name = source["name"]
    if (
        not isinstance(name, str)
        or NAME_RE.fullmatch(name) is None
        or name != manifest_path.stem
    ):
        problems.append(
            f"{manifest_path}: name must match its lowercase hyphenated file name"
        )
    repository = source["repository"]
    if (
        not isinstance(repository, str)
        or re.fullmatch(
            r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
            repository,
        )
        is None
    ):
        problems.append(
            f"{manifest_path}: repository must be a canonical GitHub HTTPS URL"
        )
    ref = source["ref"]
    if not isinstance(ref, str) or not ref.startswith("refs/") or any(
        character.isspace() for character in ref
    ):
        problems.append(f"{manifest_path}: ref must be a full Git ref")
    for field in ("commit", "git_tree"):
        if not isinstance(source[field], str) or GIT_SHA1_RE.fullmatch(source[field]) is None:
            problems.append(
                f"{manifest_path}: {field} must be a full lowercase Git SHA-1"
            )
    if (
        not isinstance(source["folder_sha256"], str)
        or SHA256_RE.fullmatch(source["folder_sha256"]) is None
    ):
        problems.append(
            f"{manifest_path}: folder_sha256 must be a full lowercase SHA-256"
        )
    try:
        relative_root = _skill_lock_relative(source["path"])
    except ValueError as exc:
        problems.append(f"{manifest_path}: path {exc}")
        return problems
    expected_root = f"skills/{name}" if isinstance(name, str) else None
    if relative_root.as_posix() != expected_root:
        problems.append(
            f"{manifest_path}: path must be {expected_root!r}"
        )
    skill_dir = root / relative_root
    if skill_dir.is_symlink() or not skill_dir.is_dir():
        problems.append(
            f"{manifest_path}: pinned skill path must be a regular directory"
        )
        return problems

    files = source["files"]
    if not isinstance(files, list) or not files:
        problems.append(f"{manifest_path}: files must be a non-empty array")
        return problems
    valid_entries: list[dict] = []
    listed: set[str] = set()
    listed_order: list[str] = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or set(entry) != SOURCE_FILE_FIELDS:
            problems.append(
                f"{manifest_path}: files[{index}] fields must be exactly "
                + ", ".join(sorted(SOURCE_FILE_FIELDS))
            )
            continue
        try:
            relative = _skill_lock_relative(entry["path"])
        except ValueError as exc:
            problems.append(f"{manifest_path}: files[{index}].path {exc}")
            continue
        rel = relative.as_posix()
        listed_order.append(rel)
        if rel in listed:
            problems.append(
                f"{manifest_path}: duplicate source path {rel!r}"
            )
            continue
        listed.add(rel)
        mode = entry["mode"]
        size = entry["bytes"]
        checksum = entry["sha256"]
        blob = entry["git_blob"]
        shape_valid = True
        if mode not in {"100644", "100755"}:
            problems.append(
                f"{manifest_path}: files[{index}].mode must be 100644 or 100755"
            )
            shape_valid = False
        if type(size) is not int or size < 0:
            problems.append(
                f"{manifest_path}: files[{index}].bytes must be a non-negative integer"
            )
            shape_valid = False
        if not isinstance(checksum, str) or SHA256_RE.fullmatch(checksum) is None:
            problems.append(
                f"{manifest_path}: files[{index}].sha256 must be a full lowercase SHA-256"
            )
            shape_valid = False
        if not isinstance(blob, str) or GIT_SHA1_RE.fullmatch(blob) is None:
            problems.append(
                f"{manifest_path}: files[{index}].git_blob must be a full lowercase Git SHA-1"
            )
            shape_valid = False
        if not shape_valid:
            continue
        valid_entries.append(entry)
        target = skill_dir / relative
        current = skill_dir
        unsafe = False
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                unsafe = True
                break
        if unsafe or not target.is_file():
            problems.append(
                f"{manifest_path}: source path {rel!r} must be a regular non-symlink file"
            )
            continue
        info = os.lstat(target)
        if not _has_single_file_link(target, info):
            problems.append(
                f"{manifest_path}: source path {rel!r} must have exactly one filesystem link"
            )
        actual_mode = (
            "100755"
            if info.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            else "100644"
        )
        if actual_mode != mode:
            problems.append(
                f"{manifest_path}: source path {rel!r} has mode {actual_mode}, expected {mode}"
            )
        data = target.read_bytes()
        if len(data) != size:
            problems.append(
                f"{manifest_path}: source path {rel!r} has {len(data)} bytes, expected {size}"
            )
        actual_sha256 = sha256(data)
        if actual_sha256 != checksum:
            problems.append(
                f"{manifest_path}: source path {rel!r} has sha256 {actual_sha256}, expected {checksum}"
            )
        actual_blob = _git_object_sha1("blob", data)
        if actual_blob != blob:
            problems.append(
                f"{manifest_path}: source path {rel!r} has Git blob {actual_blob}, expected {blob}"
            )
    if listed_order != sorted(listed_order):
        problems.append(f"{manifest_path}: files must be sorted by path")
    actual_files: set[str] = set()
    try:
        for relative, info, kind in _skill_lock_tree(skill_dir):
            rel = relative.as_posix()
            if kind == "symlink":
                problems.append(
                    f"{manifest_path}: source inventory contains symlink {rel!r}"
                )
            elif kind != "file":
                problems.append(
                    f"{manifest_path}: source inventory contains special file {rel!r}"
                )
            else:
                actual_files.add(rel)
                if not _has_single_file_link(skill_dir / relative, info):
                    problems.append(
                        f"{manifest_path}: source path {rel!r} must have exactly "
                        "one filesystem link"
                    )
    except ValueError as exc:
        problems.append(f"{manifest_path}: {exc}")
    for missing in sorted(actual_files - listed):
        problems.append(
            f"{manifest_path}: source inventory does not list {missing!r}"
        )
    for absent in sorted(listed - actual_files):
        problems.append(
            f"{manifest_path}: source inventory lists missing or unsafe file {absent!r}"
        )
    if len(valid_entries) == len(files):
        folder_sha256 = _source_folder_sha256(valid_entries)
        if folder_sha256 != source["folder_sha256"]:
            problems.append(
                f"{manifest_path}: folder_sha256 is {folder_sha256}, "
                f"expected {source['folder_sha256']}"
            )
        try:
            git_tree = _source_git_tree(valid_entries)
        except (TypeError, ValueError) as exc:
            problems.append(f"{manifest_path}: {exc}")
        else:
            if git_tree != source["git_tree"]:
                problems.append(
                    f"{manifest_path}: Git tree is {git_tree}, expected {source['git_tree']}"
                )
    return problems


def _render_skill_lock(lock_path: Path) -> str:
    if lock_path.is_symlink() or not lock_path.is_file():
        raise ValueError(f"{lock_path}: must be a regular non-symlink file")
    if not _has_single_file_link(lock_path, os.lstat(lock_path)):
        raise ValueError(f"{lock_path}: must have exactly one filesystem link")
    lock = _load_json(lock_path)
    schema = lock.get("schema")
    if schema == HIVE_HUB_SKILL_LOCK_SCHEMA:
        problems = _skill_lock_problems(lock_path.parent)
        if problems:
            raise ValueError(problems[0])
        return read_text(lock_path)
    if schema != RAPP_SKILL_LOCK_SCHEMA:
        raise ValueError(
            f"{lock_path}: schema must be {RAPP_SKILL_LOCK_SCHEMA} "
            f"or {HIVE_HUB_SKILL_LOCK_SCHEMA}"
        )
    entries = lock.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{lock_path}: files must be a non-empty array")
    skill_dir = lock_path.parent
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ValueError(f"{lock_path}: files[{index}] must contain only path and sha256")
        relative = _skill_lock_relative(entry["path"])
        rel = relative.as_posix()
        if rel == "agent.lock" or rel in seen:
            raise ValueError(f"{lock_path}: unsafe or duplicate locked path {rel!r}")
        seen.add(rel)
        target = skill_dir / relative
        current = skill_dir
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f"{lock_path}: locked path {rel!r} contains a symlink")
        if not target.is_file():
            raise ValueError(f"{lock_path}: locked path {rel!r} is not a regular file")
        if not _has_single_file_link(target, os.lstat(target)):
            raise ValueError(
                f"{lock_path}: locked path {rel!r} must have exactly one filesystem link"
            )
        entry["sha256"] = sha256(target.read_bytes())
    inventory_problems = _skill_lock_inventory_problems(skill_dir, seen)
    if inventory_problems:
        raise ValueError(f"{lock_path}: {inventory_problems[0]}")
    return _dump_json(lock)


def render_manifests(root: Path) -> dict[str, str]:
    """Every generated file as {relative path: content}, from the sources of truth."""
    root = Path(root)
    for source_path in sorted((root / "sources").glob("*.json")):
        problems = _source_manifest_problems(root, source_path)
        if problems:
            raise ValueError(problems[0])
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

    for lock_path in sorted((root / "skills").glob("*/agent.lock")):
        rendered = _render_skill_lock(lock_path)
        if _load_json(lock_path).get("schema") == HIVE_HUB_SKILL_LOCK_SCHEMA:
            continue
        files[lock_path.relative_to(root).as_posix()] = rendered

    hosts_md = ["# Hosts", "", "Each AI tool this works in is one JSON file in `hosts/`. Supporting a new tool is adding a file.", "",
                "| Host | Verified version | Verified on | Skills read from | Plugin manifest | Marketplace | Agents |", "|---|---|---|---|---|---|---|"]
    for host in hosts.values():
        v = host.get("verified", {})
        hosts_md.append(
            f"| {host['display']} | {v.get('version', '-')} | {v.get('date', '-')} | "
            + ", ".join(f"`{d}`" for d in host["skill_dirs"]) + f" | `{host['plugin_manifest']}` | `{host['marketplace']}` | "
            + f"`{host['agents']['dir']}/*{host['agents']['suffix']}` |"
        )
    hosts_md += ["", "## Install", ""]
    for host in hosts.values():
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

    # The converter skill carries its own code, so one file gives an AI the capability.
    meta_md = root / "skills" / "rapp-skills" / "SKILL.md"
    script = root / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py"
    if meta_md.is_file() and script.is_file():
        text = read_text(meta_md)
        head = text.split("\n<!-- code sha256=")[0].rstrip("\n")
        code = read_text(script)
        block = embed_block(code, f"<!-- code sha256={sha256(code.encode('utf-8'))} -->", "<!-- /code -->")
        files["skills/rapp-skills/SKILL.md"] = head + "\n\n" + block + "\n"
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
    p = sub.add_parser("to-skill", help="agent.py (or a folder of them) -> skills anyone can use")
    p.add_argument("agent", help="one *_agent.py, or a folder such as a Brainstem's agents/ to back up every agent")
    p.add_argument("--out", default="skills", help="skills directory (default: skills)")
    p.add_argument("--origin", default=None, help="URL of the agent's source, recorded in metadata")
    p.add_argument("--license", default=None)
    p = sub.add_parser("to-agent", help="skill (or a folder of skills) -> Python files a Brainstem loads as its own")
    p.add_argument("skill", help="one skill folder or SKILL.md, or a folder of skills to restore all of them")
    p.add_argument("--out", default="agents")
    p = sub.add_parser("check", help="find problems in one or more skills")
    p.add_argument("skills", nargs="+")
    p = sub.add_parser("prove", help="show nothing is lost going there and back")
    p.add_argument("path")
    p = sub.add_parser("run", help="run a skill's agent locally")
    p.add_argument("skill")
    p.add_argument("--json", default="{}")
    p.add_argument("--tool", default=None, help="which agent to run when the skill's code defines several")
    p = sub.add_parser("lock", help="lock a skill with a passphrase (header stays readable, body encrypted)")
    p.add_argument("skill")
    p.add_argument("--out", default="locked")
    p = sub.add_parser("unlock", help="unlock a locked skill with its passphrase")
    p.add_argument("skill")
    p.add_argument("--out", default="unlocked")
    p = sub.add_parser("sync", help="rewrite (or --check) every host-specific file from the sources of truth")
    p.add_argument("--root", default=".")
    p.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.cmd == "to-skill":
        source = Path(args.agent)
        agents = sorted(source.glob("*_agent.py")) if source.is_dir() else [source]
        if source.is_dir():
            agents = [a for a in agents if a.name != "basic_agent.py"]
        rc = 0
        seen: dict[str, Path] = {}
        for agent in agents:
            try:
                outs = toast_all(agent, Path(args.out), origin=args.origin, license_name=args.license, seen=seen)
            except Exception as exc:  # noqa: BLE001 - keep processing other agents
                print(f"skipped {agent.name}: {exc.__class__.__name__}: {exc}")
                rc = 1
                continue
            for out in outs:
                problems = verify(out)
                print(f"skill written: {out}")
                if problems:
                    print("\n".join("  " + p for p in problems))
                    rc = 1
        return rc
    if args.cmd == "to-agent":
        source = Path(args.skill)
        skills = sorted(d for d in source.iterdir() if (d / "SKILL.md").is_file()) if source.is_dir() and not (source / "SKILL.md").is_file() else [source]
        rc = 0
        written: dict[str, Path] = {}
        for skill in skills:
            try:
                target = compile_skill(skill, Path(args.out))
            except Exception as exc:  # noqa: BLE001 - keep processing other skills
                print(f"skipped {skill}: {exc.__class__.__name__}: {exc}")
                rc = 1
                continue
            digest = sha256(target.read_bytes())
            if digest in written:
                # Several skills came from one file of several tools; a server loading the
                # folder would register every tool once per copy. Keep the first copy only.
                if written[digest] != target:
                    target.unlink()
                print(f"{skill.name}: same code as {written[digest].name}; not written again")
                continue
            written[digest] = target
            print(target)
        return rc
    if args.cmd == "check":
        rc = 0
        for s in args.skills:
            problems = verify(Path(s))
            print(f"{'ok  ' if not problems else 'FAIL'} {s}")
            for line in problems:
                print("     " + line)
            rc |= 1 if problems else 0
        return rc
    if args.cmd == "prove":
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ok, msg = roundtrip(Path(args.path), Path(tmp))
        print(("PASS " if ok else "FAIL ") + msg)
        return 0 if ok else 1
    if args.cmd == "run":
        runner = Path(args.skill) / "scripts" / "run.py"
        if not runner.is_file():
            print("this skill has no code to run; the AI hosting it carries out its steps", file=sys.stderr)
            return 2
        return subprocess.call([sys.executable, str(runner), "--json", args.json, *(["--tool", args.tool] if args.tool else [])])
    if args.cmd in ("lock", "unlock"):
        passphrase = os.environ.get("SKILL_PASSPHRASE")
        if not passphrase:
            import getpass
            passphrase = getpass.getpass("Passphrase: ")
        fn = lock_skill if args.cmd == "lock" else unlock_skill
        print(fn(Path(args.skill), Path(args.out), passphrase))
        return 0
    if args.cmd == "sync":
        drift = manifests(Path(args.root), check=args.check)
        if args.check:
            if drift:
                print("generated files are out of date (run `rapp_skills.py sync`):\n  " + "\n  ".join(drift))
                return 1
            print("generated files are current")
        else:
            print("generated files written")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
