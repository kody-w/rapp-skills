#!/usr/bin/env python3
"""Verify every committed Agent Skill pair through the public converter CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONVERTER = ROOT / "toast.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONVERTER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def main() -> int:
    argparse.ArgumentParser(
        description="Prove every committed Agent Skill pair restores byte-identical "
        "through the converter's public CLI."
    ).parse_args()
    engine_toast = ROOT / "engine" / "rapp-agent-converter" / "scripts" / "toast.py"
    cat_toast = ROOT / "cat-agent-skills" / "rapp-agent-converter" / "scripts" / "toast.py"
    if engine_toast.read_bytes() != cat_toast.read_bytes():
        print(
            "FAIL  cat-agent-skills/rapp-agent-converter/scripts/toast.py\n"
            "      diverged from engine/rapp-agent-converter/scripts/toast.py; "
            "re-run the cat import (or copy the engine file over the mirror) to resync"
        )
        return 1
    print(f"ok    {'engine toast.py mirror':<52} byte-identical")

    skill_dirs = {
        path.parent
        for path in ROOT.rglob("SKILL.md")
        if ".git" not in path.parts
        and path.relative_to(ROOT).parts[0] != "engine"
    }
    pair_agents = list(ROOT.glob("*/*_agent.py"))
    pair_agents += list(ROOT.glob("cat-agent-skills/*/*_agent.py"))
    agent_dirs = {path.parent for path in pair_agents}
    if not skill_dirs and not agent_dirs:
        print("No top-level *_agent.py capability pairs found", file=sys.stderr)
        return 1

    failures: list[str] = []

    pair_files = set(pair_agents)
    pair_files |= set(ROOT.glob("*/SKILL.md"))
    pair_files |= set(ROOT.glob("cat-agent-skills/*/SKILL.md"))
    pair_dirs = {path.parent for path in pair_files}
    for path in sorted(list(ROOT.rglob("*_agent.py")) + list(ROOT.rglob("SKILL.md"))):
        if ".git" in path.parts or path in pair_files:
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] == "engine":
            continue
        pair_dir = next((p for p in path.parents if p in pair_dirs), None)
        if pair_dir is not None:
            if path.name == "SKILL.md":
                continue  # backstopped by the skill_dirs pairing check
            if path.relative_to(pair_dir).parts[0] in {
                "assets",
                "references",
                "scripts",
            }:
                continue  # asset/script inside a verified pair directory
        label = rel.as_posix()
        failures.append(label)
        print(
            f"FAIL  {label}\n"
            "      stray pair file outside discovery "
            "(expected <pair>/ or cat-agent-skills/<pair>/)"
        )

    for directory in sorted(skill_dirs - agent_dirs):
        label = directory.relative_to(ROOT).as_posix()
        failures.append(label)
        print(f"FAIL  {label}\n      SKILL.md has no linked *_agent.py")
    for directory in sorted(agent_dirs - skill_dirs):
        label = directory.relative_to(ROOT).as_posix()
        failures.append(label)
        print(f"FAIL  {label}\n      *_agent.py has no companion SKILL.md")

    agents = []
    for directory in sorted(skill_dirs & agent_dirs):
        matches = sorted(directory.glob("*_agent.py"))
        label = directory.relative_to(ROOT).as_posix()
        if len(matches) != 1:
            failures.append(label)
            print(
                f"FAIL  {label}\n"
                f"      expected one linked agent, found {len(matches)}"
            )
        else:
            agents.append(matches[0])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for agent in agents:
            label = agent.parent.relative_to(ROOT).as_posix()
            temp_name = label.replace("/", "__")
            skill = agent.parent / "SKILL.md"
            problems: list[str] = []

            if not skill.is_file():
                problems.append("missing companion SKILL.md")
            else:
                restored = work / f"{temp_name}_restored.py"
                result = run(
                    "convert", str(skill), "--to", "agent", "-o", str(restored)
                )
                if result.returncode != 0:
                    problems.append(
                        "SKILL.md restore failed: "
                        + (result.stderr or result.stdout).strip().splitlines()[-1]
                    )
                elif restored.read_bytes() != agent.read_bytes():
                    problems.append("SKILL.md restores different agent bytes")

                projected_dir = work / f"{temp_name}_projection"
                projected = projected_dir / "SKILL.md"
                result = run(
                    "convert", str(agent), "--to", "skill", "-o", str(projected)
                )
                if result.returncode != 0:
                    problems.append(
                        "agent projection failed: "
                        + (result.stderr or result.stdout).strip().splitlines()[-1]
                    )
                elif projected.read_bytes() != skill.read_bytes():
                    problems.append("committed SKILL.md is not the canonical projection")

            result = run("roundtrip", str(agent))
            if result.returncode != 0:
                problems.append(
                    "agent roundtrip failed: "
                    + (result.stderr or result.stdout).strip().splitlines()[-1]
                )

            tool = subprocess.run(
                [sys.executable, str(agent), "--tool"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if tool.returncode != 0:
                problems.append("--tool exits nonzero")
            else:
                try:
                    contract = json.loads(tool.stdout)
                    function = contract["function"]
                    if not function["name"]:
                        raise ValueError("empty function name")
                    if function["parameters"]["type"] != "object":
                        raise ValueError("parameters.type must be 'object'")
                except (ValueError, KeyError, TypeError):
                    problems.append("--tool output is not a function contract")

            if problems:
                failures.append(label)
                print(f"FAIL  {label}")
                for problem in problems:
                    print(f"      {problem}")
            else:
                print(f"ok    {label:<52} byte-identical + executable contract")

    print()
    if failures:
        print(f"FAILED {len(failures)}/{len(agents)}: {', '.join(failures)}")
        return 1
    print(f"PASS  {len(agents)}/{len(agents)} Agent Skill pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
