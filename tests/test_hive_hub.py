"""The imported Hive Hub skill stays exact, portable, and safety-preserving."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "hive-hub"
RUNNER = SKILL / "scripts" / "run.py"
SOURCE = ROOT / "sources" / "hive-hub.json"
EXPECTED_COMMIT = "68203b0c6940ee88b6246021a24f62dfd235dee7"
EXPECTED_GIT_TREE = "62da34d05e5ffbd1ebbbadfc31e9fe95862c40b3"
EXPECTED_FOLDER_SHA256 = (
    "c4d2bd36a52b4e0da75515e7c388899f613917cb5db9fdc36163426bd30cfc4b"
)
DENIED_PRIVATE_IDENTIFIER_SHA256 = frozenset(
    {
        "18bd7d72c25c6360e675996cf605328e499729c72c6035d55a4cbaf05992327c",
        "30c31ea528886a0b83fa156fe7f5e8da4a7fde32f0a3ad8a6fd83d6fae765cd2",
        "8b0314b3b0431a8c807bed46a21c8c43f575fffc8126f55e084c6395e0bed462",
        "3de06aca19269dfcaaaf7d0d0f07a9608ef7da210f5942864a41d42889a55d6b",
        "6c883d27f71c21d79b16488ccaf6fa3ddc86d1ada89fd8f00a2600d6318d9570",
        "6504cb31f5bfc9201ff5090eadda58aea7f66ad348f284bb065271711df85beb",
        "06b6da15e447d50451f2c76cbbe11098231277a937f54c5190a0294517531794",
        "1ed1846809379a9b81155c3df771ef09a741327a550596a58827b53eefc46866",
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


def with_link_count(information: os.stat_result, link_count: int) -> os.stat_result:
    values = list(information)
    values[3] = link_count
    return os.stat_result(values)


class MockWindowsFileApi:
    def __init__(
        self,
        *,
        number_of_links: int = 1,
        attributes: int = 0,
        create_success: bool = True,
        information_success: bool = True,
        close_success: bool = True,
    ) -> None:
        self.number_of_links = number_of_links
        self.attributes = attributes
        self.create_success = create_success
        self.information_success = information_success
        self.close_success = close_success
        self.handle = 1234
        self.create_calls: list[tuple[str, int, int, int, int]] = []
        self.closed_handles: list[int] = []

    def CreateFileW(
        self,
        path: str,
        desired_access: int,
        share_mode: int,
        _security_attributes: object,
        creation_disposition: int,
        flags_and_attributes: int,
        _template_file: object,
    ) -> int:
        self.create_calls.append(
            (
                path,
                desired_access,
                share_mode,
                creation_disposition,
                flags_and_attributes,
            )
        )
        if self.create_success:
            return self.handle
        import ctypes

        return int(ctypes.c_void_p(-1).value or -1)

    def GetFileInformationByHandle(
        self,
        _handle: int,
        information_pointer: Any,
    ) -> int:
        if not self.information_success:
            return 0
        information = information_pointer._obj
        information.dwFileAttributes = self.attributes
        information.nNumberOfLinks = self.number_of_links
        return 1

    def CloseHandle(self, handle: int) -> int:
        self.closed_handles.append(handle)
        return int(self.close_success)


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
        self.assertEqual(lock["version"], "0.1.1")
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

    def test_converter_windows_link_policy_uses_true_native_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            ordinary = Path(temporary) / "ordinary.txt"
            ordinary.write_bytes(b"ordinary")
            information = os.lstat(ordinary)
            for api, accepted in (
                (MockWindowsFileApi(number_of_links=1), True),
                (MockWindowsFileApi(number_of_links=2), False),
                (
                    MockWindowsFileApi(
                        number_of_links=1,
                        attributes=converter.FILE_ATTRIBUTE_REPARSE_POINT,
                    ),
                    False,
                ),
                (MockWindowsFileApi(create_success=False), False),
                (MockWindowsFileApi(information_success=False), False),
                (MockWindowsFileApi(close_success=False), False),
            ):
                with (
                    self.subTest(api=api, accepted=accepted),
                    mock.patch.object(converter, "_is_windows", return_value=True),
                    mock.patch.object(converter, "_windows_file_api", return_value=api),
                ):
                    self.assertEqual(
                        converter._has_single_file_link(ordinary, information),
                        accepted,
                    )
                if api.create_success:
                    self.assertEqual(api.closed_handles, [api.handle])
                if accepted:
                    _, desired_access, share_mode, disposition, flags = (
                        api.create_calls[0]
                    )
                    self.assertEqual(desired_access, 0)
                    self.assertEqual(
                        share_mode,
                        converter.FILE_SHARE_READ
                        | converter.FILE_SHARE_WRITE
                        | converter.FILE_SHARE_DELETE,
                    )
                    self.assertEqual(disposition, converter.OPEN_EXISTING)
                    self.assertTrue(
                        flags & converter.FILE_FLAG_OPEN_REPARSE_POINT
                    )

        with mock.patch.object(converter, "_is_windows", return_value=False):
            information = os.lstat(SKILL / "SKILL.md")
            self.assertFalse(
                converter._has_single_file_link(
                    SKILL / "SKILL.md",
                    with_link_count(information, 0),
                )
            )
            self.assertTrue(
                converter._has_single_file_link(
                    SKILL / "SKILL.md",
                    with_link_count(information, 1),
                )
            )
            self.assertFalse(
                converter._has_single_file_link(
                    SKILL / "SKILL.md",
                    with_link_count(information, 2),
                )
            )

    def test_converter_uses_windows_native_metadata_for_every_integrity_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "skills" / "hive-hub"
            copied.parent.mkdir(parents=True)
            shutil.copytree(SKILL, copied)
            sources = root / "sources"
            sources.mkdir()
            copied_source = sources / "hive-hub.json"
            shutil.copy2(SOURCE, copied_source)
            original_lstat = converter.os.lstat
            original_tree = converter._skill_lock_tree
            native_paths: list[Path] = []

            def zero_lstat(path):
                return with_link_count(original_lstat(path), 0)

            def zero_tree(skill_dir):
                for relative, information, kind in original_tree(skill_dir):
                    if kind == "file":
                        information = with_link_count(information, 0)
                    yield relative, information, kind

            def native_metadata(path):
                native_paths.append(Path(path))
                return 1, 0

            with (
                mock.patch.object(converter, "_is_windows", return_value=True),
                mock.patch.object(
                    converter,
                    "_windows_file_metadata",
                    side_effect=native_metadata,
                ),
                mock.patch.object(converter.os, "lstat", side_effect=zero_lstat),
                mock.patch.object(
                    converter,
                    "_skill_lock_tree",
                    side_effect=zero_tree,
                ),
            ):
                self.assertEqual(converter.verify(copied), [])
                verify_paths = list(native_paths)
                native_paths.clear()
                self.assertEqual(
                    converter._source_manifest_problems(root, copied_source),
                    [],
                )
                source_paths = list(native_paths)
                native_paths.clear()
                self.assertEqual(
                    converter._render_skill_lock(copied / "agent.lock"),
                    (copied / "agent.lock").read_text(encoding="utf-8"),
                )
                render_paths = list(native_paths)

            source = json.loads(copied_source.read_text(encoding="utf-8"))
            skill_paths = {
                copied / entry["path"] for entry in source["files"]
            }
            lock_path = copied / "agent.lock"
            self.assertGreaterEqual(verify_paths.count(lock_path), 1)
            self.assertTrue(
                all(
                    verify_paths.count(path) >= 2
                    for path in skill_paths - {lock_path}
                ),
                sorted(path.as_posix() for path in verify_paths),
            )
            self.assertGreaterEqual(source_paths.count(copied_source), 1)
            self.assertTrue(
                all(source_paths.count(path) >= 2 for path in skill_paths),
                sorted(path.as_posix() for path in source_paths),
            )
            self.assertTrue(
                all(render_paths.count(path) >= 2 for path in skill_paths),
                sorted(path.as_posix() for path in render_paths),
            )

            runner = copied / "scripts" / "run.py"

            def unsafe_runner(path):
                if Path(path) == runner:
                    return 2, 0
                return 1, 0

            with (
                mock.patch.object(converter, "_is_windows", return_value=True),
                mock.patch.object(
                    converter,
                    "_windows_file_metadata",
                    side_effect=unsafe_runner,
                ),
            ):
                self.assertTrue(
                    any(
                        "scripts/run.py" in problem
                        and "exactly one filesystem link" in problem
                        for problem in converter.verify(copied)
                    )
                )
                self.assertTrue(
                    any(
                        "scripts/run.py" in problem
                        and "exactly one filesystem link" in problem
                        for problem in converter._source_manifest_problems(
                            root,
                            copied_source,
                        )
                    )
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "exactly one filesystem link",
                ):
                    converter._render_skill_lock(copied / "agent.lock")

            def unavailable_runner(path):
                if Path(path) == runner:
                    raise OSError("GetFileInformationByHandle failed")
                return 1, 0

            with (
                mock.patch.object(converter, "_is_windows", return_value=True),
                mock.patch.object(
                    converter,
                    "_windows_file_metadata",
                    side_effect=unavailable_runner,
                ),
            ):
                self.assertTrue(
                    any(
                        "scripts/run.py" in problem
                        and "exactly one filesystem link" in problem
                        for problem in converter.verify(copied)
                    )
                )
                self.assertTrue(
                    any(
                        "scripts/run.py" in problem
                        and "exactly one filesystem link" in problem
                        for problem in converter._source_manifest_problems(
                            root,
                            copied_source,
                        )
                    )
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "exactly one filesystem link",
                ):
                    converter._render_skill_lock(copied / "agent.lock")

    def test_converter_and_skill_reject_real_hardlinks_everywhere(self):
        if not hasattr(os, "link"):
            self.skipTest("hardlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "skills" / "hive-hub"
            copied.parent.mkdir(parents=True)
            shutil.copytree(SKILL, copied)
            sources = root / "sources"
            sources.mkdir()
            copied_source = sources / "hive-hub.json"
            shutil.copy2(SOURCE, copied_source)

            target = copied / "scripts" / "run.py"
            target_alias = root / "shared-run.py"
            try:
                os.link(target, target_alias)
            except OSError as exc:
                self.skipTest(f"hardlinks unavailable: {exc}")
            self.assertGreaterEqual(target.stat().st_nlink, 2)
            lock_problems = converter.verify(copied)
            self.assertTrue(
                any("exactly one filesystem link" in item for item in lock_problems),
                lock_problems,
            )
            source_problems = converter._source_manifest_problems(
                root,
                copied_source,
            )
            self.assertTrue(
                any("scripts/run.py" in item for item in source_problems),
                source_problems,
            )
            with self.assertRaisesRegex(ValueError, "exactly one filesystem link"):
                converter._render_skill_lock(copied / "agent.lock")
            verified = run_skill(copied, "verify", cwd=root)
            self.assertEqual(verified.returncode, 2)
            self.assertEqual(result_of(verified)["status"], "blocked")
            target_alias.unlink()

            lock_path = copied / "agent.lock"
            lock_alias = root / "shared-agent.lock"
            os.link(lock_path, lock_alias)
            self.assertGreaterEqual(lock_path.stat().st_nlink, 2)
            self.assertTrue(
                any(
                    "must have exactly one filesystem link" in item
                    for item in converter.verify(copied)
                )
            )
            with self.assertRaisesRegex(ValueError, "exactly one filesystem link"):
                converter._render_skill_lock(lock_path)
            lock_alias.unlink()

            source_alias = root / "shared-source.json"
            os.link(copied_source, source_alias)
            self.assertGreaterEqual(copied_source.stat().st_nlink, 2)
            self.assertTrue(
                any(
                    "must have exactly one filesystem link" in item
                    for item in converter._source_manifest_problems(
                        root,
                        copied_source,
                    )
                )
            )

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
            "exactly one filesystem link",
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
