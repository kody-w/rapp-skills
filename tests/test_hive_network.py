"""The network workflow is one portable file, not a privileged runtime."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.test_hive_hub import converter

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "hive-network"


class HiveNetworkTests(unittest.TestCase):
    def test_one_file_is_valid_and_complete(self):
        self.assertEqual(sorted(path.name for path in SKILL.iterdir()), ["SKILL.md"])
        self.assertEqual(converter.verify(SKILL), [])
        fields, body = converter.parse_frontmatter(
            (SKILL / "SKILL.md").read_text(encoding="utf-8")
        )
        self.assertEqual(fields["name"], "hive-network")
        self.assertIn("organization-seeds.json", body)
        self.assertIn("initialize.json", body)
        self.assertIn("contribution-prepared", body)
        self.assertIn("Browser-only AIs", fields["compatibility"])
        self.assertIn("No apply is implied", body)
        self.assertIn("Submission is not acceptance", body)

    def test_file_survives_conversion_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            ok, detail = converter.roundtrip(SKILL, Path(temporary))
        self.assertTrue(ok, detail)

    def test_an_ai_receives_the_workflow_without_implicit_effects(self):
        before = (SKILL / "SKILL.md").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            compiled = converter.compile_skill(SKILL, Path(temporary))
            _module, agent = converter.load_agent(compiled)
            result = agent.perform(request="Inspect public organization seeds only.")
        self.assertIn("Inspect public organization seeds only.", result)
        self.assertIn("result.plan_sha256", result)
        self.assertIn("source's", result)
        self.assertEqual((SKILL / "SKILL.md").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
