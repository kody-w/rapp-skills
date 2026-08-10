#!/usr/bin/env python3
"""Verify every committed Agent Skill pair through the public converter CLI."""

from __future__ import annotations

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
    skill_dirs = {path.parent for path in ROOT.glob("*/SKILL.md")}
    agent_dirs = {path.parent for path in ROOT.glob("*/*_agent.py")}
    if not skill_dirs and not agent_dirs:
        print("No top-level *_agent.py capability pairs found", file=sys.stderr)
        return 1

    failures: list[str] = []
    for directory in sorted(skill_dirs - agent_dirs):
        failures.append(directory.name)
        print(f"FAIL  {directory.name}\n      SKILL.md has no linked *_agent.py")
    for directory in sorted(agent_dirs - skill_dirs):
        failures.append(directory.name)
        print(f"FAIL  {directory.name}\n      *_agent.py has no companion SKILL.md")

    agents = []
    for directory in sorted(skill_dirs & agent_dirs):
        matches = sorted(directory.glob("*_agent.py"))
        if len(matches) != 1:
            failures.append(directory.name)
            print(
                f"FAIL  {directory.name}\n"
                f"      expected one linked agent, found {len(matches)}"
            )
        else:
            agents.append(matches[0])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for agent in agents:
            slug = agent.parent.name
            skill = agent.parent / "SKILL.md"
            problems: list[str] = []

            if not skill.is_file():
                problems.append("missing companion SKILL.md")
            else:
                restored = work / f"{slug}_restored.py"
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

                projected_dir = work / f"{slug}_projection"
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
                    assert function["name"]
                    assert function["parameters"]["type"] == "object"
                except (AssertionError, KeyError, json.JSONDecodeError):
                    problems.append("--tool output is not a function contract")

            if problems:
                failures.append(slug)
                print(f"FAIL  {slug}")
                for problem in problems:
                    print(f"      {problem}")
            else:
                print(f"ok    {slug:<28} byte-identical + executable contract")

    print()
    if failures:
        print(f"FAILED {len(failures)}/{len(agents)}: {', '.join(failures)}")
        return 1
    print(f"PASS  {len(agents)}/{len(agents)} Agent Skill pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
