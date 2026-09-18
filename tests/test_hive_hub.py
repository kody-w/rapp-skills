"""The imported Hive Hub skill stays exact, portable, and safety-preserving."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "hive-hub"
RUNNER = SKILL / "scripts" / "run.py"
SOURCE = ROOT / "sources" / "hive-hub.json"
EXPECTED_COMMIT = "93c8979caf5a51017898996aadaa42dddcfb75b2"
EXPECTED_GIT_TREE = "e9e8dba608aa47adafa2156b28d7bacc1d00ac04"
EXPECTED_FOLDER_SHA256 = (
    "021c56f939a900e7c3c57aab9d6e6fa79b13a539a7dae6737c57a7485ebe573f"
)
DENIED_PRIVATE_IDENTIFIER_SHA256 = frozenset(
    {
        "18bd7d72c25c6360e675996cf605328e499729c72c6035d55a4cbaf05992327c",
        "30c31ea528886a0b83fa156fe7f5e8da4a7fde32f0a3ad8a6fd83d6fae765cd2",
    }
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


converter = load_module(
    "rapp_skills_for_hive_hub",
    ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py",
)


def run_skill(
    skill: Path,
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(skill / "scripts" / "run.py"),
            *arguments,
        ],
        cwd=cwd or ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )


def result_of(process: subprocess.CompletedProcess[str]) -> dict:
    if process.stderr:
        raise AssertionError(f"unexpected stderr: {process.stderr}")
    return json.loads(process.stdout)


class HiveHubIntegrationTests(unittest.TestCase):
    def test_exact_source_provenance_and_native_lock(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(source["schema"], "rapp-skill-source/1")
        self.assertEqual(source["repository"], "https://github.com/kody-w/hive-hub")
        self.assertEqual(source["ref"], "refs/heads/main")
        self.assertEqual(source["commit"], EXPECTED_COMMIT)
        self.assertEqual(source["git_tree"], EXPECTED_GIT_TREE)
        self.assertEqual(source["folder_sha256"], EXPECTED_FOLDER_SHA256)
        self.assertEqual(source["path"], "skills/hive-hub")
        self.assertEqual(len(source["files"]), 10)
        paths = [entry["path"] for entry in source["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertIn("agent.lock", paths)
        self.assertEqual(converter._source_manifest_problems(ROOT, SOURCE), [])

        lock = json.loads((SKILL / "agent.lock").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "hive-hub-agent-lock/1")
        self.assertEqual(lock["name"], "hive-hub")
        self.assertEqual(lock["version"], "0.1.0")
        source_files = {
            entry["path"]: (entry["bytes"], entry["sha256"])
            for entry in source["files"]
        }
        self.assertEqual(
            {entry["path"] for entry in lock["files"]},
            set(source_files) - {"agent.lock"},
        )
        for entry in lock["files"]:
            self.assertEqual(
                (entry["bytes"], entry["sha256"]),
                source_files[entry["path"]],
            )

        fields, _ = converter.parse_frontmatter(
            converter.read_text(SKILL / "SKILL.md")
        )
        self.assertEqual(
            set(fields),
            {
                "name",
                "description",
                "license",
                "compatibility",
                "metadata",
                "allowed-tools",
            },
        )
        self.assertEqual(converter.verify(SKILL), [])

    def test_source_owned_lock_is_verified_and_never_rewritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "skills" / "hive-hub"
            copied.parent.mkdir(parents=True)
            shutil.copytree(SKILL, copied)
            sources = root / "sources"
            sources.mkdir()
            copied_source = sources / "hive-hub.json"
            shutil.copy2(SOURCE, copied_source)
            lock_path = copied / "agent.lock"
            before = lock_path.read_bytes()
            rendered = converter._render_skill_lock(lock_path)
            self.assertEqual(rendered.encode("utf-8"), before)
            self.assertEqual(lock_path.read_bytes(), before)

            runner = copied / "scripts" / "run.py"
            runner.write_bytes(runner.read_bytes() + b"\n")
            lock_problems = converter.verify(copied)
            self.assertTrue(
                any("locked path" in problem for problem in lock_problems),
                lock_problems,
            )
            with self.assertRaises(ValueError):
                converter._render_skill_lock(lock_path)
            source_problems = converter._source_manifest_problems(
                root,
                copied_source,
            )
            self.assertTrue(
                any("scripts/run.py" in problem for problem in source_problems),
                source_problems,
            )
            self.assertEqual(lock_path.read_bytes(), before)

    def test_runner_verifies_decodes_and_uses_only_stdlib(self):
        verified_process = run_skill(SKILL, "verify")
        self.assertEqual(verified_process.returncode, 0)
        verified = result_of(verified_process)
        self.assertEqual(verified["status"], "verified")
        self.assertEqual(verified["files_verified"], 9)
        self.assertTrue(verified["ready"])
        self.assertTrue(verified["isolated"])
        self.assertTrue(verified["stdlib_only"])

        decoded_process = run_skill(
            SKILL,
            "decode",
            "--locator",
            "example/hive at main",
        )
        self.assertEqual(decoded_process.returncode, 0)
        decoded = result_of(decoded_process)
        self.assertEqual(decoded["status"], "decoded")
        self.assertEqual(decoded["external_effects"], [])
        self.assertFalse(decoded["ready"])

        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertTrue(imported.issubset(sys.stdlib_module_names | {"__future__"}))

    def test_copied_skill_folder_operates_without_repository_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "Copied Hive Hub With Spaces"
            shutil.copytree(SKILL, copied)
            verified = result_of(run_skill(copied, "verify", cwd=root))
            self.assertEqual(verified["status"], "verified")
            decoded = result_of(
                run_skill(
                    copied,
                    "decode",
                    "--locator",
                    "example/hive at main",
                    cwd=root,
                )
            )
            self.assertEqual(decoded["status"], "decoded")
            self.assertFalse((root / ".agent-storage").exists())

    def test_agent_and_host_projections_preserve_safety_boundaries(self):
        claude = ROOT / "agents" / "hive-hub.md"
        copilot = ROOT / ".github" / "agents" / "hive-hub.agent.md"
        claude_fields, claude_body = converter.parse_frontmatter(
            converter.read_text(claude)
        )
        copilot_fields, copilot_body = converter.parse_frontmatter(
            converter.read_text(copilot)
        )
        self.assertEqual(
            set(claude_fields),
            {"name", "description", "tools"},
        )
        self.assertEqual(claude_fields["tools"], "Bash, Read, Camera")
        self.assertEqual(
            set(copilot_fields),
            {"name", "description"},
        )
        self.assertEqual(copilot_body, claude_body)
        for boundary in (
            "Preserve the person's locator exactly.",
            "complete `plan_digest`",
            "one blocker",
            "`--card-stdin`",
            "Never execute repository or downloaded code",
            '"status": "ready"',
            '"ready": true',
            "work around a refusal",
        ):
            self.assertIn(boundary, claude_body)

        plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("hive-hub", plugin["keywords"])
        self.assertEqual(
            json.loads(
                (ROOT / ".claude-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            ),
            plugin,
        )
        self.assertEqual(converter.manifests(ROOT, check=True), [])

    def test_integration_surface_passes_private_identifier_and_secret_scan(self):
        candidate_re = re.compile(
            r"(?<![A-Za-z0-9_.-])"
            r"[A-Za-z0-9][A-Za-z0-9_.-]{2,127}"
            r"(?:/[A-Za-z0-9][A-Za-z0-9_.-]{1,127})?"
            r"(?![A-Za-z0-9_.-])"
        )
        repository_re = re.compile(
            r"(?:https://(?:raw\.)?githubusercontent\.com/|"
            r"https://github\.com/)"
            r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
        )
        local_path_re = re.compile(
            r"(?:/Users/[A-Za-z0-9._-]+/|"
            r"[A-Za-z]:/Users/[A-Za-z0-9._-]+/)"
        )
        secret_re = re.compile(
            r"(?:gh[pousr]_[A-Za-z0-9]{20,}|"
            r"github_pat_[A-Za-z0-9_]{20,}|"
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
            r"AKIA[0-9A-Z]{16})"
        )
        surface = {
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".github" / "agents" / "hive-hub.agent.md",
            ROOT / ".github" / "plugin" / "marketplace.json",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "agents" / "hive-hub.md",
            ROOT / "plugin.json",
            ROOT / "skills" / "rapp-skills" / "SKILL.md",
            ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py",
            SOURCE,
            Path(__file__),
        }
        surface.update(item for item in SKILL.rglob("*") if item.is_file())
        for path in sorted(surface):
            data = path.read_bytes()
            if b"\0" in data:
                continue
            try:
                content = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            candidates = [
                match.group(0)
                for match in candidate_re.finditer(content)
            ]
            candidates.extend(
                match.group(1).removesuffix(".git")
                for match in repository_re.finditer(content)
            )
            for candidate in candidates:
                for normalized in {candidate, candidate.casefold()}:
                    digest = hashlib.sha256(
                        normalized.encode("utf-8")
                    ).hexdigest()
                    self.assertNotIn(
                        digest,
                        DENIED_PRIVATE_IDENTIFIER_SHA256,
                        path.relative_to(ROOT),
                    )
            self.assertIsNone(
                local_path_re.search(content),
                path.relative_to(ROOT),
            )
            self.assertIsNone(
                secret_re.search(content),
                path.relative_to(ROOT),
            )


if __name__ == "__main__":
    unittest.main()
