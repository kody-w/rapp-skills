"""rapp-skills: the conversion is lossless, the skills are standard, the hosts do not drift."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
# RAPP_SKILLS_UNDER_TEST points these tests at another copy of the converter (for
# example one extracted from an older commit) to show a test really catches a bug.
CONVERTER = Path(os.environ.get("RAPP_SKILLS_UNDER_TEST") or ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py").resolve()
_spec = importlib.util.spec_from_file_location("rapp_skills", CONVERTER)
rs = importlib.util.module_from_spec(_spec)
sys.modules["rapp_skills"] = rs
_spec.loader.exec_module(rs)

FIXTURES = ROOT / "tests" / "fixtures"
HELLO = FIXTURES / "hello_world_agent.py"
PAIR = FIXTURES / "pair_agent.py"
BRIEF = FIXTURES / "writing-brief"


def run_py(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)


class ToastAndCompile(unittest.TestCase):
    def test_agent_roundtrips_byte_identically(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, msg = rs.roundtrip(HELLO, Path(tmp))
        self.assertTrue(ok, msg)

    def test_toasted_skill_is_standard_and_self_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = rs.toast(HELLO, Path(tmp) / "skills", origin="https://example.invalid/hello", license_name="MIT")
            self.assertEqual(out.name, "hello-world")
            self.assertEqual(rs.verify(out), [])
            fields, body = rs.parse_frontmatter(rs.read_text(out / "SKILL.md"))
            self.assertEqual(set(fields), {"name", "description", "license", "compatibility", "metadata"})
            self.assertEqual(fields["metadata"]["tool-name"], "HelloWorldAgent")
            self.assertEqual(fields["metadata"]["agent-sha256"], rs.sha256(HELLO.read_bytes()))
            self.assertEqual((out / "scripts" / "agent.py").read_bytes(), HELLO.read_bytes())
            self.assertEqual(rs.extract_agent(rs.read_text(out / "SKILL.md")), HELLO.read_bytes())

    def test_toasted_skill_runs_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = rs.toast(HELLO, Path(tmp) / "skills")
            result = run_py("scripts/run.py", "--json", '{"name": "Ada"}', cwd=out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "Hello, Ada! Welcome to the RAPP Agent ecosystem.")
            describe = run_py("scripts/run.py", "--describe", cwd=out)
            self.assertEqual(json.loads(describe.stdout)["function"]["name"], "HelloWorldAgent")

    def test_lone_skill_md_is_all_a_user_needs(self):
        """Drop one SKILL.md with no scripts/: it verifies, compiles, and the host can run it."""
        with tempfile.TemporaryDirectory() as tmp:
            src = rs.toast(HELLO, Path(tmp) / "skills")
            drop = Path(tmp) / "drop" / "hello-world"
            drop.mkdir(parents=True)
            (drop / "SKILL.md").write_bytes((src / "SKILL.md").read_bytes())
            self.assertEqual(rs.verify(drop / "SKILL.md"), [])
            compiled = rs.compile_skill(drop / "SKILL.md", Path(tmp) / "agents")
            self.assertEqual(compiled.read_bytes(), HELLO.read_bytes())
            text = rs.read_text(drop / "SKILL.md")
            runner, claimed = rs.extract_runner(text)
            self.assertEqual(rs.sha256(runner.encode("utf-8")), claimed)
            (drop / "agent.py").write_bytes(rs.extract_agent(text))
            rs.write_text(drop / "run.py", runner)
            result = run_py("run.py", "--json", '{"name": "Grace"}', cwd=drop)
            self.assertEqual(result.stdout.strip(), "Hello, Grace! Welcome to the RAPP Agent ecosystem.", result.stderr)

    def test_handwritten_skill_compiles_to_playbook_and_roundtrips(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rs.verify(BRIEF), [])
            compiled = rs.compile_skill(BRIEF, Path(tmp) / "agents")
            self.assertEqual(compiled.name, "writing_brief_agent.py")
            _, agent = rs.load_agent(compiled)
            self.assertEqual(agent.metadata["name"], "writing_brief")
            self.assertEqual(agent.metadata["parameters"]["required"], ["topic"])
            out = agent.perform(topic="why skills beat plugins", audience="developers")
            self.assertIn("Write a five-part outline", out)
            self.assertIn('"topic": "why skills beat plugins"', out)
            ok, msg = rs.roundtrip(BRIEF, Path(tmp) / "rt")
            self.assertTrue(ok, msg)

    def test_verify_catches_the_important_mistakes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = rs.toast(HELLO, Path(tmp) / "skills")
            md = out / "SKILL.md"
            good = rs.read_text(md)
            rs.write_text(md, good.replace('name: "hello-world"', 'name: "Hello World"'))
            self.assertTrue(any("name must be" in p for p in rs.verify(out)))
            rs.write_text(md, good.replace("Hello, {name}!", "Hello, {name}?"))
            self.assertTrue(any("sha256" in p for p in rs.verify(out)))
            rs.write_text(md, good.replace('description: ', 'model: "opus"\ndescription: ', 1))
            self.assertTrue(any("non-standard frontmatter" in p for p in rs.verify(out)))
            (out / "scripts" / "agent.py").write_bytes(b"print('tampered')\n")
            rs.write_text(md, good)
            self.assertTrue(any("differs from the agent embedded" in p for p in rs.verify(out)))


    def test_toasted_skill_mentions_no_second_world(self):
        """What a host is fed is a plain skill: no product names, no scaling pitch."""
        with tempfile.TemporaryDirectory() as tmp:
            out = rs.toast(HELLO, Path(tmp) / "skills")
            text = rs.read_text(out / "SKILL.md")
            head = text.split("<!-- agent sha256=")[0].lower()
            for word in ("rapp", "brainstem", "scale this skill", "toast", "compile", "frontmatter", "round-trip", "playbook"):
                self.assertNotIn(word, head)


    def test_sealed_skill_unwraps_and_bad_seal_is_refused(self):
        raw = rs.read_text(BRIEF / "SKILL.md")
        good = rs.sha256(raw.encode("utf-8"))
        sealed = "---\nname: writing-brief\ndescription: sealed\nschema: rapp/1-skill\nskill_hash: " + good + "\nnote: |\n  folded\n---\n<!-- RAW-SKILL-BEGIN sha256=" + good + " -->\n" + raw.rstrip("\n") + "\n<!-- RAW-SKILL-END -->\n"
        self.assertEqual(rs.unwrap_sealed(sealed), raw)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "writing-brief"; d.mkdir()
            rs.write_text(d / "SKILL.md", sealed)
            self.assertEqual(rs.verify(d), [])
            compiled = rs.compile_skill(d, Path(tmp) / "agents")
            self.assertEqual(compiled.name, "writing_brief_agent.py")
            rs.write_text(d / "SKILL.md", sealed.replace("Turn a rough idea", "Turn a polished idea"))
            self.assertTrue(any("seal does not match" in p for p in rs.verify(d)))


class ReviewDefects(unittest.TestCase):
    """One test per confirmed defect. Each fails on the converter before its fix."""

    def test_defect1_compiled_schema_with_json_literals_imports(self):
        """A step-by-step skill whose inputs use true/false/null must compile to a file that loads.

        The schema used to be pasted into the Python file as JSON text, so `true`,
        `false` and `null` were NameErrors, and nothing noticed because the compiled
        file was never loaded. Now the schema travels as a JSON string and the
        compiled file is loaded before it is written; if it cannot load, compile
        refuses instead of shipping a broken file.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "What to write about (¡en cualquier idioma!)"},
                "draft": {"type": "boolean", "default": False},
                "limit": {"type": ["integer", "null"], "default": None},
                "public": {"type": "boolean", "default": True},
            },
            "required": ["topic"],
            "additionalProperties": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "every-literal"
            skill.mkdir()
            rs.write_text(skill / "SKILL.md", "---\nname: \"every-literal\"\ndescription: \"Uses every JSON literal in its inputs.\"\n---\n\n"
                          "# Every Literal\n\n## What it needs\n\n```json\n" + json.dumps(schema, indent=2, ensure_ascii=False) + "\n```\n\nWrite about the topic.\n")
            self.assertEqual(rs.verify(skill), [])
            compiled = rs.compile_skill(skill, Path(tmp) / "agents")
            _, agent = rs.load_agent(compiled)
            self.assertEqual(agent.metadata["parameters"], schema)
            self.assertIn("¡en cualquier idioma!", agent.perform(topic="skills"))
            # A skill whose name starts with a digit still compiles to a class Python accepts.
            bad = Path(tmp) / "3d-print"
            bad.mkdir()
            rs.write_text(bad / "SKILL.md", "---\nname: \"3d-print\"\ndescription: \"A name that is not a Python class name.\"\n---\n\n# 3d Print\n\nPrint it.\n")
            self.assertEqual(rs.verify(bad), [])
            digit = rs.compile_skill(bad, Path(tmp) / "agents")
            self.assertEqual(digit.name, "3d_print_agent.py")
            _, digit_agent = rs.load_agent(digit)
            self.assertEqual(type(digit_agent).__name__, "Skill3dPrintAgent")
            self.assertEqual(digit_agent.metadata["name"], "3d_print")

    def test_defect2_file_with_several_agents_yields_one_skill_each(self):
        """A file defining several agents is several tools on a server, so it is several skills.

        The loader used to keep only the last class in the file, silently, so
        to-skill wrote one skill for the wrong agent and check compared against the
        wrong class. Now every public agent is found in definition order, each gets
        its own skill naming its own tool, check and the launcher pick by tool name,
        and the launcher refuses to guess when the name is missing.
        """
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rs.main(["to-skill", str(PAIR), "--out", str(skills)]), 0)
            self.assertEqual(sorted(p.name for p in skills.iterdir()), ["farewell", "greet"])
            for name, tool in (("greet", "GreetAgent"), ("farewell", "FarewellAgent")):
                skill = skills / name
                self.assertEqual(rs.verify(skill), [])
                fields, body = rs.parse_frontmatter(rs.read_text(skill / "SKILL.md"))
                self.assertEqual(fields["metadata"]["tool-name"], tool)
                self.assertIn(f"--tool {tool} ", body, "the run instructions must say which tool")
                self.assertEqual((skill / "scripts" / "agent.py").read_bytes(), PAIR.read_bytes())
            # The launcher runs the tool asked for, and refuses to guess between the two.
            out = skills / "greet"
            result = run_py("scripts/run.py", "--tool", "FarewellAgent", "--json", '{"name": "Ada", "until": "Monday"}', cwd=out)
            self.assertEqual(result.stdout.strip(), "Goodbye, Ada! See you Monday.", result.stderr)
            result = run_py("scripts/run.py", "--tool", "GreetAgent", "--json", '{"name": "Ada"}', cwd=out)
            self.assertEqual(result.stdout.strip(), "Hello, Ada!", result.stderr)
            result = run_py("scripts/run.py", "--json", '{"name": "Ada"}', cwd=out)
            self.assertNotEqual(result.returncode, 0, "two agents and no --tool must not silently pick one")
            self.assertIn("GreetAgent", result.stderr)
            self.assertIn("FarewellAgent", result.stderr)
            self.assertIn("--tool", result.stderr)
            # The loader: every public agent, in the order the file defines them; the
            # underscore-named one is left out, exactly as a server would leave it out.
            self.assertEqual([attr for attr, _ in rs.load_agents(PAIR)], ["GreetAgent", "FarewellAgent"])
            with self.assertRaises(RuntimeError) as caught:
                rs.load_agent(PAIR)
            self.assertIn("GreetAgent", str(caught.exception))
            self.assertIn("FarewellAgent", str(caught.exception))
            _, agent = rs.load_agent(PAIR, "FarewellAgent")
            self.assertEqual(agent.metadata["name"], "FarewellAgent")
            _, agent = rs.load_agent(HELLO)
            self.assertEqual(agent.metadata["name"], "HelloWorldAgent", "one agent needs no tool name")
            # check compares against the class the skill names, not the last one in the file.
            md = skills / "greet" / "SKILL.md"
            good = rs.read_text(md)
            rs.write_text(md, good.replace('tool-name: "GreetAgent"', 'tool-name: "FarewellAgent"'))
            self.assertTrue(any("parameters differ" in p for p in rs.verify(skills / "greet")))
            rs.write_text(md, good.replace('tool-name: "GreetAgent"', 'tool-name: "NoSuchAgent"'))
            self.assertTrue(any("must name one of them" in p for p in rs.verify(skills / "greet")))
            rs.write_text(md, good)
            ok, msg = rs.roundtrip(PAIR, Path(tmp) / "rt")
            self.assertTrue(ok, msg)

    @unittest.skipUnless(shutil.which("openssl"), "locking needs the openssl command")
    def test_defect3_lock_keeps_long_description_within_limit(self):
        """Locking a skill with a long description must still produce a valid skill.

        lock used to append its 52-character hint to the description no matter what,
        so a description near the 1024-character limit (including the 1000-plus-dots
        one to-skill itself writes) came out too long and the locked file failed
        check. Now the hint is added only when it fits; metadata.locked already says
        the file is locked.
        """
        long_description = ("Greets the user at considerable length, explaining the history of greetings. " * 20).strip()
        source = HELLO.read_text(encoding="utf-8").replace('"description": "Says hello to the user."', '"description": ' + json.dumps(long_description))
        self.assertNotEqual(source, HELLO.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            agent = Path(tmp) / "long_hello_agent.py"
            rs.write_text(agent, source)
            skill = rs.toast(agent, Path(tmp) / "skills")
            fields, _ = rs.parse_frontmatter(rs.read_text(skill / "SKILL.md"))
            self.assertTrue(973 <= len(fields["description"]) <= 1024, len(fields["description"]))
            self.assertEqual(rs.verify(skill), [])
            locked = rs.lock_skill(skill, Path(tmp) / "locked", "open sesame")
            self.assertEqual(rs.verify(locked), [], "a locked skill must still be a valid skill")
            locked_fields, _ = rs.parse_frontmatter(rs.read_text(locked / "SKILL.md"))
            self.assertLessEqual(len(locked_fields["description"]), 1024)
            self.assertTrue(locked_fields["metadata"]["locked"])
            unlocked = rs.unlock_skill(locked, Path(tmp) / "unlocked", "open sesame")
            self.assertEqual((unlocked / "SKILL.md").read_bytes(), (skill / "SKILL.md").read_bytes())
            # A short description still gets the hint for people reading the header.
            short = rs.toast(HELLO, Path(tmp) / "skills-short")
            short_locked = rs.lock_skill(short, Path(tmp) / "locked-short", "open sesame")
            short_fields, _ = rs.parse_frontmatter(rs.read_text(short_locked / "SKILL.md"))
            self.assertIn("Locked by its owner", short_fields["description"])
            self.assertEqual(rs.verify(short_locked), [])


AGENT_TEMPLATE = '''from agents.basic_agent import BasicAgent


class {cls}(BasicAgent):
    def __init__(self):
        self.name = "{cls}"
        self.metadata = {metadata}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return "ok " + str(kwargs.get("name", ""))
'''


def sealed_copy(text: str, name: str) -> str:
    """Wrap a plain skill the way a sealed one arrives: outer header, RAW-SKILL markers, sha256."""
    digest = rs.sha256(text.encode("utf-8"))
    return ("---\nname: " + name + "\ndescription: sealed\nschema: rapp/1-skill\nskill_hash: " + digest + "\n---\n"
            "<!-- RAW-SKILL-BEGIN sha256=" + digest + " -->\n" + text.rstrip("\n") + "\n<!-- RAW-SKILL-END -->\n")


class ConverterReview2(unittest.TestCase):
    """Second review round: one test per confirmed defect. Each fails on the converter before its fix."""

    def test_defectA_agent_without_usable_parameters_converts_checks_and_restores(self):
        """An agent whose metadata has no usable parameters is still a valid skill.

        to-skill wrote a default empty schema into the 'What it needs' block, but
        check compared that block against the raw metadata (missing, {}, or with
        tuples in it), so every such skill failed check and to-agent refused to
        restore it. Now one normalisation serves both sides.
        """
        empty = {"type": "object", "properties": {}, "required": []}
        variants = {
            "missing": ('{"name": self.name, "description": "No parameters at all."}', empty),
            "empty": ('{"name": self.name, "description": "Empty parameters.", "parameters": {}}', empty),
            "tuple": ('{"name": self.name, "description": "A tuple where JSON has a list.", '
                      '"parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ("name",)}}',
                      {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
        }
        for variant, (metadata, expected) in variants.items():
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                cls = variant.capitalize() + "ParamsAgent"
                agent = tmp / f"{variant}_params_agent.py"
                rs.write_text(agent, AGENT_TEMPLATE.format(cls=cls, metadata=metadata))
                skill = rs.toast(agent, tmp / "skills")
                self.assertEqual(skill.name, f"{variant}-params")
                _, body = rs.parse_frontmatter(rs.read_text(skill / "SKILL.md"))
                self.assertEqual(rs._parameters_block(body), expected, "the block shows what the agent means")
                self.assertEqual(rs.verify(skill), [], "check must accept what to-skill wrote")
                restored = rs.compile_skill(skill, tmp / "agents")
                self.assertEqual(restored.read_bytes(), agent.read_bytes(), "to-agent gives the file back unchanged")
                ok, msg = rs.roundtrip(agent, tmp / "rt-agent")
                self.assertTrue(ok, msg)
                ok, msg = rs.roundtrip(skill, tmp / "rt-skill")
                self.assertTrue(ok, msg)

    def test_defectB_prove_passes_for_origin_license_and_sealed_skills(self):
        """prove judges a skill by what it carries: its origin and license, and the plain skill inside a seal.

        roundtrip re-made the skill without the --origin and --license it was made
        with, and compared a sealed file's wrapper instead of the skill inside it,
        so every such valid skill was reported as FAIL. Now the way back carries
        origin, license and tool name from the skill itself and the comparison is
        against the unwrapped source.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            made = rs.toast(HELLO, tmp / "made", origin="https://example.invalid/hello", license_name="MIT")
            fields, _ = rs.parse_frontmatter(rs.read_text(made / "SKILL.md"))
            self.assertEqual(fields["license"], "MIT")
            self.assertEqual(fields["metadata"]["origin"], "https://example.invalid/hello")
            # A lone SKILL.md made with --origin and --license.
            lone = tmp / "lone" / "hello-world"
            lone.mkdir(parents=True)
            (lone / "SKILL.md").write_bytes((made / "SKILL.md").read_bytes())
            self.assertEqual(rs.verify(lone), [])
            ok, msg = rs.roundtrip(lone, tmp / "rt-lone")
            self.assertTrue(ok, msg)
            # The same skill sealed; the text inside the seal is the valid skill.
            sealed = tmp / "sealed" / "hello-world"
            sealed.mkdir(parents=True)
            rs.write_text(sealed / "SKILL.md", sealed_copy(rs.read_text(made / "SKILL.md"), "hello-world"))
            self.assertEqual(rs.verify(sealed), [])
            ok, msg = rs.roundtrip(sealed, tmp / "rt-sealed")
            self.assertTrue(ok, msg)
            # A sealed step-by-step skill, the other kind of skill there is.
            brief = tmp / "brief" / "writing-brief"
            brief.mkdir(parents=True)
            rs.write_text(brief / "SKILL.md", sealed_copy(rs.read_text(BRIEF / "SKILL.md"), "writing-brief"))
            self.assertEqual(rs.verify(brief), [])
            ok, msg = rs.roundtrip(brief, tmp / "rt-brief")
            self.assertTrue(ok, msg)
            # The shipped skill, through the command itself.
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = rs.main(["prove", str(ROOT / "skills" / "hello-world")])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertTrue(out.getvalue().startswith("PASS"), out.getvalue())

    def test_defectC_launcher_storage_stays_inside_its_folder(self):
        """The launcher's storage stand-in must keep every file under $AGENT_STORAGE.

        A file path with ".." or an absolute path was written wherever it pointed,
        and set_memory_context took anything, so "delete one folder to erase all of
        it" was not true and an agent behaved differently here than on a server,
        which refuses such paths. Now anything that would leave the folder raises
        ValueError, and a memory context must be a single folder name.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            skill = rs.toast(HELLO, tmp / "skills")
            spec = importlib.util.spec_from_file_location("hello_world_launcher", skill / "scripts" / "run.py")
            launcher = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(launcher)
            storage = tmp / "storage"
            with mock.patch.dict(os.environ, {"AGENT_STORAGE": str(storage)}):
                store = launcher.AzureFileStorageManager("share")
            # A named share lives in its own folder under shares/, named by the sha256 of
            # the name (review round three; the same layout a server uses).
            root = storage / "shares" / rs.sha256(b"share")
            self.assertTrue(root.is_dir())
            # Paths that would leave the folder are refused, and nothing is written.
            with self.assertRaises(ValueError) as caught:
                store.write_file("../escaped.txt", "x")
            self.assertIn("path escapes data directory", str(caught.exception))
            self.assertFalse((storage / "escaped.txt").exists())
            outside = tmp / "outside.json"
            with self.assertRaises(ValueError):
                store.write_json({"a": 1}, str(outside))
            self.assertFalse(outside.exists())
            with self.assertRaises(ValueError):
                store.read_file("sub/../../../etc")
            with self.assertRaises(ValueError):
                store.file_exists(str(HELLO))
            with self.assertRaises(ValueError):
                store.delete_file(str(HELLO))
            self.assertTrue(HELLO.is_file())
            with self.assertRaises(ValueError):
                store.list_files("..")
            elsewhere = tmp / "elsewhere"
            elsewhere.mkdir()
            try:
                (root / "link").symlink_to(elsewhere, target_is_directory=True)
            except OSError:
                pass  # symlinks unavailable here; the checks above still hold
            else:
                with self.assertRaises(ValueError):
                    store.write_file("link/x.txt", "x")
                self.assertEqual(list(elsewhere.iterdir()), [])
            # A memory context is one folder name, nothing that could be a path.
            for bad in (".", "..", "a/b", "a\\b", "a\nb", "../other", 5):
                with self.subTest(context=bad), self.assertRaises(ValueError):
                    store.set_memory_context(bad)
            # An empty name is a reset to the shared folder, as on a server (review round three).
            store.set_memory_context("user-1")
            self.assertTrue(store.set_memory_context(""))
            self.assertIsNone(store.current_guid)
            store.set_memory_context("user-1")
            store.write_json({"k": 1})
            self.assertEqual(store.read_json(), {"k": 1})
            self.assertTrue((root / "user-1" / "memory.json").is_file())
            store.set_memory_context(None)
            self.assertIn("user-1", store.list_files())
            # Everything the store touched lives under its one folder (shares/ is that folder's parent).
            for path in storage.rglob("*"):
                if path == storage / "shares":
                    continue
                self.assertIn(root, [path] + list(path.parents), path)


STORAGE_AGENT = '''"""An agent written the way most library agents are: bare imports a server resolves from its own folder."""
from basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager


class NoteAgent(BasicAgent):
    def __init__(self):
        self.name = "NoteAgent"
        self.metadata = {
            "name": self.name,
            "description": "Keeps one note.",
            "parameters": {"type": "object", "properties": {"note": {"type": "string"}}, "required": ["note"]},
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        store = get_storage_manager()
        store.write_json({"note": kwargs["note"]})
        return "kept: " + store.read_json()["note"]
'''

OTHER_ALIASES_AGENT = '''from openrappter.agents.basic_agent import BasicAgent
from utils.dynamics_storage import DynamicsStorageManager
from utils.azure_file_storage import AzureFileStorageManager
import agents.basic_agent
import basic_agent


class AliasAgent(BasicAgent):
    def __init__(self):
        self.name = "AliasAgent"
        self.metadata = {"name": self.name, "description": "Imports every name a server exposes."}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        same_class = BasicAgent is agents.basic_agent.BasicAgent is basic_agent.BasicAgent
        same_store = DynamicsStorageManager is AzureFileStorageManager
        return "same class: %s; same store: %s" % (same_class, same_store)
'''


MEMORY_AGENT = '''from agents.basic_agent import BasicAgent
from utils.azure_file_storage import AzureFileStorageManager


class ContextPeekAgent(BasicAgent):
    """Reads the storage helper the way library memory agents do: its attributes, not only its methods."""

    def __init__(self):
        self.name = "ContextPeekAgent"
        self.metadata = {
            "name": self.name,
            "description": "Reports what the storage helper exposes.",
            "parameters": {"type": "object", "properties": {"user_guid": {"type": "string"}}, "required": []},
        }
        super().__init__(self.name, self.metadata)
        self.storage_manager = AzureFileStorageManager()

    def perform(self, **kwargs):
        s = self.storage_manager
        out = {"before": s.current_guid, "share_name": s.share_name, "default_file_name": s.default_file_name,
               "storage_root": str(s.storage_root), "shared_memory_path": str(s.shared_memory_path)}
        s.set_memory_context(kwargs.get("user_guid") or "g1")
        s.write_json({"seen": True})
        folder = s.ensure_directory_exists("sub")
        s.write_file("sub/note.txt", "hi")
        out.update({"after": s.current_guid, "memory_path": str(s.current_memory_path), "sub": str(folder)})
        s.set_memory_context(None)
        out.update({"reset": s.current_guid, "reset_path": str(s.current_memory_path)})
        return out
'''


def load_launcher(skill: Path):
    """The launcher a toasted skill ships (scripts/run.py) as a module: the shim its agent runs under."""
    spec = importlib.util.spec_from_file_location("launcher_" + skill.name.replace("-", "_"), skill / "scripts" / "run.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    return launcher


class ConverterReview3(unittest.TestCase):
    """Third review round: one test per confirmed defect. Each fails on the converter before its fix."""

    def test_defect7_bare_and_factory_imports_convert_check_and_run(self):
        """An agent importing the names a server exposes converts, checks and runs.

        The launcher's shim registered only agents.basic_agent and
        utils.azure_file_storage, by hand. Most library agents write
        `from basic_agent import BasicAgent` (a server puts its agents folder on
        sys.path), and some use openrappter.agents.basic_agent,
        utils.dynamics_storage or utils.storage_factory; none of those could be
        converted, checked or run. Now one alias table names every module a
        server exposes, and a loop registers them without replacing anything
        already imported.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            agent = tmp / "note_agent.py"
            rs.write_text(agent, STORAGE_AGENT)
            skill = rs.toast(agent, tmp / "skills")
            self.assertEqual(skill.name, "note")
            self.assertEqual(rs.verify(skill), [], "check must accept an agent with bare imports")
            store = tmp / "storage"
            result = subprocess.run([sys.executable, "scripts/run.py", "--json", '{"note": "milk"}'], cwd=skill,
                                    capture_output=True, text=True, env=dict(os.environ, AGENT_STORAGE=str(store)))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "kept: milk")
            self.assertTrue((store / "default" / "memory.json").is_file(), "the factory hands out the local store")
            ok, msg = rs.roundtrip(agent, tmp / "rt")
            self.assertTrue(ok, msg)
            # The other names a server exposes, all resolving to the same objects.
            other = tmp / "alias_agent.py"
            rs.write_text(other, OTHER_ALIASES_AGENT)
            other_skill = rs.toast(other, tmp / "skills")
            self.assertEqual(rs.verify(other_skill), [])
            result = run_py("scripts/run.py", cwd=other_skill)
            self.assertEqual(result.stdout.strip(), "same class: True; same store: True", result.stderr)
            # A module already imported under one of those names is never replaced, and an
            # alias that is missing joins the class the present ones hold (a server's, when
            # running inside one) instead of bringing a second BasicAgent.
            planted = types.ModuleType("utils.dynamics_storage")
            planted.DynamicsStorageManager = object
            missing = ("openrappter", "openrappter.agents", "openrappter.agents.basic_agent")
            saved = {k: sys.modules.get(k) for k in ("utils", "utils.dynamics_storage", *missing)}
            try:
                sys.modules["utils.dynamics_storage"] = planted
                for key in missing:
                    sys.modules.pop(key, None)
                namespace: dict = {}
                exec(compile(rs.SHIM_SOURCE, "<shim>", "exec"), namespace)
                namespace["install_shims"]()
                self.assertIs(sys.modules["utils.dynamics_storage"], planted)
                present = sys.modules["agents.basic_agent"].BasicAgent
                self.assertIs(sys.modules["openrappter.agents.basic_agent"].BasicAgent, present)
                self.assertIsNot(present, namespace["BasicAgent"], "the alias joins the class already present")
                self.assertTrue(hasattr(sys.modules["openrappter"], "__path__"), "a created parent is a package")
            finally:
                for key, value in saved.items():
                    if value is None:
                        sys.modules.pop(key, None)
                    else:
                        sys.modules[key] = value

    def test_defect8_share_name_cannot_leave_agent_storage(self):
        """A share name is a name, never a path: every share lives under $AGENT_STORAGE.

        The launcher's storage stand-in built its folder as $AGENT_STORAGE/<share_name>,
        so a share named "../x" or an absolute path put the whole store outside
        the one folder the docstring promises, and the path check then contained
        files against that escaped folder. Now a share is a folder under shares/
        named by the sha256 of the normalised name, as on a server, and the
        boundary is always a fixed child of $AGENT_STORAGE.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            launcher = load_launcher(rs.toast(HELLO, tmp / "skills"))
            storage = tmp / "storage"
            outside = tmp / "outside"
            with mock.patch.dict(os.environ, {"AGENT_STORAGE": str(storage)}):
                for share in ("../x", str(outside), "sub/dir", "  Share  ", "share"):
                    with self.subTest(share=share):
                        store = launcher.AzureFileStorageManager(share)
                        self.assertEqual(store.base, storage)
                        self.assertEqual(store.root.parent, storage / "shares")
                        self.assertEqual(store.root.name, rs.sha256(share.strip().lower().encode("utf-8")))
                        store.write_json({"share": share})
                        self.assertEqual(store.read_json(), {"share": share})
                        with self.assertRaises(ValueError) as caught:
                            store.write_file("../escaped.txt", "x")
                        self.assertIn("path escapes data directory", str(caught.exception))
                self.assertFalse((tmp / "x").exists(), "'../x' must not become a folder beside the store")
                self.assertFalse(outside.exists(), "an absolute share name must not become a folder")
                # Case and surrounding whitespace do not make a different share; a real name does.
                self.assertEqual(launcher.AzureFileStorageManager("  Share  ").root, launcher.AzureFileStorageManager("share").root)
                self.assertNotEqual(launcher.AzureFileStorageManager("share").root, launcher.AzureFileStorageManager("other").root)
                unnamed = launcher.AzureFileStorageManager()
                self.assertEqual(unnamed.root, storage / "default")
                self.assertEqual(launcher.AzureFileStorageManager("").root, storage / "default")
            for path in tmp.rglob("*"):
                self.assertTrue(path == storage or storage in path.parents or path.is_relative_to(tmp / "skills"), path)

    def test_defect10_storage_stand_in_exposes_what_a_server_does(self):
        """The storage stand-in carries the attributes agents read, not only the methods they call.

        Library memory agents read storage_manager.current_guid (nine of them) and
        eight call ensure_directory_exists; the stand-in had neither, so those
        agents converted and checked but crashed when run. Now it exposes the
        server's attributes with the server's reset rules (None, "" or the marker
        guid means shared), and ensure_directory_exists makes a folder inside the
        store; every path stays under $AGENT_STORAGE.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp).resolve()  # paths the helper returns are resolved (macOS: /var -> /private/var)
            agent = tmp / "context_peek_agent.py"
            rs.write_text(agent, MEMORY_AGENT)
            skill = rs.toast(agent, tmp / "skills")
            self.assertEqual(rs.verify(skill), [])
            store = tmp / "storage"
            result = subprocess.run([sys.executable, "scripts/run.py", "--json", "{}"], cwd=skill,
                                    capture_output=True, text=True, env=dict(os.environ, AGENT_STORAGE=str(store)))
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            root = store / "default"
            self.assertEqual(out, {
                "before": None, "share_name": None, "default_file_name": "memory.json",
                "storage_root": str(root), "shared_memory_path": str(root),
                "after": "g1", "memory_path": str(root / "g1"), "sub": str(root / "g1" / "sub"),
                "reset": None, "reset_path": str(root),
            })
            self.assertEqual(json.loads((root / "g1" / "memory.json").read_text()), {"seen": True})
            self.assertEqual((root / "g1" / "sub" / "note.txt").read_text(), "hi")
            # The same rules, checked directly on the launcher's helper.
            launcher = load_launcher(skill)
            with mock.patch.dict(os.environ, {"AGENT_STORAGE": str(store)}):
                helper = launcher.AzureFileStorageManager(" Team ")
            self.assertEqual(helper.share_name, "team")
            self.assertIs(helper.storage_root, helper.root)
            self.assertEqual(helper.current_memory_path, helper.shared_memory_path)
            for reset in (None, "", helper.DEFAULT_MARKER_GUID):
                with self.subTest(reset=reset):
                    self.assertTrue(helper.set_memory_context("g2"))
                    self.assertEqual((helper.current_guid, helper.current_memory_path), ("g2", helper.root / "g2"))
                    self.assertTrue(helper.set_memory_context(reset))
                    self.assertEqual((helper.current_guid, helper.current_memory_path), (None, helper.shared_memory_path))
            for bad in ("a/b", "..", "trailing.", "CON", 5):
                with self.subTest(guid=bad), self.assertRaises(ValueError):
                    helper.set_memory_context(bad)
            self.assertIsNone(helper.current_guid, "a refused context leaves the current one alone")
            made = helper.ensure_directory_exists("reports/2026")
            self.assertTrue(made.is_dir())
            self.assertEqual(made, helper.root / "reports" / "2026")
            for escape in ("../out", str(tmp / "out"), "reports/../../out"):
                with self.subTest(directory=escape), self.assertRaises(ValueError) as caught:
                    helper.ensure_directory_exists(escape)
                self.assertIn("path escapes data directory", str(caught.exception))
            self.assertFalse((tmp / "out").exists())
            self.assertFalse((store / "out").exists())
            for path in store.rglob("*"):
                self.assertTrue(path == store / "shares" or root in path.parents or helper.root in path.parents or path in (root, helper.root), path)

    def test_defect9_parameters_section_is_found_however_it_is_written(self):
        """The 'What it needs' schema is found in ordinary variants, and an empty section is a problem.

        One strict regex accepted only "## What it needs" followed directly by a
        ```json fence with LF line ends. A trailing colon, CRLF, a sentence before
        the fence, a fence tagged JSON or " json", a longer fence, a tilde fence, or
        a bare JSON object all went unseen: check passed, prove passed, and the
        compiled tool silently got the default "request" schema. Now the section is
        found by its heading, then its first fenced block or first bare object; a
        section with nothing parseable is reported instead of defaulted.
        """
        schema = {"type": "object", "properties": {"topic": {"type": "string", "description": "What to cover"}}, "required": ["topic"]}
        block = json.dumps(schema, indent=2)
        variants = {
            "colon": "## What it needs:\n\n```json\n" + block + "\n```\n",
            "crlf": ("## What it needs\r\n\r\n```json\r\n" + block + "\r\n```\r\n").replace("\n", "\r\n").replace("\r\r\n", "\r\n"),
            "sentence": "## What it needs\n\nPass these as one JSON object:\n\n```json\n" + block + "\n```\n",
            "upper-tag": "## What it needs\n\n```JSON\n" + block + "\n```\n",
            "spaced-tag": "## What it needs\n\n``` json\n" + block + "\n```\n",
            "long-fence": "## What it needs\n\n````json\n" + block + "\n````\n",
            "tilde-fence": "## What it needs\n\n~~~json\n" + block + "\n~~~\n",
            "no-tag": "## What it needs\n\n```\n" + block + "\n```\n",
            "bare-object": "## What it needs\n\n" + block + "\n",
            "parameters-heading": "## Parameters\n\n```json\n" + block + "\n```\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for variant, section in variants.items():
                with self.subTest(variant=variant):
                    body = "# Outline\n\nMake an outline.\n\n" + section + "\n## Steps\n\n1. Write it.\n"
                    self.assertEqual(rs._parameters_block(body), schema)
                    skill = tmp / variant / "outline"
                    skill.mkdir(parents=True)
                    rs.write_text(skill / "SKILL.md", '---\nname: "outline"\ndescription: "Outlines a topic."\n---\n\n' + body)
                    self.assertEqual(rs.verify(skill), [])
                    compiled = rs.compile_skill(skill, tmp / variant / "agents")
                    _, agent = rs.load_agent(compiled)
                    self.assertEqual(agent.metadata["parameters"], schema, "the compiled tool must carry the written schema")
            # No section at all: the default schema, on purpose.
            absent = tmp / "absent" / "outline"
            absent.mkdir(parents=True)
            rs.write_text(absent / "SKILL.md", '---\nname: "outline"\ndescription: "Outlines a topic."\n---\n\n# Outline\n\nMake an outline.\n')
            self.assertIsNone(rs._parameters_block("# Outline\n\nMake an outline.\n"))
            self.assertEqual(rs.verify(absent), [])
            _, agent = rs.load_agent(rs.compile_skill(absent, tmp / "absent" / "agents"))
            self.assertEqual(agent.metadata["parameters"], rs.DEFAULT_PARAMETERS)
            # A section that holds nothing parseable is a problem, never a silent default.
            empties = {
                "prose": "## What it needs\n\nJust the topic.\n",
                "empty": "## What it needs\n",
                "bad-json": "## What it needs\n\n```json\n{\"type\": \"object\",\n```\n",
                "not-an-object": "## What it needs\n\n```json\n[\"topic\"]\n```\n",
            }
            for variant, section in empties.items():
                with self.subTest(variant=variant):
                    body = "# Outline\n\n" + section + "\n## Steps\n\n1. Write it.\n"
                    with self.assertRaises(ValueError):
                        rs._parameters_block(body)
                    skill = tmp / ("bad-" + variant) / "outline"
                    skill.mkdir(parents=True)
                    rs.write_text(skill / "SKILL.md", '---\nname: "outline"\ndescription: "Outlines a topic."\n---\n\n' + body)
                    problems = rs.verify(skill)
                    self.assertTrue(any("What it needs" in p for p in problems), problems)
                    with self.assertRaises(RuntimeError):
                        rs.compile_skill(skill, tmp / ("bad-" + variant) / "agents")


class FolderConversion(unittest.TestCase):
    def test_folder_to_agent_writes_shared_code_once(self):
        """Two skills from one file of two tools restore to one Python file, not two copies."""
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            rc = rs.main(["to-skill", str(FIXTURES / "pair_agent.py"), "--out", str(skills)])
            self.assertEqual(rc, 0)
            self.assertEqual(sorted(p.name for p in skills.iterdir()), ["farewell", "greet"])
            agents = Path(tmp) / "agents"
            rc = rs.main(["to-agent", str(skills), "--out", str(agents)])
            self.assertEqual(rc, 0)
            files = sorted(p.name for p in agents.iterdir())
            self.assertEqual(len(files), 1, files)
            self.assertEqual((agents / files[0]).read_bytes(), (FIXTURES / "pair_agent.py").read_bytes())


class RepositoryIsConsistent(unittest.TestCase):
    def test_shipped_skills_verify(self):
        for skill in sorted((ROOT / "skills").iterdir()):
            with self.subTest(skill=skill.name):
                self.assertEqual(rs.verify(skill), [])

    def test_manifests_are_current(self):
        self.assertEqual(rs.manifests(ROOT, check=True), [])

    def test_host_adapters_are_complete(self):
        required = {"name", "display", "verified", "skill_dirs", "plugin_manifest", "marketplace", "agents", "install", "skill_invocation", "instruction_files", "docs"}
        optional = {"evidence"}
        hosts = sorted((ROOT / "hosts").glob("*.json"))
        self.assertGreaterEqual(len(hosts), 2)
        for path in hosts:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(data) - required - optional, set(), path.name)
            self.assertEqual(required - set(data), set(), path.name)
            self.assertEqual(data["name"], path.stem)

    def test_converter_skill_carries_its_own_code(self):
        text = rs.read_text(ROOT / "skills" / "rapp-skills" / "SKILL.md")
        m = re.search(r"<!-- code sha256=([0-9a-f]{64}) -->\n(`{3,})python\n(.*?)\n\2\n<!-- /code -->", text, re.S)
        self.assertIsNotNone(m, "converter skill must embed its code")
        script = rs.read_text(ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py")
        self.assertEqual(m.group(3) + "\n", script)
        self.assertEqual(rs.sha256(script.encode("utf-8")), m.group(1))
        for word in ("plugin", "marketplace"):
            self.assertNotIn(word, text.split("## The code")[0].lower())

    def test_readme_speaks_in_capabilities(self):
        readme = rs.read_text(ROOT / "README.md").lower()
        for word in ("toast", "compile", "frontmatter", "round-trip", "playbook", "egg", "organism", "plugin", "marketplace"):
            self.assertNotIn(word, readme, word)

    def test_runner_in_skill_equals_converter_runner(self):
        shipped = rs.read_text(ROOT / "skills" / "hello-world" / "scripts" / "run.py")
        self.assertEqual(shipped, rs.RUN_PY.lstrip("\n"))

    def test_shim_embeds_verbatim_in_a_js_template(self):
        """A browser page pastes SHIM_SOURCE into a JS raw template: no backtick, no dollar-brace."""
        self.assertNotIn("`", rs.SHIM_SOURCE)
        self.assertNotIn("${", rs.SHIM_SOURCE)


if __name__ == "__main__":
    unittest.main()


class ConverterReview4(unittest.TestCase):
    """Round four: a folder backup keeps every agent, files read as written, launchers do not go stale."""

    def _agent(self, tool: str, cls: str) -> str:
        return (
            "from agents.basic_agent import BasicAgent\n\n\n"
            f"class {cls}(BasicAgent):\n"
            "    def __init__(self):\n"
            f"        self.name = {tool!r}\n"
            "        self.metadata = {'name': self.name, 'description': 'd', 'parameters': {'type': 'object', 'properties': {}, 'required': []}}\n"
            "        super().__init__(self.name, self.metadata)\n\n"
            "    def perform(self, **kwargs):\n"
            f"        return {cls!r}\n"
        )

    def test_defect11_folder_backup_refuses_colliding_skills_and_restores_file_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / "agents"
            agents.mkdir()
            rs.write_text(agents / "summarize_agent.py", self._agent("Summarize", "SummarizeAgent"))
            rs.write_text(agents / "summarize_docs_agent.py", self._agent("SummarizeAgent", "SummarizeDocsAgent"))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = rs.main(["to-skill", str(agents), "--out", str(Path(tmp) / "skills")])
            self.assertNotEqual(rc, 0, "two files that become one skill must not be a silent success")
            printed = out.getvalue()
            self.assertIn("summarize_agent.py", printed)
            self.assertIn("summarize_docs_agent.py", printed)
            self.assertIn("'summarize'", printed)
            # the first file's backup is intact, not replaced by the second
            written = rs.load_skill_text(Path(tmp) / "skills" / "summarize" / "SKILL.md")
            self.assertIn("SummarizeAgent(BasicAgent)", written)
            self.assertNotIn("SummarizeDocsAgent", written)

        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / "agents"
            agents.mkdir()
            # a tool whose name does not spell its file name: the backup must still give the file back
            rs.write_text(agents / "weather_agent.py", self._agent("GetWeather", "WeatherAgent"))
            rs.write_text(agents / "news_agent.py", self._agent("LatestNews", "NewsAgent"))
            skills, restored = Path(tmp) / "skills", Path(tmp) / "restored"
            self.assertEqual(rs.main(["to-skill", str(agents), "--out", str(skills)]), 0)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rs.main(["to-agent", str(skills), "--out", str(restored)]), 0)
            self.assertEqual(sorted(p.name for p in restored.iterdir()), ["news_agent.py", "weather_agent.py"])
            for name in ("weather_agent.py", "news_agent.py"):
                self.assertEqual((restored / name).read_bytes(), (agents / name).read_bytes())
            # a recorded file name is only ever a plain *_agent.py name: never a path
            fields = {"name": "weather", "metadata": {"file": "../evil_agent.py"}}
            self.assertEqual(rs.restored_file_name(fields), "weather_agent.py")

    def test_defect12_crlf_and_bom_skills_read_as_written(self):
        source = rs.read_text(BRIEF / "SKILL.md")
        toasted_src = None
        with tempfile.TemporaryDirectory() as tmp:
            hello = rs.toast(HELLO, Path(tmp) / "skills")
            toasted_src = rs.read_text(hello / "SKILL.md")
            agent_bytes = (hello / "scripts" / "agent.py").read_bytes()
        variants = {
            "lf": source.encode("utf-8"),
            "crlf": source.replace("\n", "\r\n").encode("utf-8"),
            "bom": b"\xef\xbb\xbf" + source.encode("utf-8"),
        }
        compiled: dict[str, bytes] = {}
        for label, data in variants.items():
            with tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "writing-brief"
                skill.mkdir()
                (skill / "SKILL.md").write_bytes(data)
                self.assertEqual(rs.verify(skill), [], label)
                ok, msg = rs.roundtrip(skill, Path(tmp) / "rt")
                self.assertTrue(ok, f"{label}: {msg}")
                compiled[label] = rs.compile_skill(skill, Path(tmp) / "agents").read_bytes()
                self.assertIsNotNone(rs._parameters_block(rs.parse_frontmatter(rs.load_skill_text(skill / "SKILL.md"))[1]), label)
        self.assertEqual(compiled["lf"], compiled["crlf"])
        self.assertEqual(compiled["lf"], compiled["bom"])
        # a converted skill (embedded code with its sha) translated to CRLF still restores its code
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "hello-world"
            skill.mkdir()
            (skill / "SKILL.md").write_bytes(b"\xef\xbb\xbf" + toasted_src.replace("\n", "\r\n").encode("utf-8"))
            self.assertEqual(rs.verify(skill), [])
            self.assertEqual(rs.compile_skill(skill, Path(tmp) / "agents").read_bytes(), agent_bytes)
        # mixed endings are content and stay byte-exact
        mixed = "---\nname: \"x\"\n---\n\nline one\r\nline two\n"
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "SKILL.md"
            p.write_bytes(mixed.encode("utf-8"))
            self.assertEqual(rs.load_skill_text(p), mixed)

    def test_defect13_stale_launcher_is_reported_and_refreshed(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = rs.toast(HELLO, Path(tmp) / "skills")
            self.assertEqual(rs.verify(skill), [])
            text = rs.read_text(skill / "SKILL.md")
            block, claimed = rs.extract_runner(text)
            self.assertIsNotNone(claimed, "the launcher block must carry its sha256")
            self.assertEqual(rs.sha256(block.encode("utf-8")), claimed)
            # the launcher an older converter wrote: same shape, different code, bare marker
            stale = block.replace("def main(", "def main(  # older launcher\n", 1)
            old_block = "<!-- runner -->\n" + rs.embed_block(stale, "", rs.RUNNER_CLOSE).split("\n", 1)[1]
            start = text.index("<!-- runner sha256=")
            end = text.index(rs.RUNNER_CLOSE, start) + len(rs.RUNNER_CLOSE)
            rs.write_text(skill / "SKILL.md", text[:start] + old_block + text[end:])
            rs.write_text(skill / "scripts" / "run.py", stale)
            problems = rs.verify(skill)
            self.assertTrue(any("older converter" in p for p in problems), problems)
            self.assertTrue(any("scripts/run.py" in p and "launcher block" in p for p in problems), problems)
            # the code is still restorable: staleness never blocks getting the agent back
            restored = rs.compile_skill(skill, Path(tmp) / "agents")
            self.assertEqual(restored.read_bytes(), HELLO.read_bytes())
            # converting again refreshes both copies
            rs.toast(restored, Path(tmp) / "skills")
            self.assertEqual(rs.verify(skill), [])
            # a launcher block whose sha does not match its own marker is reported too
            text = rs.read_text(skill / "SKILL.md")
            rs.write_text(skill / "SKILL.md", text.replace("def main(", "def main(  # edited\n", 1))
            self.assertTrue(any("does not match its sha256" in p for p in rs.verify(skill)), rs.verify(skill))


    def test_defect14_sealed_skill_whose_text_contains_an_end_marker_line(self):
        inner = rs.read_text(BRIEF / "SKILL.md").rstrip("\n") + "\n\n## Notes\n\nA seal ends with this line on its own:\n\n<!-- RAW-SKILL-END -->\n\nand nothing after it counts.\n"
        digest = rs.sha256(inner.encode("utf-8"))
        sealed = f"---\nname: writing-brief\nschema: rapp/1-skill\nskill_hash: {digest}\n---\n<!-- RAW-SKILL-BEGIN sha256={digest} -->\n{inner}<!-- RAW-SKILL-END -->\n"
        self.assertEqual(rs.unwrap_sealed(sealed), inner)
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "writing-brief"
            skill.mkdir()
            rs.write_text(skill / "SKILL.md", sealed)
            self.assertEqual(rs.verify(skill), [])
        # a seal that matches no END marker is still refused
        with self.assertRaises(ValueError):
            rs.unwrap_sealed(sealed.replace("nothing after it", "something after it"))
