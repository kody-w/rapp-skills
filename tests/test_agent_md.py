import pathlib
import unittest

import agent_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = (ROOT / "examples" / "hello.agent.md").read_text(encoding="utf-8")


class AgentMdTest(unittest.TestCase):
    def test_example_passes(self):
        info = agent_md.check(EXAMPLE)
        self.assertEqual(info["name"], "hello")
        self.assertEqual(info["class"], "HelloAgent")

    def test_one_changed_character_is_refused(self):
        tampered = EXAMPLE.replace("Hello, {", "Hullo, {", 1)
        self.assertNotEqual(tampered, EXAMPLE)
        with self.assertRaises(agent_md.Refused):
            agent_md.check(tampered)

    def test_two_python_blocks_are_refused(self):
        with self.assertRaises(agent_md.Refused):
            agent_md.check(EXAMPLE + "\n```python\nprint('x')\n```\n")

    def test_unknown_header_field_is_refused(self):
        with self.assertRaises(agent_md.Refused):
            agent_md.check(EXAMPLE.replace("license: MIT", "license: MIT\nagent: HelloAgent", 1))

    def test_extracted_code_compiles_and_is_never_run(self):
        compile(agent_md.code_block(EXAMPLE), "hello.agent.md", "exec")

    def test_it_is_still_a_plain_skill(self):
        head = EXAMPLE.split("\n---\n", 1)[0]
        keys = {l.split(":")[0] for l in head.splitlines()[1:] if l and not l.startswith(" ")}
        self.assertTrue(keys <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"})


    def test_legacy_agent_moves_in_and_comes_back_byte_for_byte(self):
        legacy = (ROOT / "tests" / "fixtures" / "legacy_weather_agent.py").read_text(encoding="utf-8")
        md = agent_md.from_agent(legacy, "legacy_weather")
        info = agent_md.check(md)
        self.assertEqual(info["name"], "weather-lookup")
        self.assertEqual(info["class"], "WeatherLookupAgent")
        self.assertEqual(agent_md.code_block(md), legacy)
        self.assertIn("description: Looks up a forecast", md)


if __name__ == "__main__":
    unittest.main()
