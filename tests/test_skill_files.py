"""A hand-written skill's own files (scripts, references, anything) ride inside its one agent file."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("rapp_skills_core", ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py")
rs = importlib.util.module_from_spec(spec)
sys.modules["rapp_skills_core"] = rs
spec.loader.exec_module(rs)

SKILL = "---\nname: tide-table\ndescription: Says when the tide turns.\n---\n\n# Tide table\n\nRun `scripts/tide.sh`.\n"


def make(base: Path, files: dict[str, bytes]) -> Path:
    d = base / "tide-table"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(SKILL)
    for rel, data in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_bytes(data)
    return d


class SkillFilesRideAlong(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    FILES = {"scripts/tide.sh": b"#!/bin/sh\necho high at noon\n", "references/ports.md": "# Ports\n\nBrest — high\n".encode(),
             "assets/dot.bin": bytes(range(256)), "notes/crlf.txt": b"a\r\nb\r\n"}

    def test_there_and_back_is_byte_identical(self):
        src = make(self.t / "src", self.FILES)
        agent = rs.compile_skill(src, self.t / "agents")
        back = rs.toast(agent, self.t / "back")
        self.assertEqual((back / "SKILL.md").read_bytes(), (src / "SKILL.md").read_bytes())
        self.assertEqual(rs.carried_files(back), self.FILES)
        ok, why = rs.roundtrip(src, self.t / "rt")
        self.assertTrue(ok, why)
        self.assertIn("all 4 of its files", why)

    def test_a_skill_with_no_files_is_written_exactly_as_before(self):
        src = make(self.t / "src", {})
        text = rs.compile_skill(src, self.t / "agents").read_text()
        self.assertNotIn("SKILL_FILES", text)
        self.assertNotIn("_carried", text)
        self.assertEqual(rs.roundtrip(src, self.t / "rt"), (True, "SKILL.md came back byte-identical"))

    def test_the_agent_hands_its_files_out(self):
        src = make(self.t / "src", self.FILES)
        loaded = rs.load_agent(rs.compile_skill(src, self.t / "agents"))
        agent = loaded[-1] if isinstance(loaded, tuple) else loaded
        self.assertIn("scripts/tide.sh", agent.perform())                       # the playbook lists what it carries
        self.assertEqual(agent.perform(skill_file="scripts/tide.sh"), "#!/bin/sh\necho high at noon\n")
        self.assertIn("No such file", agent.perform(skill_file="nope"))
        out = self.t / "laid"
        self.assertIn("Wrote 4 files", agent.perform(skill_files_to=str(out)))
        self.assertEqual({p.relative_to(out).as_posix(): p.read_bytes() for p in out.rglob("*") if p.is_file()}, self.FILES)

    def test_a_changed_file_is_refused(self):
        src = make(self.t / "src", self.FILES)
        agent = rs.compile_skill(src, self.t / "agents")
        agent.write_text(agent.read_text().replace("echo high at noon", "echo low at noon"))
        with self.assertRaises(RuntimeError):
            rs.toast(agent, self.t / "back")

    def test_too_big_or_linked_says_so(self):
        src = make(self.t / "big", {"models/weights.bin": b"0" * (rs.CARRY_LIMIT + 1)})
        with self.assertRaisesRegex(RuntimeError, "Move data and models out"):
            rs.compile_skill(src, self.t / "agents")
        src = make(self.t / "link", {"scripts/real.sh": b"x\n"})
        (src / "scripts" / "alias.sh").symlink_to(src / "scripts" / "real.sh")
        with self.assertRaisesRegex(RuntimeError, "is a link"):
            rs.compile_skill(src, self.t / "agents")

    def test_prove_notices_a_lost_file(self):
        src = make(self.t / "src", self.FILES)
        real = rs._pack_files
        rs._pack_files = lambda files: real({k: v for k, v in files.items() if k != "references/ports.md"})
        try:
            ok, why = rs.roundtrip(src, self.t / "rt")
        finally:
            rs._pack_files = real
        self.assertFalse(ok)
        self.assertIn("references/ports.md", why)


if __name__ == "__main__":
    unittest.main()
