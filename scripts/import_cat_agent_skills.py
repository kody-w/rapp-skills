#!/usr/bin/env python3
"""Import CAT Agent Skills as verified RAPP Agent Skill pairs.

For every actual Agent Skill submission:

1. copy the complete agent-facing bundle;
2. synthesize a RAPP launchpad agent from the authored SKILL.md;
3. project that agent back into a capsule-bearing SKILL.md + linked agent;
4. prove restoration, projection, roundtrip, and --tool behavior;
5. write a deterministic catalog with source and hash provenance.

Scout automation JSON and installer-only archives are recorded as exclusions,
not invented into capabilities they are not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONVERTER = (
    ROOT / "engine" / "rapp-agent-converter" / "scripts" / "toast.py"
)
DEFAULT_OUTPUT = ROOT / "cat-agent-skills"
SOURCE_REPOSITORY = "https://github.com/microsoft/cat-agent-skills"
CATALOG_SCHEMA = "rapp-skills-cat-catalog/1.0"
OWNERSHIP_MARKER = ".rapp-cat-catalog"
SIDECARS = {"metadata.json", "metadata.yaml", "README.md"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def git(source: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(args)}\n{detail}")
    return result


def safe_archive_path(name: str) -> PurePosixPath:
    if "\\" in name or re.match(r"^[A-Za-z]:", name) \
            or name.startswith(("/", "//", "\\\\")):
        raise RuntimeError(f"unsafe archive entry: {name}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"unsafe archive entry: {name}")
    return path


def safe_destination(root: Path, relative: PurePosixPath) -> Path:
    target = root.joinpath(*relative.parts)
    base = root.resolve()
    resolved = target.resolve()
    try:
        inside = os.path.commonpath([str(base), str(resolved)]) == str(base)
    except ValueError:
        inside = False
    if not inside:
        raise RuntimeError(f"archive entry escapes destination: {relative}")
    return target


def materialize_git_submissions(source: Path, commit: str, destination: Path) -> None:
    """Materialize committed blobs, never the mutable checkout working tree."""
    destination.mkdir(parents=True)
    process = subprocess.Popen(
        ["git", "-C", str(source), "archive", "--format=tar", commit, "submissions"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                relative = safe_archive_path(member.name)
                target = safe_destination(destination, relative)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise RuntimeError(
                        f"unsupported git archive entry: {member.name}"
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"cannot read git blob: {member.name}")
                target.write_bytes(extracted.read())
                target.chmod(member.mode & 0o777)
    finally:
        process.stdout.close()
    stderr = process.stderr.read().decode("utf-8", "replace") \
        if process.stderr is not None else ""
    if process.stderr is not None:
        process.stderr.close()
    if process.wait() != 0:
        raise RuntimeError(f"git archive failed: {stderr.strip()}")


def load_metadata(submission: Path) -> dict:
    path = submission / "metadata.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def copy_unpacked_skill(submission: Path, destination: Path) -> str:
    for child in sorted(submission.iterdir()):
        if child.name in SIDECARS:
            continue
        target = destination / child.name
        if child.is_dir():
            shutil.copytree(child, target)
        elif child.is_file():
            shutil.copy2(child, target)
    if not (destination / "SKILL.md").is_file():
        raise RuntimeError(f"{submission}: unpacked skill has no SKILL.md")
    return f"submissions/{submission.name}/SKILL.md"


def copy_zipped_skill(archive: Path, destination: Path) -> str | None:
    with zipfile.ZipFile(archive) as bundle:
        entries = [
            (info, safe_archive_path(info.filename))
            for info in bundle.infolist()
        ]
        skills = [path for _, path in entries if path.name == "SKILL.md"]
        if not skills:
            return None
        if len(skills) != 1:
            raise RuntimeError(
                f"{archive}: expected one SKILL.md, found {len(skills)}"
            )
        skill_path = skills[0]
        prefix = skill_path.parent
        for info, path in entries:
            if info.is_dir():
                continue
            if prefix.parts:
                try:
                    relative = path.relative_to(prefix)
                except ValueError:
                    continue
            else:
                relative = path
            if not relative.parts \
                    or (len(relative.parts) == 1 and relative.name in SIDECARS):
                continue
            target = safe_destination(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.read(info))
    if not (destination / "SKILL.md").is_file():
        raise RuntimeError(f"{archive}: selected skill root has no SKILL.md")
    return f"submissions/{archive.parent.name}/{archive.name}#{skill_path.as_posix()}"


def classify(submission: Path) -> tuple[str, Path | None, str]:
    if (submission / "SKILL.md").is_file():
        return "unpacked-skill", submission / "SKILL.md", ""
    archives = sorted(submission.glob("*.zip"))
    if archives:
        with zipfile.ZipFile(archives[0]) as bundle:
            skills = [
                safe_archive_path(info.filename)
                for info in bundle.infolist()
                if safe_archive_path(info.filename).name == "SKILL.md"
            ]
        if skills:
            return "legacy-zip-skill", archives[0], ""
        return "excluded-installer", archives[0], "archive contains no SKILL.md"
    payload_json = [
        path for path in submission.glob("*.json")
        if path.name != "metadata.json"
    ]
    if payload_json:
        return (
            "excluded-automation",
            payload_json[0],
            "Scout automation JSON is not an Agent Skill",
        )
    return "excluded-other", None, "no Agent Skill payload"


def verify_pair(
    converter: Path,
    skill: Path,
    agent: Path,
    work: Path,
) -> dict:
    restored = work / "restored.py"
    run(
        sys.executable,
        str(converter),
        "convert",
        str(skill),
        "--to",
        "agent",
        "-o",
        str(restored),
    )
    if restored.read_bytes() != agent.read_bytes():
        raise RuntimeError(f"{skill.parent.name}: SKILL.md restores different bytes")

    projection = work / "projection" / "SKILL.md"
    run(
        sys.executable,
        str(converter),
        "convert",
        str(agent),
        "--to",
        "skill",
        "-o",
        str(projection),
    )
    if projection.read_bytes() != skill.read_bytes():
        raise RuntimeError(f"{skill.parent.name}: SKILL.md is not canonical")

    result = run(
        sys.executable,
        str(converter),
        "roundtrip",
        str(agent),
    )
    if "IDENTICAL" not in result.stdout:
        raise RuntimeError(f"{skill.parent.name}: roundtrip gave no IDENTICAL verdict")

    tool = run(sys.executable, str(agent), "--tool")
    contract = json.loads(tool.stdout)
    function = contract["function"]
    parameters = function["parameters"]
    if not function.get("name") or parameters.get("type") != "object":
        raise RuntimeError(f"{skill.parent.name}: invalid --tool contract")
    execution = run(sys.executable, str(agent), "{}")
    result = json.loads(execution.stdout)
    if "steps" in result:
        result_kind = "steps"
    elif "instructions" in result:
        result_kind = "instructions"
    else:
        result_kind = "direct"
    return {
        "tool": function["name"],
        "parameters": len(parameters.get("properties", {})),
        "required": len(parameters.get("required", [])),
        "resultKind": result_kind,
    }


def source_url(repository: str, commit: str, location: str) -> str:
    if "#" in location:
        path, fragment = location.split("#", 1)
        return f"{repository}/blob/{commit}/{path}#{fragment}"
    return f"{repository}/blob/{commit}/{location}"


def contains_path(container: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath(
            [str(container.resolve()), str(candidate.resolve())]
        ) == str(container.resolve())
    except ValueError:
        return False


def output_is_owned_catalog(output: Path) -> bool:
    marker = output / OWNERSHIP_MARKER
    if marker.is_file() and marker.read_text(encoding="utf-8") == \
            CATALOG_SCHEMA + "\n":
        return True
    manifest = output / "catalog.json"
    if manifest.is_file():
        try:
            return json.loads(manifest.read_text()).get("schema") == CATALOG_SCHEMA
        except (json.JSONDecodeError, OSError):
            return False
    return False


def render_readme(manifest: dict) -> str:
    source = manifest["source"]
    counts = manifest["counts"]
    exclusions = "\n".join(
        f"| `{item['slug']}` | {item['reason']} |"
        for item in manifest["excluded"]
    )
    return f"""# CAT Agent Skills as RAPP pairs

