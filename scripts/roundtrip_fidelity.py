#!/usr/bin/env python3
"""Prove the full conversion loop preserves capability, with no third-party deps.

The loop this repo promises, and the loop this script actually walks:

    raw SKILL.md  ->  toasted SKILL.md  ->  *_agent.py  ->  SKILL.md  ->  *_agent.py
      (bread)          (this repo)          (RAPP agent)     (back)        (lap 2)

`toaster.py roundtrip` answers a narrower question -- "are the bytes identical?"
-- and a byte comparison necessarily fails on the derived side of the loop,
because the RCI capsule carries an append-only `provenance` trail that is
*supposed* to grow by one entry per hop. That is the ledger working, not drift.

The invariant that actually matters is capability identity: `capability_id` is
a hash of WHAT the capability is, independent of the route it travelled. This
script asserts that identity, plus every field a user would notice losing,
holds at every stage of the loop -- and separately asserts byte-exactness for
the home format, where it is a real guarantee rather than an artifact.

Usage:
    python3 scripts/roundtrip_fidelity.py [repo_root]
    TOASTER=/path/to/toaster.py python3 scripts/roundtrip_fidelity.py

Implementation lives in https://github.com/kody-w/rapp-toaster.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# The two artifacts toasting adds to a SKILL.md. Removing both returns the file
# to raw bread -- prose with nothing canonical underneath it.
#
# Both markers are anchored to a whole line, because a skill is allowed to
# *document* them: matching them mid-sentence made a prose mention of the begin
# and end markers look like a real block, so the strip removed the sentence and
# left the actual blocks in place.
GENERATED_BLOCK = re.compile(
    r"\n?^<!-- toaster:generated:begin -->$.*?^<!-- toaster:generated:end -->$\n?",
    re.S | re.M,
)
CAPSULE = re.compile(r"\n?^<!-- rci-capsule:v1:[^>]*-->$\n?", re.S | re.M)

# Fields a consumer of the skill would notice losing. `provenance` and the
# `preserved` blob are deliberately excluded: they are route metadata, and
# they are expected to differ between stages.
CAPABILITY_FIELDS = (
    "name",
    "slug",
    "description",
    "instructions",
    "parameters",
    "system_context",
    "tags",
    "license",
    "examples",
    "platform",
)

TOASTER_SEARCH = (
    "toaster.py",
    "../rapp-toaster/toaster.py",
    "~/Documents/GitHub/rapp-toaster/toaster.py",
    "~/rapp-toaster/toaster.py",
)


def find_toaster(root: Path) -> Path | None:
    explicit = os.environ.get("TOASTER")
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.is_file() else None
    for candidate in TOASTER_SEARCH:
        path = Path(os.path.expanduser(candidate))
        if not path.is_absolute():
            path = (root / candidate).resolve()
        if path.is_file():
            return path
    return None


def load_toaster(path: Path):
    spec = importlib.util.spec_from_file_location("toaster", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def steps_of(rci: dict) -> list:
    return ((rci.get("impl") or {}).get("steps")) or []


def render_to(tk, rci: dict, fmt: str, path: Path) -> Path:
    """toaster.render returns bytes; write them and hand back the path."""
    path.write_bytes(tk.render(rci, fmt))
    return path


def runs_standalone(agent_py: Path) -> bool:
    """An emitted agent must be runnable Python, not merely plausible text.

    Capability comparison alone cannot catch a file that parses as a valid
    record but raises on import -- which is exactly how a JSON `false` leaking
    into Python source presented.
    """
    probe = subprocess.run(
        [sys.executable, str(agent_py), "--tool"], capture_output=True, timeout=60
    )
    return probe.returncode == 0


def compare(stage_a: str, rci_a: dict, stage_b: str, rci_b: dict, tk) -> list[str]:
    """Report every capability-level difference between two stages."""
    problems = []
    hop = f"{stage_a} -> {stage_b}"

    if tk.capability_id(rci_a) != tk.capability_id(rci_b):
        problems.append(f"{hop}: capability-id changed")

    for field in CAPABILITY_FIELDS:
        if rci_a.get(field) != rci_b.get(field):
            problems.append(f"{hop}: field {field!r} changed")

    if steps_of(rci_a) != steps_of(rci_b):
        problems.append(f"{hop}: deterministic steps changed")

    return problems


def check_skill(skill_md: Path, tk, workdir: Path) -> tuple[list[str], dict]:
    """Walk one skill through the full loop; return (problems, stats)."""
    problems: list[str] = []
    slug = skill_md.parent.name

    # ---- Stage 1: the toasted skill as committed in this repo ---------------
    toasted = tk.load(str(skill_md), "skill")

    # ---- Stage 0: strip back to raw bread on disk, re-toast, and confirm the
    # derived layer is reproducible rather than a one-off accident. This is the
    # real entry to the loop: a raw SKILL.md written by a human or another
    # agent, with no canonical record yet.
    text = CAPSULE.sub("", GENERATED_BLOCK.sub("", skill_md.read_text("utf-8")))
    raw_path = workdir / f"{slug}_raw_SKILL.md"
    raw_path.write_text(text.rstrip() + "\n", encoding="utf-8")
    if GENERATED_BLOCK.search(text) or CAPSULE.search(text):
        problems.append("raw: strip left toaster artifacts behind")

    raw = tk.load(str(raw_path), "skill")
    tk.toast_rci(raw)  # mutates in place; the return value is a report

    if raw.get("parameters") != toasted.get("parameters"):
        problems.append("raw -> toast: derived parameters not reproducible")
    if steps_of(raw) != steps_of(toasted):
        problems.append("raw -> toast: derived steps not reproducible")
    if tk.capability_id(raw) != tk.capability_id(toasted):
        problems.append("raw -> toast: capability-id not reproducible")

    # ---- Stage 2: skill -> agent -------------------------------------------
    agent_path = render_to(tk, toasted, "agent", workdir / f"{slug}_lap1_agent.py")
    as_agent = tk.load(str(agent_path), "agent")
    problems += compare("skill", toasted, "agent", as_agent, tk)

    # ---- Stage 3: agent -> skill (the return leg) --------------------------
    back_path = render_to(tk, as_agent, "skill", workdir / f"{slug}_lap1_SKILL.md")
    as_skill = tk.load(str(back_path), "skill")
    problems += compare("agent", as_agent, "skill'", as_skill, tk)
    problems += compare("skill", toasted, "skill'", as_skill, tk)

    # The home format must be byte-exact: a skill that leaves as an agent and
    # comes home must be the same file, or the repo's own diff review is lying.
    if skill_md.read_bytes() != back_path.read_bytes():
        problems.append("skill -> agent -> skill: NOT byte-exact")

    # ---- Stage 4: second lap, to catch drift that only accumulates ----------
    lap2_path = render_to(tk, as_skill, "agent", workdir / f"{slug}_lap2_agent.py")
    lap2 = tk.load(str(lap2_path), "agent")
    problems += compare("skill'", as_skill, "agent'", lap2, tk)
    problems += compare("skill", toasted, "agent'", lap2, tk)

    # ---- The committed agent must match what conversion produces -----------
    committed = skill_md.parent / tk.agent_filename(toasted)
    if not committed.is_file():
        problems.append(f"missing committed agent: {committed.name}")
    else:
        on_disk = tk.load(str(committed), "agent")
        problems += compare("committed agent", on_disk, "skill", toasted, tk)
        if not runs_standalone(committed):
            problems.append("committed agent: does not run standalone (--tool)")

    stats = {
        "params": len((toasted.get("parameters") or {}).get("properties", {})),
        "steps": len(steps_of(toasted)),
        "capability_id": tk.capability_id(toasted)[:12],
    }
    return problems, stats


def check_raw_skill(skill_md: Path, tk, workdir: Path) -> tuple[list[str], dict]:
    """Walk a never-toasted SKILL.md through the loop.

    This is the harder test: the file was authored by hand for some other host
    and the toaster has never seen it, so nothing was tuned to make it pass.
    Entry is genuine bread rather than a committed skill stripped back to look
    like bread.
    """
    problems: list[str] = []
    slug = skill_md.parent.name

    # An already-toasted file in a raw corpus is not a failure -- it simply
    # belongs to the other check. Report it as skipped rather than broken.
    if "rci-capsule" in skill_md.read_text("utf-8", errors="replace"):
        return [], {"skipped": "already toast"}

    # ---- Stage 0 -> 1: bread -> toast --------------------------------------
    # The vaulted copy of the raw input must be dropped before rendering, or
    # render() faithfully restores the very bytes we are replacing and toasting
    # silently no-ops. This mirrors `toaster.py toast`, the supported entry.
    toasted = tk.load(str(skill_md), "skill")
    toasted.setdefault("preserved", {}).pop("skill", None)
    tk.toast_rci(toasted)

    # Toasting must be idempotent: a second pass may re-append provenance, but
    # it must not discover new parameters or steps that the first pass missed.
    again = tk.load(str(skill_md), "skill")
    again.setdefault("preserved", {}).pop("skill", None)
    tk.toast_rci(again)
    tk.toast_rci(again)
    if again.get("parameters") != toasted.get("parameters"):
        problems.append("toast: not idempotent (parameters)")
    if steps_of(again) != steps_of(toasted):
        problems.append("toast: not idempotent (steps)")

    # ---- Stage 1 -> 2: toasted skill on disk -------------------------------
    skill_path = render_to(tk, toasted, "skill", workdir / f"{slug}_t_SKILL.md")
    on_disk = tk.load(str(skill_path), "skill")
    problems += compare("toast", toasted, "skill", on_disk, tk)

    # ---- Stage 2 -> 3: skill -> agent --------------------------------------
    agent_path = render_to(tk, on_disk, "agent", workdir / f"{slug}_agent.py")
    as_agent = tk.load(str(agent_path), "agent")
    problems += compare("skill", on_disk, "agent", as_agent, tk)

    # The emitted agent must actually be runnable Python, not plausible text.
    if not runs_standalone(agent_path):
        problems.append("agent: does not run standalone (--tool)")

    # ---- Stage 3 -> 4: agent -> skill, and byte-exactness once toasted -----
    back_path = render_to(tk, as_agent, "skill", workdir / f"{slug}_back_SKILL.md")
    back = tk.load(str(back_path), "skill")
    problems += compare("agent", as_agent, "skill'", back, tk)
    problems += compare("skill", on_disk, "skill'", back, tk)
    if skill_path.read_bytes() != back_path.read_bytes():
        problems.append("skill -> agent -> skill: NOT byte-exact")

    # ---- Stage 4 -> 5: second lap ------------------------------------------
    lap2_path = render_to(tk, back, "agent", workdir / f"{slug}_lap2_agent.py")
    lap2 = tk.load(str(lap2_path), "agent")
    problems += compare("skill'", back, "agent'", lap2, tk)
    problems += compare("toast", toasted, "agent'", lap2, tk)

    stats = {
        "params": len((toasted.get("parameters") or {}).get("properties", {})),
        "steps": len(steps_of(toasted)),
        "capability_id": tk.capability_id(toasted)[:12],
    }
    return problems, stats


def find_skills(root: Path) -> list[Path]:
    """Locate every SKILL.md under root, following symlinked skill directories.

    `Path.rglob` does not descend into symlinked directories, and symlinking a
    skill into a host's skills folder is the documented install method -- so a
    naive walk silently validates a fraction of the corpus and reports success.
    Resolved paths are deduped, since the same skill is often linked twice.
    """
    found: dict[Path, Path] = {}
    for path in root.rglob("SKILL.md"):
        if ".git" not in path.parts:
            found.setdefault(path.resolve(), path)
    if root.is_dir():
        for entry in root.iterdir():
            if entry.is_symlink() and entry.is_dir():
                for path in entry.resolve().rglob("SKILL.md"):
                    if ".git" not in path.parts:
                        found.setdefault(path.resolve(), path)
    return sorted(found.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="treat every SKILL.md under root as never-toasted bread "
             "(e.g. ~/.claude/skills) rather than a committed toasted skill",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    toaster_path = find_toaster(root)
    if not toaster_path:
        print(
            "toaster.py not found. Clone it and retry:\n"
            "  git clone https://github.com/kody-w/rapp-toaster.git\n"
            "  TOASTER=rapp-toaster/toaster.py python3 "
            "scripts/roundtrip_fidelity.py",
            file=sys.stderr,
        )
        return 1

    tk = load_toaster(toaster_path)
    skills = find_skills(root)
    if not skills:
        print(f"No SKILL.md files found under {root}", file=sys.stderr)
        return 1

    walk = check_raw_skill if args.raw else check_skill
    failures: list[str] = []
    skipped = 0
    total_params = total_steps = 0

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for skill_md in skills:
            slug = skill_md.parent.name
            problems, stats = walk(skill_md, tk, workdir)
            if stats.get("skipped"):
                skipped += 1
                print(f"skip  {slug:<28} {stats['skipped']}")
                continue
            total_params += stats.get("params", 0)
            total_steps += stats.get("steps", 0)
            if problems:
                failures.append(slug)
                print(f"FAIL  {slug}  [{stats.get('capability_id', '-')}]")
                for problem in problems:
                    print(f"        {problem}")
            else:
                print(
                    f"ok    {slug:<28} {stats['params']:>2} params "
                    f"{stats['steps']:>2} steps  [{stats['capability_id']}]"
                )

    print()
    print(f"toaster:   {toaster_path}")
    print(
        f"loop:      {'bread' if args.raw else 'raw'} -> skill -> agent -> "
        f"skill -> agent  ({len(skills)} skills x 2 laps)"
    )
    print(f"derived:   {total_params} typed parameters, {total_steps} ordered steps")

    if failures:
        print(f"FIDELITY LOST in {len(failures)}: {', '.join(failures)}")
        return 1
    checked = len(skills) - skipped
    print(f"result:    {checked}/{checked} preserved capability, no drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
