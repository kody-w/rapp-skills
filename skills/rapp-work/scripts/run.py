#!/usr/bin/env python3
"""Locked, plan-first adapter for the canonical RAPP Work SDK/CLI."""

from __future__ import annotations

import sys as _bootstrap_sys


def _sanitize_bootstrap_path() -> None:
    """Keep only this interpreter's standard library before importing from disk."""
    stdlib = getattr(_bootstrap_sys, "_stdlib_dir", "")
    if not isinstance(stdlib, str) or not stdlib:
        if not _bootstrap_sys.flags.isolated:
            raise RuntimeError("run this adapter with Python isolated mode (-I)")
        return
    normalized_stdlib = stdlib.replace("\\", "/").rstrip("/")
    stdlib_parent = normalized_stdlib.rsplit("/", 1)[0]
    folded_stdlib = normalized_stdlib.casefold()
    folded_parent = stdlib_parent.casefold()
    safe: list[str] = []
    for entry in _bootstrap_sys.path:
        if not isinstance(entry, str) or not entry:
            continue
        normalized = entry.replace("\\", "/").rstrip("/")
        if any(part in {".", ".."} for part in normalized.split("/")):
            continue
        folded = normalized.casefold()
        if "/site-packages" in folded or "/dist-packages" in folded:
            continue
        in_stdlib = folded == folded_stdlib or folded.startswith(
            folded_stdlib + "/"
        )
        in_dlls = folded == folded_parent + "/dlls" or folded.startswith(
            folded_parent + "/dlls/"
        )
        stdlib_zip = (
            folded.startswith(folded_parent + "/python")
            and folded.endswith(".zip")
            and "/" not in folded[len(folded_parent) + 1 :]
        )
        if in_stdlib or in_dlls or stdlib_zip:
            safe.append(entry)
    if not safe:
        raise RuntimeError("Python standard-library path could not be isolated")
    _bootstrap_sys.path[:] = safe