This collection assimilates every Agent Skill in
[`microsoft/cat-agent-skills`]({source['repository']}) at commit
[`{source['commit'][:8]}`]({source['repository']}/commit/{source['commit']})
into the RAPP linked-pair shape:

```text
<slug>/
├── SKILL.md
└── <slug>_agent.py
```

The original agent-facing bundle (`scripts/`, `references/`, and `assets/`) is
preserved. The authored skill is synthesized into a RAPP launchpad agent, then
that agent is projected back into the final capsule-bearing `SKILL.md`. The
result works as an Agent Skill and restores the adjacent agent byte-identical.

## Inventory

| Item | Count |
|---|---:|
| Verified Agent Skill pairs | {counts['pairs']} |
| Unpacked source skills | {counts['unpacked']} |
| Legacy zip skills assimilated | {counts['legacy_zip']} |
| Skills with explicit typed parameters | {counts['typed_contracts']} |
| Prose-only / untyped launchpads | {counts['untyped_contracts']} |
| Launchpads returning preserved instructions | {counts['instruction_launchpads']} |
| Non-skill submissions recorded but excluded | {counts['excluded']} |

See [`catalog.json`](catalog.json) for every source path, source hash, final
hash, tool name, parameter count, supporting file, and exclusion.

## Use either surface

