"""rapp-skills: the conversion is lossless, the skills are standard, the hosts do not drift."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "rapp-skills" / "scripts"))
import rapp_skills as rs  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
HELLO = FIXTURES / "hello_world_agent.py"
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
