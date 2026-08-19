#!/usr/bin/env python3
"""Verify every CAT catalog file, capsule, and provenance hash."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COLLECTION = ROOT / "cat-agent-skills"
OWNERSHIP_MARKER = ".rapp-cat-catalog"
EXPECTED_COUNTS = {
    "pairs": 76,
    "unpacked": 73,
    "legacy_zip": 3,
    "typed_contracts": 0,
    "untyped_contracts": 76,
    "instruction_launchpads": 76,
    "step_launchpads": 0,
    "direct_result_agents": 0,
    "excluded": 5,
}


def check(condition: bool, message: object = None) -> None:
    """Explicit assertion that survives `python3 -O`."""
    if not condition:
        raise SystemExit(
            "CAT CATALOG FAIL"
            + ("" if message is None else f": {message!r}")
        )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_hash(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, data in sorted(files.items()):
        name = relative.encode()
        digest.update(len(name).to_bytes(4, "big"))
        digest.update(name)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads((COLLECTION / "catalog.json").read_text())
    check(manifest["counts"] == EXPECTED_COUNTS)
    check(len(manifest["skills"]) == 76)
    check(len(manifest["excluded"]) == 5)
    slugs = [item["slug"] for item in manifest["skills"]]
    check(len(set(slugs)) == len(slugs))
    check(
        (COLLECTION / OWNERSHIP_MARKER).read_text()
        == manifest["schema"] + "\n"
    )

    converter = ROOT / manifest["converter"]["path"]
    check(
        sha256(converter.read_bytes()) == manifest["converter"]["sha256"]
    )
    spec = importlib.util.spec_from_file_location("converter", converter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected_collection_files = {
        "README.md",
        "catalog.json",
        OWNERSHIP_MARKER,
    }
    for item in manifest["skills"]:
        directory = COLLECTION / item["slug"]
        skill = directory / "SKILL.md"
        agent = directory / (item["slug"].replace("-", "_") + "_agent.py")
        actual_files = {
            path.relative_to(directory).as_posix(): path
            for path in directory.rglob("*")
            if path.is_file()
        }
        check(sorted(actual_files) == item["files"], item["slug"])
        expected_collection_files.update(
            f"{item['slug']}/{relative}" for relative in item["files"]
        )
        check(set(actual_files) == set(item["fileSha256"]), item["slug"])
        for relative, path in actual_files.items():
            check(
                sha256(path.read_bytes()) == item["fileSha256"][relative],
                (item["slug"], relative),
            )

        check(
            sha256(skill.read_bytes()) == item["skillSha256"], item["slug"]
        )
        check(
            sha256(agent.read_bytes()) == item["agentSha256"], item["slug"]
        )

        rci = module.load(str(agent), "agent")
        raw_skill = module.restore(rci, "skill")
        check(sha256(raw_skill) == item["rawSkillSha256"], item["slug"])
        check(
            set(item["sourceFiles"]) == set(actual_files) - {agent.name},
            (item["slug"], "source file set"),
        )
        source_bytes = {}
        for relative, expected_hash in item["sourceFiles"].items():
            data = (
                raw_skill
                if relative == "SKILL.md"
                else actual_files[relative].read_bytes()
            )
            check(sha256(data) == expected_hash, (item["slug"], relative))
            source_bytes[relative] = data
        check(
            tree_hash(source_bytes) == item["sourceBundleSha256"],
            item["slug"],
        )

    actual_collection_files = {
        path.relative_to(COLLECTION).as_posix()
        for path in COLLECTION.rglob("*")
        if path.is_file()
    }
    check(actual_collection_files == expected_collection_files)

    print("CAT CATALOG PASS: 76/76 pairs, source bundles, and final files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
