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
import unittest
from pathlib import Path

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
            runner = re.search(r"<!-- runner -->\n```python\n(.*?)\n```\n<!-- /runner -->", text, re.S).group(1)
            (drop / "agent.py").write_bytes(rs.extract_agent(text))
            rs.write_text(drop / "run.py", runner + "\n")
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


if __name__ == "__main__":
    unittest.main()
