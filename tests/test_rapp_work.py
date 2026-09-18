"""The multi-host RAPP Work adapter stays locked, plan-first, and inert."""

from __future__ import annotations

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
from typing import ClassVar
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "rapp-work"
FIXTURE = ROOT / "tests" / "fixtures" / "rapp-work"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    original_path = list(sys.path)
    original_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = original_path
        sys.dont_write_bytecode = original_bytecode
    return module


runner = load_module("rapp_work_runner", SKILL / "scripts" / "run.py")
converter = load_module(
    "rapp_skills_for_rapp_work",
    ROOT / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args: str, cwd: Path, env: dict[str, str] | None = None):
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


class AdapterFixture:
    def __init__(self, root: Path):
        self.root = root
        self.skill = root / "rapp-work"
        self.sdk = root / "sdk"
        self.rapp1 = root / "rapp-1"
        self.workspace = root / "workspace"
        self.source = root / "source"
        shutil.copytree(SKILL, self.skill)
        shutil.copytree(FIXTURE / "sdk", self.sdk)
        shutil.copytree(FIXTURE / "rapp-1", self.rapp1)
        self.source.mkdir()
        self.rapp1_commit = self._commit(self.rapp1)
        (self.sdk / "RAPP1_PIN.json").write_text(
            json.dumps(
                {
                    "schema": "rapp-work-parent-pin/1",
                    "protocol": "rapp/1",
                    "repository": "https://github.com/kody-w/rapp-1",
                    "commit": self.rapp1_commit,
                    "spec_path": "SPEC.md",
                    "spec_sha256": sha(self.rapp1 / "SPEC.md"),
                    "reference_path": "rapp.py",
                    "reference_sha256": sha(self.rapp1 / "rapp.py"),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.sdk_commit = self._commit(self.sdk)
        self.static = FIXTURE / "static" / "index.json"
        lock_path = self.skill / "agent.lock"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["protocol"]["commit"] = self.rapp1_commit
        lock["protocol"]["sha256"] = sha(self.rapp1 / "SPEC.md")
        lock["protocol"]["reference_sha256"] = sha(self.rapp1 / "rapp.py")
        lock["sdk"]["commit"] = self.sdk_commit
        lock["sdk"]["sha256"] = sha(
            self.sdk / "src" / "rapp_work" / "cli.py"
        )
        lock["static"]["commit"] = "3" * 40
        lock["static"]["api_base"] = runner._static_api_base("3" * 40)
        lock["static"]["sha256"] = sha(self.static)
        lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")

    def _commit(self, path: Path) -> str:
        subprocess.run(["git", "init", "-q", str(path)], check=True)
        subprocess.run(
            ["git", "-C", str(path), "config", "core.autocrlf", "false"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(path), "config", "core.eol", "lf"],
            check=True,
        )
        subprocess.run(["git", "-C", str(path), "add", "."], check=True)
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_AUTHOR_NAME": "RAPP Work Fixture",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "RAPP Work Fixture",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
                "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
            }
        )
        subprocess.run(
            ["git", "-C", str(path), "commit", "-q", "-m", "fixture"],
            check=True,
            env=environment,
        )
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()

    def commit_sdk_change(self, message: str = "fixture update") -> str:
        subprocess.run(["git", "-C", str(self.sdk), "add", "."], check=True)
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_AUTHOR_NAME": "RAPP Work Fixture",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "RAPP Work Fixture",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": "2026-01-02T00:00:00Z",
                "GIT_COMMITTER_DATE": "2026-01-02T00:00:00Z",
            }
        )
        subprocess.run(
            ["git", "-C", str(self.sdk), "commit", "-q", "-m", message],
            check=True,
            env=environment,
        )
        self.sdk_commit = subprocess.check_output(
            ["git", "-C", str(self.sdk), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        lock_path = self.skill / "agent.lock"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["sdk"]["commit"] = self.sdk_commit
        lock["sdk"]["sha256"] = sha(
            self.sdk / "src" / "rapp_work" / "cli.py"
        )
        lock_path.write_text(
            json.dumps(lock, indent=2) + "\n",
            encoding="utf-8",
        )
        return self.sdk_commit

    def run(self, operation: str | None = None, *extra: str, env=None):
        arguments = [str(self.skill / "scripts" / "run.py")]
        if operation is not None:
            arguments.append(operation)
        if operation == "migrate":
            arguments.extend(
                ["--source", str(self.source), "--target", str(self.workspace)]
            )
        else:
            arguments.extend(["--root", str(self.workspace)])
        if operation == "scaffold":
            arguments.extend(
                [
                    "--kind",
                    "workspace",
                    "--owner-label",
                    "fixture-owner",
                    "--slug",
                    "fixture-workspace",
                    "--world-id",
                    "fixture-world",
                ]
            )
        arguments.extend(
            [
                "--sdk-path",
                str(self.sdk),
                "--rapp1-path",
                str(self.rapp1),
                *extra,
            ]
        )
        return command(*arguments, cwd=self.root, env=env)


class SkillPackageTests(unittest.TestCase):
    def test_standard_six_field_skill_and_lock_are_current(self):
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
        self.assertEqual(converter.manifests(ROOT, check=True), [])

    def test_lock_has_exact_final_upstream_pins(self):
        lock = json.loads((SKILL / "agent.lock").read_text(encoding="utf-8"))
        self.assertEqual(lock["schema"], "rapp-skill-lock/1")
        self.assertEqual(lock["name"], "rapp-work")
        self.assertEqual(
            {
                "name": "rapp/1",
                "repository": "https://github.com/kody-w/rapp-1",
                "commit": "591e014ad39e223b00ab343ae26e5d9a867ebeee",
                "path": "SPEC.md",
                "sha256": (
                    "348e7d5baa94aaf2ce4c5354f3cb261f"
                    "389298a04af65e271a686d3b62f7c384"
                ),
                "reference_path": "rapp.py",
                "reference_sha256": (
                    "1a04362b02f14c1e37b70c6b4f72d79"
                    "e92df1cc9c2b5b394e8e1b141fc0b6050"
                ),
            },
            lock["protocol"],
        )
        self.assertEqual(
            {
                "name": "rapp-work-sdk/1",
                "repository": "https://github.com/kody-w/rapp-work",
                "commit": "29ead23b21645f8d7682ee00414930ffa9ce0ca6",
                "entrypoint": "src/rapp_work/cli.py",
                "sha256": (
                    "be5a5c5a07119cda5544008a1b9b9832"
                    "a74c3277c6b6f466039f66613e818a0d"
                ),
                "source_path": "src",
                "rapp1_pin": "RAPP1_PIN.json",
                "interface": "python-sdk-json-stdin-v1",
            },
            lock["sdk"],
        )
        self.assertEqual(
            {
                "name": "rapp-work-static-api/1",
                "repository": "https://github.com/kody-w/rapp-static-apis",
                "commit": "30abe938520fa310123c179b1da593fd5a97ddfc",
                "api_base": (
                    "https://raw.githubusercontent.com/kody-w/"
                    "rapp-static-apis/"
                    "30abe938520fa310123c179b1da593fd5a97ddfc/"
                    "api/rapp-work/v1"
                ),
                "index": "index.json",
                "sha256": (
                    "c1957907d684fc19af47d9954a24bcc02"
                    "16c83507fb67f0ee1b585978b412121"
                ),
            },
            lock["static"],
        )
        self.assertEqual(runner._lock_pin_state(lock), "final")
        for entry in lock["files"]:
            self.assertEqual(sha(SKILL / entry["path"]), entry["sha256"])

    def test_lock_state_is_atomic_and_static_url_is_commit_derived(self):
        self.assertEqual(runner._lock_pin_state(runner.load_lock(SKILL)), "final")
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            final_lock = runner.load_lock(fixture.skill)
            self.assertEqual(runner._lock_pin_state(final_lock), "final")
            self.assertEqual(
                final_lock["static"]["api_base"],
                runner._static_api_base(final_lock["static"]["commit"]),
            )

            lock_path = fixture.skill / "agent.lock"
            mixed = json.loads(lock_path.read_text(encoding="utf-8"))
            mixed["sdk"]["commit"] = "PENDING_RAPP_WORK_SDK_COMMIT"
            lock_path.write_text(
                json.dumps(mixed, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                runner.LockError,
                "entirely pending or entirely finalized",
            ):
                runner.load_lock(fixture.skill)

            mixed["sdk"]["commit"] = fixture.sdk_commit
            mixed["static"]["api_base"] = (
                "https://raw.githubusercontent.com/kody-w/"
                "rapp-static-apis/main/api/rapp-work/v1"
            )
            lock_path.write_text(
                json.dumps(mixed, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                runner.LockError,
                "derived from the exact static commit",
            ):
                runner.load_lock(fixture.skill)

    def test_sync_repairs_a_changed_locked_hash_and_check_detects_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "rapp-work"
            shutil.copytree(SKILL, copied)
            runner_path = copied / "scripts" / "run.py"
            runner_path.write_text(
                runner_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            problems = converter.verify(copied)
            self.assertTrue(any("locked path" in item for item in problems))
            rendered = json.loads(
                converter._render_skill_lock(copied / "agent.lock")
            )
            locked = {
                item["path"]: item["sha256"] for item in rendered["files"]
            }
            self.assertEqual(locked["scripts/run.py"], sha(runner_path))

    def test_lock_generator_refuses_traversal_and_symlinked_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "rapp-work"
            shutil.copytree(SKILL, copied)
            lock_path = copied / "agent.lock"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["files"][0]["path"] = "../outside"
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            self.assertTrue(
                any("traverse" in item for item in converter.verify(copied))
            )
            with self.assertRaises(ValueError):
                converter._render_skill_lock(lock_path)

        if not hasattr(os, "symlink"):
            return
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "rapp-work"
            shutil.copytree(SKILL, copied)
            target = copied / "scripts" / "run.py"
            real = copied / "scripts" / "real.py"
            target.rename(real)
            try:
                target.symlink_to(real.name)
            except OSError:
                return
            self.assertTrue(
                any("non-symlink" in item for item in converter.verify(copied))
            )
            with self.assertRaises(ValueError):
                converter._render_skill_lock(copied / "agent.lock")

    def test_lock_rejects_unlisted_importable_files_and_external_hardlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            shutil.copytree(SKILL, copied)
            unlisted = copied / "scripts" / "argparse.py"
            unlisted.write_text("raise RuntimeError('must stay inert')\n", encoding="utf-8")
            problems = converter.verify(copied)
            self.assertTrue(
                any("does not list executable or importable" in item for item in problems),
                problems,
            )
            with self.assertRaisesRegex(
                runner.LockError,
                "does not list executable or importable",
            ):
                runner.load_lock(copied)
            with self.assertRaisesRegex(ValueError, "does not list executable"):
                converter._render_skill_lock(copied / "agent.lock")

        if not hasattr(os, "link"):
            return
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            shutil.copytree(SKILL, copied)
            target = copied / "scripts" / "run.py"
            outside = root / "outside-run.py"
            try:
                os.link(target, outside)
            except OSError as exc:
                self.skipTest(str(exc))
            problems = converter.verify(copied)
            self.assertTrue(
                any("exactly one filesystem link" in item for item in problems),
                problems,
            )
            with self.assertRaisesRegex(
                runner.LockError,
                "exactly one filesystem link",
            ):
                runner.load_lock(copied)
            with self.assertRaisesRegex(ValueError, "exactly one filesystem link"):
                converter._render_skill_lock(copied / "agent.lock")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            shutil.copytree(SKILL, copied)
            note = copied / "notes.txt"
            note.write_text("inert but still one file\n", encoding="utf-8")
            outside = root / "outside-notes.txt"
            try:
                os.link(note, outside)
            except OSError as exc:
                self.skipTest(str(exc))
            self.assertGreaterEqual(note.stat().st_nlink, 2)
            problems = converter.verify(copied)
            self.assertTrue(
                any("exactly one filesystem link" in item for item in problems),
                problems,
            )
            with self.assertRaisesRegex(ValueError, "exactly one filesystem link"):
                converter._render_skill_lock(copied / "agent.lock")

    def test_host_agent_projection_is_generated(self):
        expected = converter.render_manifests(ROOT)[
            ".github/agents/rapp-work.agent.md"
        ]
        actual = converter.read_text(
            ROOT / ".github" / "agents" / "rapp-work.agent.md"
        )
        self.assertEqual(actual, expected)
        self.assertIn("exact plan and digest", actual)

    def test_runner_contains_no_clone_install_or_shell_execution(self):
        source = (SKILL / "scripts" / "run.py").read_text(encoding="utf-8")
        for forbidden in (
            "git clone",
            "pip install",
            "npm install",
            "shell=True",
            "os.system(",
            "eval(",
            "exec(",
        ):
            self.assertNotIn(forbidden, source)


class BootstrapIsolationTests(unittest.TestCase):
    @staticmethod
    def malicious_argparse(marker: Path) -> str:
        return (
            f"open({str(marker)!r}, 'w', encoding='utf-8').write('executed')\n"
            "raise RuntimeError('malicious argparse executed')\n"
        )

    def test_caller_pythonpath_and_working_directory_have_zero_import_effect(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            injection = root.joinpath(*(["injection"] * 9))
            marker = root / "executed"
            shutil.copytree(SKILL, copied)
            injection.mkdir(parents=True)
            (injection / "argparse.py").write_text(
                self.malicious_argparse(marker),
                encoding="utf-8",
            )
            disguised = str(
                Path(sys._stdlib_dir)
                / os.path.relpath(injection, Path(sys._stdlib_dir))
            )
            for pythonpath in (str(injection), disguised):
                with self.subTest(pythonpath=pythonpath):
                    environment = os.environ.copy()
                    environment["PYTHONPATH"] = pythonpath
                    result = command(
                        str(copied / "scripts" / "run.py"),
                        "status",
                        cwd=injection,
                        env=environment,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        json.loads(result.stdout)["status"],
                        "unresolved",
                    )
                    self.assertFalse(marker.exists())

    def test_unlisted_argparse_beside_runner_is_inert_then_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            marker = root / "executed"
            shutil.copytree(SKILL, copied)
            (copied / "scripts" / "argparse.py").write_text(
                self.malicious_argparse(marker),
                encoding="utf-8",
            )
            result = command(
                str(copied / "scripts" / "run.py"),
                "status",
                cwd=root,
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "refused")
            self.assertEqual(value["error"]["code"], "lock-error")
            self.assertIn(
                "does not list executable or importable",
                value["error"]["message"],
            )
            self.assertFalse(marker.exists())


class ResolutionTests(unittest.TestCase):
    def test_explicit_values_precede_environment_and_local_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            explicit = root / "explicit"
            environment = root / "environment"
            local = root / "rapp-work-sdk"
            for path in (explicit, environment, local):
                path.mkdir()
            with mock.patch.dict(
                os.environ, {"RAPP_WORK_SDK_PATH": str(environment)}, clear=False
            ):
                resolved, source = runner.resolve_sdk(str(explicit), root)
                self.assertEqual(
                    (resolved, source),
                    (Path(os.path.realpath(explicit)), "explicit"),
                )
                resolved, source = runner.resolve_sdk(None, root)
                self.assertEqual(
                    (resolved, source),
                    (
                        Path(os.path.realpath(environment)),
                        "environment:RAPP_WORK_SDK_PATH",
                    ),
                )
            with mock.patch.dict(os.environ, {}, clear=True):
                resolved, source = runner.resolve_sdk(None, root)
                self.assertEqual(
                    (resolved, source), (Path(os.path.realpath(local)), "local")
                )

    def test_invalid_explicit_value_never_falls_back(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment = root / "environment"
            environment.mkdir()
            with mock.patch.dict(
                os.environ, {"RAPP_WORK_SDK_PATH": str(environment)}, clear=False
            ):
                with self.assertRaises(runner.SafetyError):
                    runner.resolve_sdk("../escape", root)
                with self.assertRaises(runner.SafetyError):
                    runner.resolve_sdk(str(root / "missing"), root)
            lock = json.loads((SKILL / "agent.lock").read_text(encoding="utf-8"))
            with mock.patch.dict(
                os.environ,
                {"RAPP_WORK_API_BASE": "https://environment.invalid/v1"},
                clear=False,
            ), self.assertRaises(runner.ResolutionError):
                runner.resolve_api("http://explicit.invalid/v1", lock)

    def test_api_and_rapp1_use_the_same_explicit_first_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            lock = json.loads(
                (fixture.skill / "agent.lock").read_text(encoding="utf-8")
            )
            expected = runner._static_api_base(lock["static"]["commit"])
            with mock.patch.dict(
                os.environ,
                {"RAPP_WORK_API_BASE": expected},
                clear=False,
            ):
                self.assertEqual(
                    runner.resolve_api(expected + "/", lock),
                    (expected, "explicit"),
                )
                self.assertEqual(
                    runner.resolve_api(None, lock),
                    (expected, "environment:RAPP_WORK_API_BASE"),
                )
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(
                    runner.resolve_api(None, lock),
                    (expected, "lock"),
                )
            with self.assertRaisesRegex(
                runner.ResolutionError,
                "derived from the exact static commit",
            ):
                runner.resolve_api("https://example.invalid/rapp-work/v1", lock)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            explicit = root / "explicit"
            environment = root / "environment"
            local = root / "rapp-1"
            for path in (explicit, environment, local):
                path.mkdir()
            with mock.patch.dict(
                os.environ, {"RAPP1_PATH": str(environment)}, clear=False
            ):
                self.assertEqual(
                    runner.resolve_rapp1(str(explicit), root, None),
                    (Path(os.path.realpath(explicit)), "explicit"),
                )
                self.assertEqual(
                    runner.resolve_rapp1(None, root, None),
                    (
                        Path(os.path.realpath(environment)),
                        "environment:RAPP1_PATH",
                    ),
                )
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(
                    runner.resolve_rapp1(None, root, None),
                    (Path(os.path.realpath(local)), "local"),
                )

    def test_symlinked_explicit_path_is_refused(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real"
            link = root / "link"
            real.mkdir()
            try:
                link.symlink_to(real, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            with self.assertRaises(runner.SafetyError):
                runner.resolve_sdk(str(link), root)


class PlanAndApplyTests(unittest.TestCase):
    def test_default_verify_and_status_with_final_release_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copied = root / "rapp-work"
            isolated = root.joinpath(*(["isolated"] * 9))
            shutil.copytree(SKILL, copied)
            isolated.mkdir(parents=True)
            environment = os.environ.copy()
            for name in (
                "PYTHONPATH",
                "RAPP_WORK_API_BASE",
                "RAPP_WORK_SDK_PATH",
                "RAPP1_PATH",
            ):
                environment.pop(name, None)

            status = command(
                str(copied / "scripts" / "run.py"),
                "status",
                cwd=isolated,
                env=environment,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            value = json.loads(status.stdout)
            self.assertEqual(value["status"], "unresolved")
            self.assertEqual(value["pending_pins"], [])
            self.assertEqual(
                value["resolution"]["api_base"],
                {
                    "value": (
                        "https://raw.githubusercontent.com/kody-w/"
                        "rapp-static-apis/"
                        "30abe938520fa310123c179b1da593fd5a97ddfc/"
                        "api/rapp-work/v1"
                    ),
                    "source": "lock",
                },
            )
            self.assertEqual(
                value["operations"],
                ["verify", "status", "discover", "scaffold", "update", "migrate"],
            )
            default = command(
                str(copied / "scripts" / "run.py"),
                cwd=isolated,
                env=environment,
            )
            self.assertEqual(default.returncode, 2)
            refusal = json.loads(default.stdout)
            self.assertEqual(refusal["operation"], "verify")
            self.assertEqual(refusal["error"]["code"], "resolution-error")

    def test_scaffold_is_plan_only_and_apply_needs_the_exact_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            planned = fixture.run("scaffold")
            self.assertEqual(planned.returncode, 0, planned.stderr)
            result = json.loads(planned.stdout)
            self.assertEqual(result["status"], "planned")
            self.assertFalse(fixture.workspace.exists())
            plan_digest = result["plan_digest"]

            wrong = fixture.run("scaffold", "--apply", "0" * 64)
            self.assertEqual(wrong.returncode, 2)
            self.assertEqual(json.loads(wrong.stdout)["status"], "refused")
            self.assertFalse(fixture.workspace.exists())

            applied = fixture.run("scaffold", "--apply", plan_digest)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual(json.loads(applied.stdout)["status"], "applied")
            self.assertTrue((fixture.workspace / "install.json").is_file())

    def test_update_replans_and_rejects_a_stale_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            first = json.loads(fixture.run("scaffold").stdout)
            self.assertEqual(
                fixture.run(
                    "scaffold", "--apply", first["plan_digest"]
                ).returncode,
                0,
            )
            update = json.loads(fixture.run("update").stdout)
            target = fixture.workspace / "install.json"
            target.write_text("owner change\n", encoding="utf-8")
            refused = fixture.run(
                "update", "--apply", update["plan_digest"]
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("does not equal current plan", refused.stdout)
            self.assertEqual(target.read_text(encoding="utf-8"), "owner change\n")

    def test_replace_is_atomic_and_preserves_the_previous_inode_bytes(self):
        if os.name == "nt":
            self.skipTest(
                "Windows does not guarantee replacement while another handle keeps the old inode open"
            )
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            scaffold = json.loads(fixture.run("scaffold").stdout)
            applied = fixture.run(
                "scaffold",
                "--apply",
                scaffold["plan_digest"],
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            target = fixture.workspace / "install.json"
            previous = target.read_bytes()
            with target.open("rb") as old_inode:
                update = json.loads(fixture.run("update").stdout)
                applied = fixture.run(
                    "update",
                    "--apply",
                    update["plan_digest"],
                )
                self.assertEqual(applied.returncode, 0, applied.stderr)
                old_inode.seek(0)
                self.assertEqual(old_inode.read(), previous)
            self.assertNotEqual(target.read_bytes(), previous)

    def test_multiply_linked_managed_file_is_refused_without_touching_external_file(self):
        if not hasattr(os, "link"):
            self.skipTest("hardlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            scaffold = json.loads(fixture.run("scaffold").stdout)
            self.assertEqual(
                fixture.run(
                    "scaffold",
                    "--apply",
                    scaffold["plan_digest"],
                ).returncode,
                0,
            )
            target = fixture.workspace / "install.json"
            external = root / "external-install.json"
            try:
                os.link(target, external)
            except OSError as exc:
                self.skipTest(str(exc))
            before = external.read_bytes()
            result = fixture.run("update")
            self.assertEqual(result.returncode, 2, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "refused")
            self.assertIn("exactly one filesystem link", value["error"]["message"])
            self.assertEqual(external.read_bytes(), before)
            self.assertEqual(target.read_bytes(), before)

    def test_nonempty_destination_is_refused_before_sdk_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            marker = fixture.workspace / "owner.txt"
            marker.write_text("keep", encoding="utf-8")
            result = fixture.run("migrate")
            self.assertEqual(result.returncode, 2)
            self.assertIn("must be absent or empty", result.stdout)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_traversal_external_effects_and_conflicts_are_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            workspace.mkdir()
            paths = {
                "root": workspace,
                "source": workspace,
                "target": workspace,
            }
            base = {
                "operation": "update",
                "network": False,
                "target": str(workspace),
                "actions": [],
            }
            with self.assertRaises(runner.SafetyError):
                runner._validate_plan(
                    {
                        **base,
                        "actions": [
                            {
                                "operation": "create",
                                "path": "../escape",
                                "bytes": 1,
                                "content_base64": "eA==",
                                "expected_sha256": None,
                                "sha256": hashlib.sha256(b"x").hexdigest(),
                            }
                        ],
                    },
                    "update",
                    paths,
                    before_apply=False,
                )
            with self.assertRaises(runner.SafetyError):
                runner._validate_plan(
                    {**base, "external_effects": ["publish"]},
                    "update",
                    paths,
                    before_apply=False,
                )
            managed = workspace / "install.json"
            managed.write_text("owner bytes", encoding="utf-8")
            with self.assertRaises(runner.SafetyError):
                runner._validate_plan(
                    {
                        **base,
                        "actions": [
                            {
                                "operation": "replace",
                                "path": "install.json",
                                "bytes": 1,
                                "content_base64": "eA==",
                                "expected_sha256": "0" * 64,
                                "sha256": hashlib.sha256(b"x").hexdigest(),
                            }
                        ],
                    },
                    "update",
                    paths,
                    before_apply=False,
                )

    def test_symlinked_destination_is_refused(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            outside = Path(temporary) / "outside"
            outside.mkdir()
            try:
                fixture.workspace.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            result = fixture.run("scaffold")
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink", result.stdout)
            self.assertEqual(list(outside.iterdir()), [])

    def test_sdk_receives_no_caller_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            environment = os.environ.copy()
            environment.update(
                {
                    "GITHUB_TOKEN": "do-not-forward",
                    "AWS_SECRET_ACCESS_KEY": "do-not-forward",
                    "PYTHONPATH": "do-not-forward",
                    "SSH_AUTH_SOCK": "do-not-forward",
                }
            )
            result = fixture.run("verify", env=environment)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            sdk_result = value["result"]["result"]
            self.assertTrue(sdk_result["environment_clean"])
            self.assertTrue(sdk_result["import_path_clean"])
            self.assertFalse(sdk_result["network"])

    def test_dirty_sdk_checkout_is_never_executed(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            cli = fixture.sdk / "src" / "rapp_work" / "cli.py"
            cli.write_text("raise RuntimeError('must not run')\n", encoding="utf-8")
            result = fixture.run("verify")
            self.assertEqual(result.returncode, 2)
            self.assertIn("checkout must be clean", result.stdout)
            self.assertNotIn("must not run", result.stdout)

    def test_hidden_sdk_index_flags_are_rejected_before_module_execution(self):
        relative = "src/rapp_work/api.py"
        for option in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(option=option), tempfile.TemporaryDirectory() as temporary:
                fixture = AdapterFixture(Path(temporary))
                fixture.workspace.mkdir()
                marker = fixture.root / "executed"
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(fixture.sdk),
                        "update-index",
                        option,
                        relative,
                    ],
                    check=True,
                )
                (fixture.sdk / relative).write_text(
                    f"open({str(marker)!r}, 'w').write('executed')\n",
                    encoding="utf-8",
                )
                self.assertEqual(
                    subprocess.check_output(
                        [
                            "git",
                            "-C",
                            str(fixture.sdk),
                            "status",
                            "--porcelain=v1",
                            "--untracked-files=all",
                        ],
                        text=True,
                    ),
                    "",
                )
                result = fixture.run("verify")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("hidden or non-standard index state", result.stdout)
                self.assertFalse(marker.exists())

    def test_sdk_replacement_objects_are_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            marker = fixture.root / "executed"
            relative = "src/rapp_work/api.py"
            original = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(fixture.sdk),
                    "rev-parse",
                    f"HEAD:{relative}",
                ],
                text=True,
            ).strip()
            replacement = subprocess.run(
                ["git", "-C", str(fixture.sdk), "hash-object", "-w", "--stdin"],
                input=f"open({str(marker)!r}, 'w').write('executed')\n",
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(fixture.sdk),
                    "replace",
                    original,
                    replacement,
                ],
                check=True,
            )
            result = fixture.run("verify")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("replacement objects", result.stdout)
            self.assertFalse(marker.exists())

    def test_ignored_sdk_executable_code_is_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            marker = fixture.root / "executed"
            relative = Path("src/rapp_work/ignored.py")
            exclude = fixture.sdk / ".git" / "info" / "exclude"
            with exclude.open("a", encoding="utf-8") as stream:
                stream.write("\n/src/rapp_work/ignored.py\n")
            (fixture.sdk / relative).write_text(
                f"open({str(marker)!r}, 'w').write('executed')\n",
                encoding="utf-8",
            )
            self.assertEqual(
                subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(fixture.sdk),
                        "status",
                        "--porcelain=v1",
                        "--untracked-files=all",
                    ],
                    text=True,
                ),
                "",
            )
            result = fixture.run("verify")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("unpinned executable or importable file", result.stdout)
            self.assertFalse(marker.exists())

    def test_sdk_parent_pin_must_equal_the_explicit_rapp1_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            lock = json.loads(
                (fixture.skill / "agent.lock").read_text(encoding="utf-8")
            )
            lock["protocol"]["commit"] = "0" * 40
            with self.assertRaises(runner.ResolutionError):
                runner._verify_sdk_parent_pin(
                    fixture.sdk, lock["sdk"], lock["protocol"]
                )

    def test_local_discovery_uses_the_pinned_sdk_without_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            result = fixture.run(
                "discover", "--discover-root", str(fixture.source)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "inert-local-metadata")
            self.assertFalse(value["executed"])
            self.assertFalse(value["result"]["result"]["executed"])

    def test_unknown_external_operation_returns_json_without_echoing_values(self):
        result = command(
            str(SKILL / "scripts" / "run.py"),
            "publish",
            "--token",
            "do-not-echo",
            cwd=SKILL,
        )
        self.assertEqual(result.returncode, 2)
        value = json.loads(result.stdout)
        self.assertEqual(value["status"], "refused")
        self.assertNotIn("do-not-echo", result.stdout + result.stderr)


class ProcessFailureTests(unittest.TestCase):
    EXPECTED_ERROR: ClassVar[dict[str, str]] = {
        "code": "local-execution-error",
        "message": runner.LOCAL_PROCESS_ERROR,
    }

    def test_git_timeout_and_sdk_launch_error_use_one_internal_refusal(self):
        with mock.patch.object(
            runner.shutil,
            "which",
            return_value="/usr/bin/git",
        ), mock.patch.object(
            runner.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["git"], 15),
        ), self.assertRaisesRegex(
            runner.ExecutionError,
            f"^{re.escape(runner.LOCAL_PROCESS_ERROR)}$",
        ):
            runner._git(Path("."), "status")

        with mock.patch.object(
            runner,
            "_sdk_command",
            return_value=[sys.executable],
        ), mock.patch.object(
            runner.subprocess,
            "run",
            side_effect=OSError("launch failed"),
        ), self.assertRaisesRegex(
            runner.ExecutionError,
            f"^{re.escape(runner.LOCAL_PROCESS_ERROR)}$",
        ):
            runner.invoke_sdk(
                Path("."),
                {},
                {"operation": "verify"},
                1,
            )

    def test_sdk_timeout_is_one_json_refusal_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = AdapterFixture(Path(temporary))
            fixture.workspace.mkdir()
            api = fixture.sdk / "src" / "rapp_work" / "api.py"
            source = api.read_text(encoding="utf-8").replace(
                "from __future__ import annotations\n",
                (
                    "from __future__ import annotations\n"
                    "import time\n"
                    "time.sleep(5)\n"
                ),
                1,
            )
            api.write_text(source, encoding="utf-8")
            fixture.commit_sdk_change("slow fixture")
            result = fixture.run("verify", "--timeout", "1")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "refused")
            self.assertEqual(value["error"], self.EXPECTED_ERROR)
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_git_launch_oserror_is_same_json_refusal_without_traceback(self):
        if os.name == "nt":
            self.skipTest("invalid executable launch differs on Windows")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = AdapterFixture(root)
            fixture.workspace.mkdir()
            binaries = root / "bin"
            binaries.mkdir()
            fake_git = binaries / "git"
            fake_git.write_text("not an executable image\n", encoding="utf-8")
            fake_git.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = str(binaries)
            result = fixture.run("verify", env=environment)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "refused")
            self.assertEqual(value["error"], self.EXPECTED_ERROR)
            self.assertNotIn("Traceback", result.stdout + result.stderr)


class DiscoveryTests(unittest.TestCase):
    class Response:
        def __init__(self, data: bytes):
            self.data = data
            self.headers = {"Content-Length": str(len(data))}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, limit: int):
            return self.data[:limit]

    class Opener:
        def __init__(self, response):
            self.response = response

        def open(self, request, timeout):
            return self.response

    def test_downloaded_commands_and_code_locations_remain_inert(self):
        raw = (FIXTURE / "static" / "index.json").read_bytes()
        lock = json.loads((SKILL / "agent.lock").read_text(encoding="utf-8"))
        lock["static"]["commit"] = "3" * 40
        lock["static"]["api_base"] = runner._static_api_base("3" * 40)
        lock["static"]["sha256"] = hashlib.sha256(raw).hexdigest()
        api_base = lock["static"]["api_base"]
        with mock.patch.object(
            runner,
            "build_opener",
            return_value=self.Opener(self.Response(raw)),
        ), mock.patch.object(runner.subprocess, "run") as executed:
            value = runner._fetch_discovery(
                api_base, lock, 5
            )
        executed.assert_not_called()
        self.assertFalse(value["executed"])
        self.assertEqual(
            value["document"]["entrypoints"]["sdk"]["entrypoint"],
            "downloaded.py",
        )

    def test_duplicate_members_and_oversized_documents_are_refused(self):
        with self.assertRaises(ValueError):
            runner.parse_json_object(b'{"same":1,"same":2}', "response")
        with self.assertRaises(ValueError):
            runner.parse_json_object(
                b'{"value":"' + b"x" * runner.MAX_JSON_BYTES + b'"}',
                "response",
            )

    def test_static_hash_mismatch_is_refused_without_execution(self):
        raw = (FIXTURE / "static" / "index.json").read_bytes()
        lock = json.loads((SKILL / "agent.lock").read_text(encoding="utf-8"))
        lock["static"]["commit"] = "3" * 40
        lock["static"]["api_base"] = runner._static_api_base("3" * 40)
        lock["static"]["sha256"] = "0" * 64
        api_base = lock["static"]["api_base"]
        with mock.patch.object(
            runner,
            "build_opener",
            return_value=self.Opener(self.Response(raw)),
        ), mock.patch.object(
            runner.subprocess, "run"
        ) as executed, self.assertRaises(runner.DiscoveryError):
            runner._fetch_discovery(api_base, lock, 5)
        executed.assert_not_called()


if __name__ == "__main__":
    unittest.main()
