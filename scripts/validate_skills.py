#!/usr/bin/env python3
"""Validate the repository's Agent Skills without third-party dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
    "disable-model-invocation",
}


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Imported CAT pairs preserve upstream-authored prose verbatim; their
    # catalog hashes enforce drift while local style recommendations stay local.
    imported_cat_skill = "cat-agent-skills" in path.parts

    if not lines or lines[0] != "---":
        return [f"{path}: frontmatter must start on line 1"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return [f"{path}: missing closing frontmatter delimiter"]

    fields: dict[str, str] = {}
    # True while consuming the indented continuation lines of a block scalar
    # (e.g. "description: >-"): the one multiline form this scanner
    # deliberately supports. Any other indented line is unrecognized.
    # Continuation lines are accumulated into the field value so the
    # required-field and length checks apply to the real content, not the
    # ">-" indicator literal.
    in_block_scalar = False
    block_key = ""
    block_lines: list[str] = []

    def close_block_scalar() -> None:
        nonlocal in_block_scalar
        if in_block_scalar:
            fields[block_key] = " ".join(block_lines).strip()
        in_block_scalar = False

    for line_number, line in enumerate(lines[1:end], start=2):
        if not line or not line.strip():
            # Blank lines are inert in YAML frontmatter (and legal inside a
            # block scalar), so they stay skipped.
            continue
        if line[0].isspace():
            if in_block_scalar:
                block_lines.append(line.strip())
                continue
            errors.append(
                f"{path}:{line_number}: unrecognized frontmatter line "
                f"(indented line outside a block scalar): {line.strip()!r}"
            )
            continue
        close_block_scalar()
        match = re.match(r"^([a-zA-Z0-9-]+):(?:[ \t]*(.*))?$", line)
        if not match:
            errors.append(f"{path}:{line_number}: invalid frontmatter entry")
            continue
        raw_value = (match.group(2) or "").strip()
        key, value = match.group(1), scalar(match.group(2) or "")
        if re.fullmatch(r"[>|][+-]?", raw_value):
            in_block_scalar = True
            block_key = key
            block_lines = []
        if key not in ALLOWED_FIELDS:
            errors.append(f"{path}:{line_number}: unsupported field {key!r}")
        if key in fields:
            errors.append(f"{path}:{line_number}: duplicate field {key!r}")
        fields[key] = value
    close_block_scalar()

    name = fields.get("name", "")
    description = fields.get("description", "")

    if not name:
        errors.append(f"{path}: missing required field 'name'")
    elif len(name) > 64 or not NAME_RE.fullmatch(name):
        errors.append(f"{path}: invalid Agent Skills name {name!r}")
    elif name != path.parent.name:
        errors.append(
            f"{path}: name {name!r} must match directory {path.parent.name!r}"
        )

    if not description:
        errors.append(f"{path}: missing required field 'description'")
    elif len(description) > 1024 and not imported_cat_skill:
        errors.append(f"{path}: description exceeds 1024 characters")

    compatibility = fields.get("compatibility", "")
    if len(compatibility) > 500:
        errors.append(f"{path}: compatibility exceeds 500 characters")

    if not any(line.strip() for line in lines[end + 1 :]):
        errors.append(f"{path}: Markdown body is empty")
    # Converter projections embed the complete linked agent after this marker.
    # The 500-line recommendation applies to authored instructions, not to the
    # byte-exact implementation that makes the pair self-contained.
    authored = text.split("<!-- toaster:generated:begin -->", 1)[0]
    if len(authored.splitlines()) > 500 and not imported_cat_skill:
        errors.append(f"{path}: SKILL.md exceeds the recommended 500-line limit")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the frontmatter and body of every SKILL.md under a root."
    )
    parser.add_argument(
        "root", nargs="?", default=".",
        help="directory to scan (default: current directory)",
    )
    root = Path(parser.parse_args().root).resolve()
    skills = sorted(
        path for path in root.rglob("SKILL.md") if ".git" not in path.parts
    )
    if not skills:
        print(f"No SKILL.md files found under {root}", file=sys.stderr)
        return 1

    errors = [error for path in skills for error in validate(path)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"Validated {len(skills)} skill(s):")
    for path in skills:
        print(f"- {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