Install/read the skill:

```text
cat-agent-skills/<slug>/SKILL.md
```

Run or hot-load the RAPP cartridge:

```bash
python3 cat-agent-skills/<slug>/<slug_with_underscores>_agent.py --tool
python3 cat-agent-skills/<slug>/<slug_with_underscores>_agent.py '{{}}'
```

The synthesized agent intentionally does not invent behavior. It preserves the
skill instructions and explicit parameter/deterministic fences. A prose-only
skill returns its instructions and inputs for the host to follow.

## Rebuild and verify

```bash
python3 scripts/import_cat_agent_skills.py \\
  --source /path/to/cat-agent-skills
python3 scripts/validate_skills.py
python3 scripts/roundtrip_fidelity.py
```

The importer validates each pair in both directions, byte-compares a fresh
projection, runs the agent's `--tool` contract, and writes the collection only
after every item passes.

## Deliberate exclusions

| Submission | Reason |
|---|---|
{exclusions}

These are not silently converted because doing so would fabricate an Agent
Skill contract that the source repository does not claim.
"""


def import_catalog(source: Path, output: Path, converter: Path) -> dict:
    if not (source / ".git").exists():
        raise RuntimeError(f"{source}: Git checkout not found")
    if not converter.is_file():
        raise RuntimeError(f"converter not found: {converter}")
    if output.resolve() != DEFAULT_OUTPUT.resolve():
        raise RuntimeError(
            f"output is fixed to the importer-owned catalog: {DEFAULT_OUTPUT}"
        )
    if output == output.parent or contains_path(output, ROOT) \
            or contains_path(output, source) or contains_path(output, converter):
        raise RuntimeError(f"refusing unsafe output directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and (
        not output.is_dir() or not output_is_owned_catalog(output)
    ):
        raise RuntimeError(
            f"refusing to replace non-catalog output directory: {output}"
        )

    repository = SOURCE_REPOSITORY
    commit = git(source, "rev-parse", "HEAD")
    if not commit:
        raise RuntimeError("cannot resolve CAT source commit")
    try:
        converter_path = converter.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise RuntimeError(
            "converter must live inside the rapp-skills repository"
        ) from exc

    backup_prefix = f".{output.name}.backup-"
    stranded = sorted(
        path for path in output.parent.iterdir()
        if path.name.startswith(backup_prefix)
    )
    if stranded:
        names = ", ".join(path.name for path in stranded)
        raise RuntimeError(
            f"stranded catalog backup requires recovery before import: {names}"
        )

    temp_root = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.build-", dir=output.parent)
    )
    snapshot = temp_root / "source"
    materialize_git_submissions(source, commit, snapshot)
    submissions = snapshot / "submissions"
    if not submissions.is_dir():
        raise RuntimeError(f"{commit}: submissions/ not found in Git tree")

    collection = temp_root / output.name
    collection.mkdir()
    skills, excluded = [], []
    try:
        for submission in sorted(
            path for path in submissions.iterdir()
            if path.is_dir() and not path.name.startswith("_")
        ):
            slug = submission.name
            kind, payload, reason = classify(submission)
            if kind.startswith("excluded-"):
                excluded.append({"slug": slug, "kind": kind, "reason": reason})
                print(f"skip  {slug:<42} {reason}")
                continue

            destination = collection / slug
            destination.mkdir()
            if kind == "unpacked-skill":
                location = copy_unpacked_skill(submission, destination)
            else:
                location = copy_zipped_skill(payload, destination)
                if location is None:
                    raise RuntimeError(f"{slug}: zip classification changed")

            raw_skill = destination / "SKILL.md"
            raw_hash = sha256(raw_skill)
            source_tree_hash = tree_sha256(destination)
            source_files = {
                path.relative_to(destination).as_posix(): sha256(path)
                for path in sorted(
                    item for item in destination.rglob("*") if item.is_file()
                )
            }
            agent_name = slug.replace("-", "_") + "_agent.py"

            with tempfile.TemporaryDirectory() as pair_temp:
                work = Path(pair_temp)
                agent = work / agent_name
                run(
                    sys.executable,
                    str(converter),
                    "convert",
                    str(raw_skill),
                    "--to",
                    "agent",
                    "-o",
                    str(agent),
                )
                projected = work / "pair" / "SKILL.md"
                run(
                    sys.executable,
                    str(converter),
                    "convert",
                    str(agent),
                    "--to",
                    "skill",
                    "-o",
                    str(projected),
                )
                linked = projected.parent / agent_name
                if linked.read_bytes() != agent.read_bytes():
                    raise RuntimeError(f"{slug}: projected linked agent drifted")
                shutil.copy2(projected, raw_skill)
                shutil.copy2(linked, destination / agent_name)
                proof = verify_pair(
                    converter,
                    raw_skill,
                    destination / agent_name,
                    work / "verify",
                )

            metadata = load_metadata(submission)
            files = sorted(
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file()
            )
            entry = {
                "slug": slug,
                "name": metadata.get("name", slug),
                "author": metadata.get("author"),
                "platforms": metadata.get("platforms", []),
                "tags": metadata.get("tags", []),
                "sourceKind": kind,
                "sourcePath": location,
                "sourceUrl": source_url(repository, commit, location),
                "rawSkillSha256": raw_hash,
                "sourceBundleSha256": source_tree_hash,
                "sourceFiles": source_files,
                "skillSha256": sha256(raw_skill),
                "agentSha256": sha256(destination / agent_name),
                "skillBytes": raw_skill.stat().st_size,
                "agentBytes": (destination / agent_name).stat().st_size,
                "tool": proof["tool"],
                "parameters": proof["parameters"],
                "required": proof["required"],
                "resultKind": proof["resultKind"],
                "files": files,
                "fileSha256": {
                    path.relative_to(destination).as_posix(): sha256(path)
                    for path in sorted(
                        item for item in destination.rglob("*") if item.is_file()
                    )
                },
            }
            skills.append(entry)
            print(
                f"ok    {slug:<42} {proof['parameters']:>2} params "
                f"{len(files):>2} files"
            )

        manifest = {
            "schema": CATALOG_SCHEMA,
            "source": {
                "repository": repository,
                "commit": commit,
            },
            "converter": {
                "path": converter_path,
                "sha256": sha256(converter),
            },
            "counts": {
                "pairs": len(skills),
                "unpacked": sum(
                    item["sourceKind"] == "unpacked-skill" for item in skills
                ),
                "legacy_zip": sum(
                    item["sourceKind"] == "legacy-zip-skill" for item in skills
                ),
                "typed_contracts": sum(
                    item["parameters"] > 0 for item in skills
                ),
                "untyped_contracts": sum(
                    item["parameters"] == 0 for item in skills
                ),
                "instruction_launchpads": sum(
                    item["resultKind"] == "instructions" for item in skills
                ),
                "step_launchpads": sum(
                    item["resultKind"] == "steps" for item in skills
                ),
                "direct_result_agents": sum(
                    item["resultKind"] == "direct" for item in skills
                ),
                "excluded": len(excluded),
            },
            "skills": skills,
            "excluded": excluded,
        }
        (collection / "catalog.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (collection / "README.md").write_text(
            render_readme(manifest),
            encoding="utf-8",
        )
        (collection / OWNERSHIP_MARKER).write_text(
            CATALOG_SCHEMA + "\n",
            encoding="utf-8",
        )

        backup = Path(
            tempfile.mkdtemp(
                prefix=f".{output.name}.backup-",
                dir=output.parent,
            )
        )
        backup.rmdir()
        if output.exists():
            os.replace(output, backup)
        try:
            os.replace(collection, output)
        except Exception:
            if backup.exists() and not output.exists():
                os.replace(backup, output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return manifest
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def selftest() -> int:
    for unsafe in (
        "../escape",
        r"..\escape",
        r"C:\escape",
        r"\\server\share",
        "/absolute",
    ):
        try:
            safe_archive_path(unsafe)
            raise AssertionError(f"unsafe archive path accepted: {unsafe}")
        except RuntimeError:
            pass
    assert safe_archive_path("skills/example/SKILL.md").as_posix() == \
        "skills/example/SKILL.md"
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        target = safe_destination(root, PurePosixPath("a/b.txt"))
        assert target == root / "a" / "b.txt"
        repo = root / "repo"
        skill = repo / "submissions" / "demo" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        committed = b"---\nname: demo\ndescription: committed\n---\n\nBody.\n"
        skill.write_bytes(committed)
        run("git", "init", "-q", str(repo))
        run("git", "-C", str(repo), "add", ".")
        run(
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Importer Selftest",
            "-c",
            "user.email=selftest@example.invalid",
            "commit",
            "-qm",
            "fixture",
        )
        commit = git(repo, "rev-parse", "HEAD")
        skill.write_bytes(b"DIRTY WORKTREE\r\n")
        (skill.parent / ".ignored-secret").write_text("must not travel")
        snapshot = root / "snapshot"
        materialize_git_submissions(repo, commit, snapshot)
        assert (snapshot / "submissions/demo/SKILL.md").read_bytes() == committed
        assert not (snapshot / "submissions/demo/.ignored-secret").exists()
        unrelated = root / "unrelated"
        unrelated.mkdir()
        assert not output_is_owned_catalog(unrelated)
        (unrelated / "catalog.json").write_text(
            json.dumps({"schema": CATALOG_SCHEMA})
        )
        assert output_is_owned_catalog(unrelated)
        assert contains_path(root, unrelated)
        assert not contains_path(unrelated, root)
    print("IMPORTER SELFTEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        help="checkout of microsoft/cat-agent-skills",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run archive/path safety regressions and exit",
    )
    parser.add_argument(
        "--converter",
        type=Path,
        default=DEFAULT_CONVERTER,
        help="rapp-agent-converter scripts/toast.py",
    )
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.source is None:
        parser.error("--source is required unless --selftest is used")

    manifest = import_catalog(
        args.source.expanduser().resolve(),
        DEFAULT_OUTPUT.resolve(),
        args.converter.expanduser().resolve(),
    )
    counts = manifest["counts"]
    print()
    print(
        f"IMPORTED {counts['pairs']} Agent Skill pairs "
        f"({counts['unpacked']} unpacked + {counts['legacy_zip']} legacy zip)"
    )
    print(f"EXCLUDED {counts['excluded']} non-skill submissions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