_sanitize_bootstrap_path()
del _sanitize_bootstrap_path

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SKILL_ROOT = Path(__file__).resolve().parents[1]
LOCK_SCHEMA = "rapp-skill-lock/1"
RESULT_SCHEMA = "rapp-work-run-result/1"
OPERATIONS = ("verify", "status", "discover", "scaffold", "update", "migrate")
MUTATIONS = {"scaffold", "update", "migrate"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SENSITIVE_RE = re.compile(
    r"(?:password|passwd|passphrase|secret|token|credential|private[-_]?key|"
    r"api[-_]?key|cookie|authorization)",
    re.IGNORECASE,
)
MAX_JSON_BYTES = 1_048_576
MAX_SDK_JSON_BYTES = 32 * 1024 * 1024
MAX_JSON_DEPTH = 32
MAX_JSON_NODES = 20_000
MAX_LOCK_TREE_ENTRIES = 10_000
MAX_SDK_SOURCE_ENTRIES = 10_000
MAX_SDK_SOURCE_BYTES = 256 * 1024 * 1024
LOCAL_PROCESS_ERROR = "required local process could not be completed safely"
STATIC_REPOSITORY = "https://github.com/kody-w/rapp-static-apis"
STATIC_RAW_ROOT = "https://raw.githubusercontent.com/kody-w/rapp-static-apis"
STATIC_API_PATH = "api/rapp-work/v1"
ACTIVE_SUFFIXES = frozenset(
    {
        ".bat",
        ".cmd",
        ".com",
        ".dll",
        ".dylib",
        ".egg",
        ".exe",
        ".fish",
        ".jar",
        ".node",
        ".php",
        ".phtml",
        ".pl",
        ".ps1",
        ".pth",
        ".py",
        ".pyc",
        ".pyd",
        ".pyo",
        ".pyw",
        ".rb",
        ".sh",
        ".so",
        ".wasm",
        ".whl",
        ".zip",
        ".zsh",
    }
)
PIN_FIELDS = (
    ("protocol", "commit", "PENDING_RAPP1_COMMIT"),
    ("protocol", "sha256", "PENDING_RAPP1_SPEC_SHA256"),
    (
        "protocol",
        "reference_sha256",
        "PENDING_RAPP1_REFERENCE_SHA256",
    ),
    ("sdk", "commit", "PENDING_RAPP_WORK_SDK_COMMIT"),
    ("sdk", "sha256", "PENDING_RAPP_WORK_SDK_CLI_SHA256"),
    ("static", "commit", "PENDING_RAPP_STATIC_API_COMMIT"),
    ("static", "sha256", "PENDING_RAPP_STATIC_INDEX_SHA256"),
    (
        "static",
        "api_base",
        f"{STATIC_RAW_ROOT}/PENDING_RAPP_STATIC_API_COMMIT/{STATIC_API_PATH}",
    ),
)
LOCK_SECTION_MEMBERS = {
    "protocol": {
        "name",
        "repository",
        "commit",
        "path",
        "sha256",
        "reference_path",
        "reference_sha256",
    },
    "sdk": {
        "name",
        "repository",
        "commit",
        "entrypoint",
        "sha256",
        "source_path",
        "rapp1_pin",
        "interface",
    },
    "static": {
        "name",
        "repository",
        "commit",
        "api_base",
        "index",
        "sha256",
    },
}
SDK_BOOTSTRAP = """\
import sys
sys.path.insert(0, sys.argv[1])
from rapp_work._json import canonical_text, strict_json_loads
from rapp_work.api import execute
request = strict_json_loads(sys.stdin.buffer.read(), where="adapter request")
if not isinstance(request, dict):
    raise ValueError("adapter request must be an object")
operation = request.pop("operation")
sys.stdout.write(canonical_text(execute(operation, request)) + "\\n")
"""


class RappWorkError(RuntimeError):
    code = "rapp-work-error"


class LockError(RappWorkError):
    code = "lock-error"


class ResolutionError(RappWorkError):
    code = "resolution-error"


class SafetyError(RappWorkError):
    code = "safety-error"


class SdkError(RappWorkError):
    code = "sdk-error"


class DiscoveryError(RappWorkError):
    code = "discovery-error"


class ExecutionError(RappWorkError):
    code = "local-execution-error"


class LockedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise SafetyError("invalid command arguments")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DiscoveryError(f"discovery redirect refused ({code})")


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SafetyError(f"value is not canonical JSON: {exc}") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def _bound_json(value: Any, maximum: int) -> None:
    nodes = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise ValueError("JSON document has too many values")
        if depth > MAX_JSON_DEPTH:
            raise ValueError("JSON document is too deeply nested")
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError(  # noqa: TRY004
                        "JSON object member is not a string"
                    )
                visit(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                visit(child, depth + 1)
        elif isinstance(item, str) and len(item.encode("utf-8")) > maximum:
            raise ValueError("JSON string is too large")

    visit(value, 0)


def parse_json_object(
    raw: bytes, label: str, maximum: int = MAX_JSON_BYTES
) -> dict[str, Any]:
    if len(raw) > maximum:
        raise ValueError(f"{label} exceeds {maximum} bytes")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")  # noqa: TRY004
    _bound_json(value, maximum)
    return value


def emit(value: dict[str, Any]) -> None:
    sys.stdout.buffer.write(canonical_bytes(value) + b"\n")


def _safe_relative(raw: str, label: str) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        raise SafetyError(f"{label} must be a non-empty relative POSIX path")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise SafetyError(f"{label} contains an absolute or traversing path")
    if ":" in raw:
        raise SafetyError(f"{label} contains an unsafe ':'")
    return Path(*pure.parts)


def _contains_traversal(raw: str) -> bool:
    return any(part == ".." for part in raw.replace("\\", "/").split("/"))


def _absolute_path(raw: str, base: Path, label: str) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise SafetyError(f"{label} must be a non-empty path")
    if _contains_traversal(raw):
        raise SafetyError(f"{label} contains path traversal")
    value = Path(raw).expanduser()
    if not value.is_absolute():
        value = base / value
    value = Path(os.path.abspath(value))
    _refuse_symlink_components(value, label)
    return Path(os.path.realpath(value))


def _refuse_symlink_components(path: Path, label: str) -> None:
    absolute = Path(os.path.abspath(path))
    anchor = Path(absolute.anchor)
    current = anchor
    parts = absolute.parts[1:] if absolute.anchor else absolute.parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            root_owned_alias = (
                current.parent == anchor
                and getattr(info, "st_uid", -1) == 0
                and Path(os.path.realpath(current)).is_dir()
            )
            if not root_owned_alias:
                raise SafetyError(f"{label} contains a symlink: {current}")
            continue
        if index < len(parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise SafetyError(f"{label} has a non-directory ancestor: {current}")


def _regular_file(
    path: Path, label: str, *, single_link: bool = False
) -> os.stat_result:
    _refuse_symlink_components(path, label)
    try:
        info = os.lstat(path)
    except FileNotFoundError as exc:
        raise SafetyError(f"{label} does not exist: {path}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise SafetyError(f"{label} is not a regular file: {path}")
    if single_link and info.st_nlink != 1:
        raise SafetyError(f"{label} must have exactly one filesystem link: {path}")
    return info


def _directory(path: Path, label: str) -> None:
    _refuse_symlink_components(path, label)
    try:
        info = os.lstat(path)
    except FileNotFoundError as exc:
        raise SafetyError(f"{label} does not exist: {path}") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise SafetyError(f"{label} is not a directory: {path}")


def _empty_destination(path: Path, label: str = "destination") -> None:
    _refuse_symlink_components(path, label)
    if not path.exists():
        return
    _directory(path, label)
    try:
        next(os.scandir(path))
    except StopIteration:
        return
    raise SafetyError(f"{label} must be absent or empty: {path}")


def _strict_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise LockError(f"{label} must be an exact lowercase SHA-256")
    return value


def _strict_commit(value: Any, label: str) -> str:
    if not isinstance(value, str) or COMMIT_RE.fullmatch(value) is None:
        raise LockError(f"{label} must be an exact 40-character commit")
    return value


def _pending(value: Any) -> bool:
    return isinstance(value, str) and "PENDING_" in value


def _static_api_base(commit: str) -> str:
    return f"{STATIC_RAW_ROOT}/{commit}/{STATIC_API_PATH}"


def _lock_pin_state(lock: dict[str, Any]) -> str:
    values = [
        lock.get(section, {}).get(field)
        if isinstance(lock.get(section), dict)
        else None
        for section, field, _ in PIN_FIELDS
    ]
    expected_pending = [placeholder for _, _, placeholder in PIN_FIELDS]
    if values == expected_pending:
        return "pending"
    if any(_pending(value) for value in values):
        raise LockError(
            "agent.lock release pins must be entirely pending or entirely finalized"
        )
    _strict_commit(lock["protocol"].get("commit"), "RAPP/1 pin")
    _strict_sha(lock["protocol"].get("sha256"), "RAPP/1 specification pin")
    _strict_sha(
        lock["protocol"].get("reference_sha256"),
        "RAPP/1 reference pin",
    )
    _strict_commit(lock["sdk"].get("commit"), "SDK pin")
    _strict_sha(lock["sdk"].get("sha256"), "SDK entrypoint pin")
    static_commit = _strict_commit(lock["static"].get("commit"), "static API pin")
    _strict_sha(lock["static"].get("sha256"), "static API index pin")
    expected_api_base = _static_api_base(static_commit)
    if lock["static"].get("api_base") != expected_api_base:
        raise LockError(
            "static.api_base must be derived from the exact static commit: "
            + expected_api_base
        )
    return "final"


def _pending_pins(lock: dict[str, Any]) -> list[str]:
    if _lock_pin_state(lock) != "pending":
        return []
    return sorted(f"{section}.{field}" for section, field, _ in PIN_FIELDS)


def _active_file(path: Path, mode: int) -> bool:
    return path.suffix.casefold() in ACTIVE_SUFFIXES or bool(
        mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    )


def _skill_tree(root: Path):
    stack: list[tuple[Path, Path]] = [(root, Path())]
    count = 0
    while stack:
        directory, relative_directory = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise LockError(f"cannot inspect locked skill folder: {directory}") from exc
        for entry in entries:
            count += 1
            if count > MAX_LOCK_TREE_ENTRIES:
                raise LockError("locked skill folder contains too many entries")
            relative = relative_directory / entry.name
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise LockError(
                    f"cannot inspect locked skill path: {relative.as_posix()}"
                ) from exc
            if stat.S_ISLNK(info.st_mode):
                yield relative, info, "symlink"
            elif stat.S_ISDIR(info.st_mode):
                stack.append((Path(entry.path), relative))
            elif stat.S_ISREG(info.st_mode):
                yield relative, info, "file"
            else:
                yield relative, info, "special"


def _verify_locked_tree(root: Path, listed: set[str]) -> None:
    allowed = listed | {"agent.lock"}
    for relative, info, kind in _skill_tree(root):
        name = relative.as_posix()
        if name in allowed:
            continue
        if kind == "symlink":
            raise LockError(f"agent.lock does not allow unlisted symlink: {name}")
        if kind != "file":
            raise LockError(
                f"agent.lock does not allow unlisted special file: {name}"
            )
        if _active_file(relative, info.st_mode):
            raise LockError(
                "agent.lock does not list executable or importable file: " + name
            )


def load_lock(root: Path = SKILL_ROOT) -> dict[str, Any]:
    path = root / "agent.lock"
    try:
        _regular_file(path, "agent.lock", single_link=True)
    except SafetyError as exc:
        raise LockError(str(exc)) from exc
    try:
        lock = parse_json_object(path.read_bytes(), "agent.lock")
    except ValueError as exc:
        raise LockError(str(exc)) from exc
    if lock.get("schema") != LOCK_SCHEMA:
        raise LockError(f"agent.lock schema must be {LOCK_SCHEMA}")
    if lock.get("name") != "rapp-work":
        raise LockError("agent.lock name must be rapp-work")
    if not isinstance(lock.get("version"), str) or not lock["version"]:
        raise LockError("agent.lock version is required")
    allowed = {"schema", "name", "version", "protocol", "sdk", "static", "files"}
    extra = sorted(set(lock) - allowed)
    if extra:
        raise LockError(f"agent.lock has unknown members: {', '.join(extra)}")
    files = lock.get("files")
    if not isinstance(files, list) or not files:
        raise LockError("agent.lock files must be a non-empty list")
    seen: set[str] = set()
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise LockError(f"agent.lock files[{index}] must contain path and sha256")
        relative = _safe_relative(entry["path"], f"agent.lock files[{index}].path")
        if relative.as_posix() == "agent.lock":
            raise LockError("agent.lock cannot hash itself")
        if relative.as_posix() in seen:
            raise LockError(f"agent.lock repeats {relative.as_posix()}")
        seen.add(relative.as_posix())
        expected = _strict_sha(entry["sha256"], f"agent.lock {relative.as_posix()}")
        target = root / relative
        try:
            _regular_file(
                target,
                f"locked file {relative.as_posix()}",
                single_link=True,
            )
        except SafetyError as exc:
            raise LockError(str(exc)) from exc
        actual = file_digest(target)
        if actual != expected:
            raise LockError(
                f"locked file changed: {relative.as_posix()} "
                f"(expected {expected}, got {actual})"
            )
    for section in ("protocol", "sdk", "static"):
        if not isinstance(lock.get(section), dict):
            raise LockError(f"agent.lock {section} must be an object")
        expected_members = LOCK_SECTION_MEMBERS[section]
        actual_members = set(lock[section])
        if actual_members != expected_members:
            missing = sorted(expected_members - actual_members)
            extra_members = sorted(actual_members - expected_members)
            details = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if extra_members:
                details.append("unknown " + ", ".join(extra_members))
            raise LockError(
                f"agent.lock {section} members are invalid ({'; '.join(details)})"
            )
    if lock["static"].get("repository") != STATIC_REPOSITORY:
        raise LockError(
            f"static.repository must be the canonical {STATIC_REPOSITORY}"
        )
    _lock_pin_state(lock)
    _verify_locked_tree(root, seen)
    return lock


def _git_environment() -> dict[str, str]:
    value = {
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
        "LANG": "C",
        "PATH": os.environ.get("PATH", os.defpath),
    }
    for key in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT"):
        if key in os.environ:
            value[key] = os.environ[key]
    return value


def _run_local_process(*args: Any, **kwargs: Any):
    try:
        return subprocess.run(*args, **kwargs)  # noqa: PLW1510
    except (subprocess.TimeoutExpired, OSError):
        raise ExecutionError(LOCAL_PROCESS_ERROR) from None


def _git_bytes(path: Path, *args: str) -> bytes:
    executable = shutil.which("git")
    if not executable:
        raise ResolutionError("git is required to verify an exact local checkout")
    result = _run_local_process(
        [
            executable,
            "-c",
            "core.fsmonitor=false",
            "-c",
            f"core.hooksPath={SKILL_ROOT / '.disabled-git-hooks'}",
            "-C",
            str(path),
            *args,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=_git_environment(),
        timeout=15,
        check=False,
    )
    if result.returncode:
        raise ResolutionError(f"{path} is not a readable Git checkout")
    return result.stdout


def _git(path: Path, *args: str) -> str:
    try:
        return os.fsdecode(_git_bytes(path, *args)).strip()
    except UnicodeError as exc:
        raise ResolutionError(f"{path} returned unreadable Git metadata") from exc


def _verify_git_index(path: Path, label: str) -> None:
    replacements = _git(
        path,
        "for-each-ref",
        "--format=%(refname)",
        "refs/replace",
    )
    if replacements:
        raise ResolutionError(f"{label} checkout contains replacement objects")
    records = _git_bytes(path, "ls-files", "-v", "-z").split(b"\0")
    for record in records:
        if not record:
            continue
        if len(record) < 3 or record[1:2] != b" " or record[:1] != b"H":
            raise ResolutionError(
                f"{label} checkout contains hidden or non-standard index state"
            )


def _verify_git_checkout(path: Path, pin: dict[str, Any], label: str) -> str:
    _directory(path, label)
    commit = _strict_commit(pin.get("commit"), f"{label} pin")
    top = _absolute_path(_git(path, "rev-parse", "--show-toplevel"), path, f"{label} root")
    if top != path:
        raise ResolutionError(f"{label} path must be the checkout root: {path}")
    _verify_git_index(path, label)
    head = _git(path, "rev-parse", "HEAD")
    if head != commit:
        raise ResolutionError(f"{label} checkout is {head}, lock requires {commit}")
    dirty = _git(path, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise ResolutionError(f"{label} checkout must be clean at {commit}")
    return commit


def _verify_checkout(
    path: Path,
    pin: dict[str, Any],
    *,
    label: str,
    artifact_field: str,
    sha_field: str = "sha256",
) -> Path:
    _verify_git_checkout(path, pin, label)
    expected_sha = _strict_sha(pin.get(sha_field), f"{label} artifact pin")
    relative = _safe_relative(str(pin.get(artifact_field, "")), f"{label} {artifact_field}")
    artifact = path / relative
    _regular_file(artifact, f"{label} pinned artifact")
    actual = file_digest(artifact)
    if actual != expected_sha:
        raise ResolutionError(
            f"{label} artifact changed (expected {expected_sha}, got {actual})"
        )
    return artifact


def _verify_protocol_checkout(path: Path, pin: dict[str, Any]) -> None:
    _verify_git_checkout(path, pin, "RAPP/1")
    for path_field, sha_field, label in (
        ("path", "sha256", "RAPP/1 specification"),
        ("reference_path", "reference_sha256", "RAPP/1 reference"),
    ):
        relative = _safe_relative(str(pin.get(path_field, "")), label)
        target = path / relative
        _regular_file(target, label)
        expected = _strict_sha(pin.get(sha_field), f"{label} pin")
        actual = file_digest(target)
        if actual != expected:
            raise ResolutionError(
                f"{label} changed (expected {expected}, got {actual})"
            )


def _verify_sdk_parent_pin(
    sdk_root: Path, sdk_pin: dict[str, Any], protocol_pin: dict[str, Any]
) -> None:
    relative = _safe_relative(
        str(sdk_pin.get("rapp1_pin", "")), "SDK RAPP/1 pin path"
    )
    path = sdk_root / relative
    _regular_file(path, "SDK RAPP/1 pin")
    try:
        value = parse_json_object(path.read_bytes(), "SDK RAPP/1 pin")
    except ValueError as exc:
        raise ResolutionError(str(exc)) from exc
    expected = {
        "schema": "rapp-work-parent-pin/1",
        "protocol": "rapp/1",
        "repository": protocol_pin.get("repository"),
        "commit": protocol_pin.get("commit"),
        "spec_path": protocol_pin.get("path"),
        "spec_sha256": protocol_pin.get("sha256"),
        "reference_path": protocol_pin.get("reference_path"),
        "reference_sha256": protocol_pin.get("reference_sha256"),
    }
    if value != expected:
        raise ResolutionError(
            "the canonical SDK is pinned to different RAPP/1 bytes"
        )


def _git_tree_entries(
    root: Path, commit: str, prefix: Path
) -> dict[str, tuple[str, str, str]]:
    raw = _git_bytes(
        root,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        commit,
        "--",
        prefix.as_posix(),
    )
    entries: dict[str, tuple[str, str, str]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        header, separator, raw_name = record.partition(b"\t")
        fields = header.split(b" ")
        if not separator or len(fields) != 3:
            raise ResolutionError("SDK commit has an unreadable source inventory")
        try:
            mode = fields[0].decode("ascii")
            object_type = fields[1].decode("ascii")
            object_id = fields[2].decode("ascii")
            name = raw_name.decode("utf-8")
            relative = _safe_relative(name, "SDK commit path")
        except (UnicodeError, SafetyError) as exc:
            raise ResolutionError("SDK commit has an unsafe source path") from exc
        normalized = relative.as_posix()
        if normalized in entries:
            raise ResolutionError("SDK commit repeats a source path")
        entries[normalized] = (mode, object_type, object_id)
    return entries


def _sdk_source_files(source_root: Path) -> dict[str, os.stat_result]:
    files: dict[str, os.stat_result] = {}
    stack: list[tuple[Path, Path]] = [(source_root, Path())]
    entries_seen = 0
    bytes_seen = 0
    while stack:
        directory, relative_directory = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise ResolutionError(
                f"SDK source cannot be inspected: {relative_directory.as_posix()}"
            ) from exc
        for entry in entries:
            entries_seen += 1
            if entries_seen > MAX_SDK_SOURCE_ENTRIES:
                raise ResolutionError("SDK source contains too many entries")
            relative = relative_directory / entry.name
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ResolutionError(
                    f"SDK source cannot be inspected: {relative.as_posix()}"
                ) from exc
            if stat.S_ISLNK(info.st_mode):
                raise ResolutionError(
                    f"SDK source contains a symlink: {relative.as_posix()}"
                )
            if stat.S_ISDIR(info.st_mode):
                stack.append((Path(entry.path), relative))
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ResolutionError(
                    f"SDK source contains a special file: {relative.as_posix()}"
                )
            bytes_seen += info.st_size
            if bytes_seen > MAX_SDK_SOURCE_BYTES:
                raise ResolutionError("SDK source executable inventory is too large")
            if _active_file(relative, info.st_mode):
                files[relative.as_posix()] = info
    return files


def _git_blob_digest(path: Path, info: os.stat_result, algorithm: str) -> str:
    try:
        value = hashlib.new(algorithm)
    except ValueError as exc:
        raise ResolutionError(
            f"SDK repository uses unsupported Git object format {algorithm!r}"
        ) from exc
    value.update(f"blob {info.st_size}\0".encode("ascii"))
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _verify_sdk_source(sdk_root: Path, sdk_pin: dict[str, Any]) -> None:
    commit = _strict_commit(sdk_pin.get("commit"), "SDK pin")
    source = _safe_relative(str(sdk_pin.get("source_path", "")), "SDK source path")
    source_root = sdk_root / source
    _directory(source_root, "SDK source path")
    entries = _git_tree_entries(sdk_root, commit, source)
    package_prefix = (source / "rapp_work").as_posix() + "/"
    expected: dict[str, tuple[str, str]] = {}
    package_modules = 0
    for name, (mode, object_type, object_id) in entries.items():
        relative_name = name[len(source.as_posix()) + 1 :]
        relative = Path(*PurePosixPath(relative_name).parts)
        active = _active_file(relative, 0) or mode == "100755"
        if name.startswith(package_prefix):
            if mode == "120000" or object_type != "blob":
                raise ResolutionError(
                    "SDK commit contains a non-regular rapp_work module"
                )
            if active:
                package_modules += 1
        if active:
            if object_type != "blob" or mode not in {"100644", "100755"}:
                raise ResolutionError(
                    f"SDK commit contains unsafe executable content: {name}"
                )
            expected[relative.as_posix()] = (mode, object_id)
    if package_modules == 0:
        raise ResolutionError("SDK commit contains no executable rapp_work modules")

    working = _sdk_source_files(source_root)
    unpinned = sorted(set(working) - set(expected))
    if unpinned:
        raise ResolutionError(
            "SDK source contains unpinned executable or importable file: "
            + unpinned[0]
        )
    missing = sorted(set(expected) - set(working))
    if missing:
        raise ResolutionError(
            "SDK source is missing pinned executable or importable file: "
            + missing[0]
        )
    object_format = _git(sdk_root, "rev-parse", "--show-object-format")
    if object_format not in {"sha1", "sha256"}:
        raise ResolutionError(
            f"SDK repository uses unsupported Git object format {object_format!r}"
        )
    for name in sorted(expected):
        path = source_root / Path(*PurePosixPath(name).parts)
        info = working[name]
        actual = _git_blob_digest(path, info, object_format)
        if actual != expected[name][1]:
            raise ResolutionError(
                f"SDK executable module differs from pinned commit: "
                f"{(source / Path(*PurePosixPath(name).parts)).as_posix()}"
            )


def _ancestors(path: Path, maximum: int = 8) -> list[Path]:
    values: list[Path] = []
    current = path
    for _ in range(maximum):
        values.append(current)
        if current.parent == current:
            break
        current = current.parent
    return values


def _first_existing(candidates: list[Path]) -> Path | None:
    seen: set[str] = set()
    for candidate in candidates:
        absolute = Path(os.path.abspath(candidate))
        key = os.path.normcase(str(absolute))
        if key in seen:
            continue
        seen.add(key)
        if absolute.exists():
            _refuse_symlink_components(absolute, "local discovery path")
            return Path(os.path.realpath(absolute))
    return None


def _resolve_path(
    explicit: str | None,
    env_name: str,
    candidates: list[Path],
    *,
    cwd: Path,
    label: str,
) -> tuple[Path | None, str]:
    if explicit is not None:
        value = _absolute_path(explicit, cwd, label)
        _directory(value, label)
        return value, "explicit"
    environment = os.environ.get(env_name)
    if environment:
        value = _absolute_path(environment, cwd, label)
        _directory(value, label)
        return value, f"environment:{env_name}"
    found = _first_existing(candidates)
    return (found, "local") if found is not None else (None, "unresolved")


def resolve_sdk(
    explicit: str | None, cwd: Path
) -> tuple[Path | None, str]:
    candidates: list[Path] = []
    for parent in _ancestors(cwd):
        candidates.extend(
            [
                parent / ".rapp-work-sdk",
                parent / "vendor" / "rapp-work-sdk",
                parent / "rapp-work-sdk",
            ]
        )
    return _resolve_path(
        explicit,
        "RAPP_WORK_SDK_PATH",
        candidates,
        cwd=cwd,
        label="SDK path",
    )


def resolve_rapp1(
    explicit: str | None, cwd: Path, sdk_path: Path | None
) -> tuple[Path | None, str]:
    candidates: list[Path] = []
    if sdk_path is not None:
        candidates.append(sdk_path / "vendor" / "rapp-1")
    for parent in _ancestors(cwd):
        candidates.extend(
            [
                parent / ".rapp" / "rapp-1",
                parent / "vendor" / "rapp-1",
                parent / "rapp-1",
            ]
        )
    return _resolve_path(
        explicit,
        "RAPP1_PATH",
        candidates,
        cwd=cwd,
        label="RAPP/1 path",
    )


def _normalize_api_base(value: str, label: str) -> str:
    if "PENDING_" in value:
        raise ResolutionError(f"{label} is waiting for an exact release pin")
    parsed = urlsplit(value)
    if parsed.scheme != "https":
        raise ResolutionError(f"{label} must use HTTPS")
    if not parsed.netloc or parsed.username or parsed.password:
        raise ResolutionError(f"{label} must not contain credentials")
    if parsed.query or parsed.fragment:
        raise ResolutionError(f"{label} must not contain a query or fragment")
    decoded = unquote(parsed.path)
    if _contains_traversal(decoded):
        raise ResolutionError(f"{label} contains path traversal")
    return value.rstrip("/")


def resolve_api(
    explicit: str | None, lock: dict[str, Any]
) -> tuple[str | None, str]:
    state = _lock_pin_state(lock)
    expected = (
        _static_api_base(_strict_commit(lock["static"].get("commit"), "static API pin"))
        if state == "final"
        else None
    )
    if explicit is not None:
        value = _normalize_api_base(explicit, "API base")
        if expected is None or value != expected:
            raise ResolutionError(
                "API base must equal the URL derived from the exact static commit"
            )
        return value, "explicit"
    environment = os.environ.get("RAPP_WORK_API_BASE")
    if environment:
        value = _normalize_api_base(environment, "RAPP_WORK_API_BASE")
        if expected is None or value != expected:
            raise ResolutionError(
                "RAPP_WORK_API_BASE must equal the URL derived from the exact static commit"
            )
        return value, "environment:RAPP_WORK_API_BASE"
    value = lock["static"].get("api_base")
    if state == "pending":
        return None, "pending-lock"
    if not isinstance(value, str) or value != expected:
        raise LockError("locked API base differs from the exact static commit")
    return _normalize_api_base(value, "locked API base"), "lock"


def _clean_sdk_environment() -> dict[str, str]:
    value = {
        "HOME": str(SKILL_ROOT),
        "USERPROFILE": str(SKILL_ROOT),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C",
        "LANG": "C",
        "RAPP_WORK_NETWORK_DEFAULT": "disabled",
        "RAPP_WORK_EXTERNAL_EFFECTS": "refuse",
    }
    for key in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT"):
        if key in os.environ:
            value[key] = os.environ[key]
    return value


def _reject_sensitive_members(value: Any, label: str = "response") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_RE.search(key):
                raise SafetyError(f"{label} contains a credential-like member")
            _reject_sensitive_members(child, label)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_members(child, label)


def _sdk_command(sdk_root: Path, sdk: dict[str, Any]) -> list[str]:
    if sdk.get("interface") != "python-sdk-json-stdin-v1":
        raise LockError("sdk.interface must be python-sdk-json-stdin-v1")
    source = _safe_relative(str(sdk.get("source_path", "")), "SDK source path")
    source_root = sdk_root / source
    _directory(source_root, "SDK source path")
    return [
        sys.executable,
        "-I",
        "-S",
        "-B",
        "-c",
        SDK_BOOTSTRAP,
        str(source_root),
    ]


def invoke_sdk(
    sdk_root: Path,
    sdk_pin: dict[str, Any],
    request: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    result = _run_local_process(
        _sdk_command(sdk_root, sdk_pin),
        input=canonical_bytes(request) + b"\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        cwd=sdk_root,
        env=_clean_sdk_environment(),
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        raise SdkError(f"canonical SDK/CLI exited with status {result.returncode}")
    try:
        response = parse_json_object(
            result.stdout,
            "canonical SDK/CLI output",
            maximum=MAX_SDK_JSON_BYTES,
        )
    except ValueError as exc:
        raise SdkError(str(exc)) from exc
    _reject_sensitive_members(response, "canonical SDK/CLI output")
    if response.get("schema") != "rapp-work-result/1":
        raise SdkError("canonical SDK returned an unknown result schema")
    if response.get("operation") != request["operation"]:
        raise SdkError("canonical SDK/CLI returned a different operation")
    if response.get("status") == "refused":
        refusal = response.get("refusal")
        code = refusal.get("code") if isinstance(refusal, dict) else None
        suffix = f" ({code})" if isinstance(code, str) else ""
        raise SdkError(f"canonical SDK/CLI refused the operation{suffix}")
    return response


def _operation_paths(args: argparse.Namespace, cwd: Path) -> dict[str, Path]:
    if args.operation == "migrate":
        if args.source is None or args.target is None:
            raise SafetyError("migrate requires --source and --target")
        source = _absolute_path(args.source, cwd, "source")
        target = _absolute_path(args.target, cwd, "target")
        _directory(source, "source")
        _empty_destination(target, "target")
        if (
            source == target
            or source in target.parents
            or target in source.parents
        ):
            raise SafetyError("migration source and target must be disjoint")
        return {"root": source, "source": source, "target": target}

    root = _absolute_path(args.root, cwd, "root")
    if args.operation == "scaffold":
        _empty_destination(root, "scaffold destination")
    else:
        _directory(root, "root")
    return {"root": root, "source": root, "target": root}


def _discover_roots(args: argparse.Namespace, cwd: Path) -> list[Path]:
    raw = args.discover_root or [args.root]
    roots: list[Path] = []
    seen: set[str] = set()
    for index, value in enumerate(raw):
        path = _absolute_path(value, cwd, f"discover root {index}")
        _directory(path, f"discover root {index}")
        key = os.path.normcase(str(path))
        if key not in seen:
            seen.add(key)
            roots.append(path)
    if not 1 <= len(roots) <= 32:
        raise SafetyError("discover requires one to thirty-two distinct roots")
    return roots


def _relative_plan_path(raw: Any, label: str) -> Path:
    if not isinstance(raw, str):
        raise SafetyError(f"{label} must be a string")
    return _safe_relative(raw, label)


def _protected_component(path: Path) -> str | None:
    for component in path.parts:
        lowered = component.casefold()
        if lowered == ".git":
            return ".git"
        if "credential" in lowered:
            return "credentials"
        if lowered in {
            ".aws",
            ".azure",
            ".env",
            ".gnupg",
            ".netrc",
            ".npmrc",
            ".pypirc",
            ".ssh",
            "id_ed25519",
            "id_rsa",
            "soul.md",
            "brainstem.py",
        }:
            return lowered
        if Path(lowered).suffix in {".key", ".p12", ".pfx"}:
            return lowered
    return None


def _plan_actions(plan: dict[str, Any]) -> list[dict[str, Any]]:
    actions = plan.get("actions")
    if not isinstance(actions, list):
        raise SafetyError("canonical SDK/CLI plan actions must be an array")
    if len(actions) > 4096:
        raise SafetyError("plan has too many actions")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise SafetyError(f"plan actions[{index}] must be an object")
        operation = action.get("operation")
        if operation not in {"create", "replace"}:
            raise SafetyError(
                f"plan actions[{index}] has unsafe operation {operation!r}"
            )
        relative = _relative_plan_path(
            action.get("path"), f"plan actions[{index}].path"
        )
        name = relative.as_posix()
        if name in seen:
            raise SafetyError(f"plan repeats managed path {name}")
        for prior in seen:
            if name.startswith(prior + "/") or prior.startswith(name + "/"):
                raise SafetyError("plan contains overlapping managed paths")
        seen.add(name)
        protected = _protected_component(relative)
        if protected is not None:
            raise SafetyError(f"plan targets protected content: {protected}")
        expected = action.get("expected_sha256")
        if operation == "create" and expected is not None:
            raise SafetyError(
                f"plan actions[{index}] create has a replace precondition"
            )
        if operation == "replace" and SHA256_RE.fullmatch(str(expected)) is None:
            raise SafetyError(
                f"plan actions[{index}] replace lacks an exact precondition"
            )
        committed = action.get("sha256")
        if SHA256_RE.fullmatch(str(committed)) is None:
            raise SafetyError(f"plan actions[{index}].sha256 is invalid")
        encoded = action.get("content_base64")
        if not isinstance(encoded, str):
            raise SafetyError(f"plan actions[{index}].content_base64 is required")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise SafetyError(
                f"plan actions[{index}] contains invalid base64"
            ) from exc
        if base64.b64encode(content).decode("ascii") != encoded:
            raise SafetyError(f"plan actions[{index}] base64 is not canonical")
        if len(content) > 16 * 1024 * 1024:
            raise SafetyError(f"plan actions[{index}] content is too large")
        if action.get("bytes") != len(content):
            raise SafetyError(f"plan actions[{index}] byte count is invalid")
        if hashlib.sha256(content).hexdigest() != committed:
            raise SafetyError(f"plan actions[{index}] content hash is invalid")
        mode = action.get("mode")
        if (
            isinstance(mode, bool)
            or not isinstance(mode, int)
            or not 0 <= mode <= 0o777
        ):
            raise SafetyError(
                f"plan actions[{index}].mode must be ordinary file permissions"
            )
        result.append({**action, "_relative": relative, "_content": content})
    return result


def _validate_plan(
    plan: dict[str, Any],
    operation: str,
    paths: dict[str, Path],
    *,
    before_apply: bool,
) -> list[dict[str, Any]]:
    if not isinstance(plan, dict):
        raise SafetyError("canonical SDK/CLI plan must be an object")
    if plan.get("operation") != operation:
        raise SafetyError("plan operation does not match the request")
    if plan.get("network") is not False:
        raise SafetyError("plan must keep network disabled")
    for key in ("external_effects", "network_effects"):
        effects = plan.get(key, [])
        if effects not in (None, []):
            raise SafetyError(f"plan requests forbidden {key}")
    for key in ("push", "publish", "deploy"):
        if plan.get(key) not in (None, False):
            raise SafetyError(f"plan requests forbidden {key}")
    root = paths["target"]
    if plan.get("target") != str(root):
        raise SafetyError("plan target differs from the requested destination")
    actions = _plan_actions(plan)
    if operation in {"scaffold", "migrate"}:
        _empty_destination(root, "destination")
    for index, action in enumerate(actions):
        target = root / action["_relative"]
        _refuse_symlink_components(target, f"plan actions[{index}] target")
        exists = target.exists()
        if exists:
            _regular_file(
                target,
                f"managed file {target}",
                single_link=True,
            )
        if action["operation"] == "create" and exists:
            raise SafetyError(f"managed file already exists: {target}")
        if action["operation"] == "replace":
            if not exists:
                raise SafetyError(f"managed file is missing: {target}")
            if file_digest(target) != action["expected_sha256"]:
                raise SafetyError(f"managed file conflicts with plan: {target}")
        if before_apply and action["operation"] == "create" and target.exists():
            raise SafetyError(f"managed file appeared before apply: {target}")
    return actions


def _stage_managed_file(target: Path, content: bytes, mode: int) -> Path:
    _refuse_symlink_components(target.parent, "managed file parent")
    target.parent.mkdir(parents=True, exist_ok=True)
    _directory(target.parent, "managed file parent")
    _refuse_symlink_components(target.parent, "managed file parent")
    descriptor = -1
    staged: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            prefix=".rapp-work-stage-",
            dir=target.parent,
        )
        staged = Path(raw_path)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(staged, mode)
        return staged
    except OSError:
        if descriptor >= 0:
            os.close(descriptor)
        if staged is not None:
            try:
                staged.unlink()
            except OSError:
                pass
        raise SafetyError("managed file could not be staged atomically") from None


def _publish_staged_file(
    action: dict[str, Any], target: Path, staged: Path
) -> None:
    _refuse_symlink_components(target, "managed file target")
    if action["operation"] == "replace":
        _regular_file(target, "managed file target", single_link=True)
        if file_digest(target) != action["expected_sha256"]:
            raise SafetyError(f"managed file conflicts with plan: {target}")
        try:
            os.replace(staged, target)
        except OSError:
            raise SafetyError("managed file replacement was not atomic") from None
        return

    if os.path.lexists(target):
        raise SafetyError(f"managed file appeared before apply: {target}")
    try:
        os.link(staged, target)
        staged.unlink()
    except FileExistsError:
        raise SafetyError(f"managed file appeared before apply: {target}") from None
    except OSError:
        raise SafetyError("managed file creation was not atomic") from None


def _apply_actions_atomically(
    actions: list[dict[str, Any]], root: Path
) -> dict[str, Any]:
    if actions:
        _refuse_symlink_components(root, "managed destination")
        root.mkdir(parents=True, exist_ok=True)
        _directory(root, "managed destination")
    staged: list[tuple[dict[str, Any], Path, Path]] = []
    try:
        for action in actions:
            target = root / action["_relative"]
            staged_path = _stage_managed_file(
                target,
                action["_content"],
                action["mode"],
            )
            staged.append((action, target, staged_path))
        for action, target, staged_path in staged:
            _publish_staged_file(action, target, staged_path)
        _validate_postconditions(actions, root)
    finally:
        for _, _, staged_path in staged:
            try:
                staged_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass
    return {
        "schema": "rapp-work-apply-result/1",
        "status": "applied",
        "files": len(actions),
    }


def _validate_postconditions(
    actions: list[dict[str, Any]], root: Path
) -> None:
    for action in actions:
        target = root / action["_relative"]
        _refuse_symlink_components(target, "applied managed path")
        _regular_file(target, "applied managed file", single_link=True)
        if file_digest(target) != action["sha256"]:
            raise SafetyError(f"applied managed file has unexpected bytes: {target}")


def _request(
    args: argparse.Namespace,
    paths: dict[str, Path],
) -> dict[str, Any]:
    operation = args.operation
    value: dict[str, Any] = {"operation": operation}
    if operation in {"status", "verify", "update"}:
        value["root"] = str(paths["root"])
    elif operation == "scaffold":
        value.update(
            {
                "root": str(paths["root"]),
                "kind": args.kind,
                "mode": args.mode,
                "owner_label": args.owner_label,
                "slug": args.slug,
                "world_id": args.world_id,
            }
        )
    elif operation == "migrate":
        value.update(
            {
                "source": str(paths["source"]),
                "target": str(paths["target"]),
            }
        )
    return value


def _discover_request(roots: list[Path], maximum: int) -> dict[str, Any]:
    return {
        "operation": "discover",
        "roots": [str(path) for path in roots],
        "max_entries": maximum,
    }


def _plan_from_response(response: dict[str, Any]) -> tuple[dict[str, Any], str]:
    result = response.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("plan"), dict):
        raise SdkError("canonical SDK/CLI did not return one plan object")
    plan = result["plan"]
    claimed = result.get("plan_sha256")
    actual = digest(plan)
    if claimed != actual:
        raise SdkError("canonical SDK/CLI plan SHA-256 does not match its plan")
    return plan, actual


def _status(
    lock: dict[str, Any],
    sdk_path: Path | None,
    sdk_source: str,
    rapp1_path: Path | None,
    rapp1_source: str,
    api_base: str | None,
    api_source: str,
) -> dict[str, Any]:
    pending = _pending_pins(lock)
    ready = not pending and sdk_path is not None and rapp1_path is not None
    return {
        "schema": RESULT_SCHEMA,
        "operation": "status",
        "status": "ready" if ready else (
            "awaiting-exact-pins" if pending else "unresolved"
        ),
        "pending_pins": pending,
        "resolution": {
            "sdk": {
                "path": str(sdk_path) if sdk_path is not None else None,
                "source": sdk_source,
            },
            "rapp1": {
                "path": str(rapp1_path) if rapp1_path is not None else None,
                "source": rapp1_source,
            },
            "api_base": {"value": api_base, "source": api_source},
        },
        "operations": list(OPERATIONS),
        "mutation_default": "plan-only",
        "apply_requires": "exact-plan-digest",
        "network_responses": "inert-data-only",
        "auto_clone_install": False,
        "external_effects_authorized": False,
    }


def _fetch_discovery(api_base: str, lock: dict[str, Any], timeout: int) -> dict[str, Any]:
    static = lock["static"]
    static_commit = _strict_commit(static.get("commit"), "static API pin")
    expected_api_base = _static_api_base(static_commit)
    if api_base != expected_api_base:
        raise DiscoveryError(
            "discovery API base differs from the exact static commit"
        )
    expected = _strict_sha(static.get("sha256"), "static API index pin")
    index = _safe_relative(str(static.get("index", "")), "static API index")
    url = api_base + "/" + index.as_posix()
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        raise DiscoveryError("discovery URL is not credential-free HTTPS")
    opener = build_opener(_NoRedirect)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "rapp-work-skill/1",
        },
        method="GET",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_JSON_BYTES:
                raise DiscoveryError("discovery response is too large")
            raw = response.read(MAX_JSON_BYTES + 1)
    except RappWorkError:
        raise
    except Exception as exc:
        raise DiscoveryError(
            f"discovery request failed without executing downloaded content: "
            f"{exc.__class__.__name__}"
        ) from exc
    if len(raw) > MAX_JSON_BYTES:
        raise DiscoveryError("discovery response is too large")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise DiscoveryError(
            f"discovery index hash differs from lock (expected {expected}, got {actual})"
        )
    try:
        document = parse_json_object(raw, "discovery response")
    except ValueError as exc:
        raise DiscoveryError(str(exc)) from exc
    _reject_sensitive_members(document, "discovery response")
    return {
        "schema": RESULT_SCHEMA,
        "operation": "discover",
        "status": "verified-inert-metadata",
        "sha256": actual,
        "source": url,
        "executed": False,
        "document": document,
    }


def _require_ready_pins(lock: dict[str, Any], sections: tuple[str, ...]) -> None:
    pending = [
        item
        for item in _pending_pins(lock)
        if item.split(".", 1)[0] in sections
    ]
    if pending:
        raise LockError("exact release pins are still pending: " + ", ".join(pending))


def parser() -> argparse.ArgumentParser:
    root = LockedArgumentParser(description=__doc__)
    root.add_argument("operation", nargs="?", default="verify", choices=OPERATIONS)
    root.add_argument("--sdk-path")
    root.add_argument("--rapp1-path")
    root.add_argument("--api-base")
    root.add_argument("--root", "--workspace", dest="root", default=".")
    root.add_argument("--source")
    root.add_argument("--target", "--destination", dest="target")
    root.add_argument("--discover-root", action="append")
    root.add_argument("--max-entries", type=int, default=10_000)
    root.add_argument("--kind", choices=("workspace", "organization"))
    root.add_argument("--owner-label")
    root.add_argument("--slug")
    root.add_argument("--world-id")
    root.add_argument("--mode", choices=("solo", "hive"), default="solo")
    root.add_argument(
        "--apply",
        metavar="PLAN_DIGEST",
        help="apply only this exact 64-character plan digest",
    )
    root.add_argument("--timeout", type=int, default=20)
    return root


def _prepare_sdk(
    sdk_path: Path,
    rapp1_path: Path,
    lock: dict[str, Any],
) -> None:
    _verify_checkout(
        sdk_path,
        lock["sdk"],
        label="SDK",
        artifact_field="entrypoint",
    )
    _verify_protocol_checkout(rapp1_path, lock["protocol"])
    _verify_sdk_parent_pin(sdk_path, lock["sdk"], lock["protocol"])
    _verify_sdk_source(sdk_path, lock["sdk"])


def _require_sdk_paths(
    sdk_path: Path | None, rapp1_path: Path | None
) -> tuple[Path, Path]:
    if sdk_path is None:
        raise ResolutionError(
            "no canonical SDK checkout found; use --sdk-path or RAPP_WORK_SDK_PATH"
        )
    if rapp1_path is None:
        raise ResolutionError(
            "no canonical RAPP/1 checkout found; use --rapp1-path or RAPP1_PATH"
        )
    return sdk_path, rapp1_path


def _validate_operation_arguments(args: argparse.Namespace) -> None:
    if args.operation == "scaffold":
        missing = [
            flag
            for flag, value in (
                ("--kind", args.kind),
                ("--owner-label", args.owner_label),
                ("--slug", args.slug),
                ("--world-id", args.world_id),
            )
            if not value
        ]
        if missing:
            raise SafetyError("scaffold requires " + ", ".join(missing))
    if args.operation == "migrate" and (args.source is None or args.target is None):
        raise SafetyError("migrate requires --source and --target")
    if not 1 <= args.max_entries <= 10_000:
        raise SafetyError("--max-entries must be between 1 and 10000")


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if not 1 <= args.timeout <= 60:
        raise SafetyError("timeout must be between 1 and 60 seconds")
    if args.apply is not None and args.operation not in MUTATIONS:
        raise SafetyError("--apply is only valid for scaffold, update, or migrate")
    if args.apply is not None and SHA256_RE.fullmatch(args.apply) is None:
        raise SafetyError("--apply requires an exact lowercase SHA-256 plan digest")
    _validate_operation_arguments(args)

    lock = load_lock()
    cwd = Path(os.path.abspath(Path.cwd()))
    _refuse_symlink_components(cwd, "working directory")
    sdk_path, sdk_source = resolve_sdk(args.sdk_path, cwd)
    rapp1_path, rapp1_source = resolve_rapp1(args.rapp1_path, cwd, sdk_path)
    api_base, api_source = resolve_api(args.api_base, lock)

    if args.operation == "status":
        value = _status(
            lock,
            sdk_path,
            sdk_source,
            rapp1_path,
            rapp1_source,
            api_base,
            api_source,
        )
        if not _pending_pins(lock) and sdk_path is not None and rapp1_path is not None:
            _prepare_sdk(sdk_path, rapp1_path, lock)
            paths = _operation_paths(args, cwd)
            value["sdk_result"] = invoke_sdk(
                sdk_path, lock["sdk"], _request(args, paths), args.timeout
            )
            value["status"] = "ready"
        return 0, value

    if args.operation == "discover":
        static_requested = (
            args.api_base is not None
            or bool(os.environ.get("RAPP_WORK_API_BASE"))
        )
        if static_requested:
            _require_ready_pins(lock, ("static",))
            if api_base is None:
                raise ResolutionError(
                    "no API base found; use --api-base or RAPP_WORK_API_BASE"
                )
            return 0, _fetch_discovery(api_base, lock, args.timeout)
        _require_ready_pins(lock, ("protocol", "sdk"))
        sdk_path, rapp1_path = _require_sdk_paths(sdk_path, rapp1_path)
        _prepare_sdk(sdk_path, rapp1_path, lock)
        roots = _discover_roots(args, cwd)
        result = invoke_sdk(
            sdk_path,
            lock["sdk"],
            _discover_request(roots, args.max_entries),
            args.timeout,
        )
        return (
            0,
            {
                "schema": RESULT_SCHEMA,
                "operation": "discover",
                "status": "inert-local-metadata",
                "executed": False,
                "result": result,
            },
        )

    _require_ready_pins(lock, ("protocol", "sdk"))
    sdk_path, rapp1_path = _require_sdk_paths(sdk_path, rapp1_path)
    _prepare_sdk(sdk_path, rapp1_path, lock)
    paths = _operation_paths(args, cwd)

    if args.operation == "verify":
        result = invoke_sdk(
            sdk_path, lock["sdk"], _request(args, paths), args.timeout
        )
        return (
            0,
            {
                "schema": RESULT_SCHEMA,
                "operation": args.operation,
                "status": "verified",
                "result": result,
            },
        )

    planned = invoke_sdk(
        sdk_path, lock["sdk"], _request(args, paths), args.timeout
    )
    plan, plan_digest = _plan_from_response(planned)
    actions = _validate_plan(
        plan,
        args.operation,
        paths,
        before_apply=args.apply is not None,
    )
    if args.apply is None:
        return (
            0,
            {
                "schema": RESULT_SCHEMA,
                "operation": args.operation,
                "status": "planned",
                "plan_digest": plan_digest,
                "plan_sha256": plan_digest,
                "plan": plan,
            },
        )
    if args.apply != plan_digest:
        raise SafetyError(
            f"refusing apply: supplied digest {args.apply} "
            f"does not equal current plan {plan_digest}"
        )
    actions = _validate_plan(
        plan,
        args.operation,
        paths,
        before_apply=True,
    )
    applied = _apply_actions_atomically(actions, paths["target"])
    applied["plan_sha256"] = plan_digest
    return (
        0,
        {
            "schema": RESULT_SCHEMA,
            "operation": args.operation,
            "status": "applied",
            "plan_digest": plan_digest,
            "plan_sha256": plan_digest,
            "result": applied,
        },
    )


def main(argv: list[str] | None = None) -> int:
    operation = "unknown"
    try:
        parsed = parser().parse_args(argv)
        operation = parsed.operation
        code, value = run(parsed)
    except RappWorkError as exc:
        emit(
            {
                "schema": RESULT_SCHEMA,
                "operation": operation,
                "status": "refused",
                "error": {"code": exc.code, "message": str(exc)},
            }
        )
        return 2
    emit(value)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
