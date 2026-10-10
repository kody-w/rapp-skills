#!/usr/bin/env python3
"""Check a one-file skill-with-agent (`<name>.agent.md`, spec: AGENT-MD.md) without running it.

    python3 agent_md.py check <file>     # valid skill, one python block, hash matches -> exit 0
    python3 agent_md.py extract <file>   # print the python block, only if the hash matches
    python3 agent_md.py from-agent <agent.py> [out.agent.md]   # move a legacy agent.py into one .agent.md, losslessly

Standard library only. This file never executes the code it reads; running it is the host's decision.
"""
from __future__ import annotations

import hashlib
import re
import sys

SPEC = "https://raw.githubusercontent.com/kody-w/rapp-skills/main/AGENT-MD.md"
FORMAT = "rapp-agent-md/1"
_FENCE = re.compile(r"^```python[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)


class Refused(ValueError):
    pass


def _frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise Refused("no skill header")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise Refused("skill header is not closed")
    head, body = text[4:end], text[end + 5:]
    fields, meta, in_meta = {}, {}, False
    for line in head.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) and in_meta:
            k, _, v = line.strip().partition(":")
            meta[k.strip()] = v.strip().strip('"')
            continue
        k, _, v = line.partition(":")
        in_meta = k.strip() == "metadata"
        if not in_meta:
            fields[k.strip()] = v.strip().strip('"')
    fields["metadata"] = meta
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    extra = set(fields) - allowed
    if extra:
        raise Refused("unknown header fields: " + ", ".join(sorted(extra)))
    if not fields.get("name") or not fields.get("description"):
        raise Refused("name and description are required")
    return fields, body


def code_block(text: str) -> str:
    _, body = _frontmatter(text)
    blocks = _FENCE.findall(body)
    if len(blocks) != 1:
        raise Refused(f"expected exactly one python block, found {len(blocks)}")
    return blocks[0]


def check(text: str) -> dict:
    fields, _ = _frontmatter(text)
    meta = fields["metadata"]
    if meta.get("format") != FORMAT:
        raise Refused(f"metadata.format must be {FORMAT}")
    code = code_block(text)
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    if meta.get("code-sha256") != digest:
        raise Refused("the code was changed after it was approved (hash does not match)")
    return {"name": fields["name"], "class": meta.get("agent-class", ""), "code-sha256": digest,
            "signed-by": meta.get("signed-by", "")}


def _literal_metadata(code: str) -> tuple[str, str, str]:
    """name, description and class of a legacy agent, read from its source without running it."""
    import ast
    tree = ast.parse(code)
    cls = next((n.name for n in tree.body if isinstance(n, ast.ClassDef)), "")
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in ("name", "description") and isinstance(v, ast.Constant) \
                        and isinstance(v.value, str) and k.value not in found:
                    found[k.value] = v.value
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr == "name" and "name" not in found:
                    found["name"] = node.value.value
    return found.get("name", ""), found.get("description", ""), cls


def from_agent(code: str, fallback_name: str) -> str:
    """A legacy single-file agent.py as one .agent.md. The code goes in byte for byte (extract gives it back exactly);
    the know-how section starts from the agent's own description and is the part a person should improve."""
    if "```" in code:
        raise Refused("the agent's code contains a ``` fence; it cannot sit inside one python block")
    if not code.endswith("\n"):
        raise Refused("the agent file must end with a newline to come back byte for byte")
    raw, desc, cls = _literal_metadata(code)
    slug = re.sub(r"[^a-z0-9]+", "-", (raw or fallback_name).lower()).strip("-") or "agent"
    desc = (desc or f"Runs the {raw or fallback_name} agent.").replace("\n", " ").strip()
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    return (f"---\nname: {slug}\ndescription: {desc}\nmetadata:\n  format: {FORMAT}\n  spec: {SPEC}\n"
            f"  agent-class: {cls}\n  code-sha256: {digest}\n  signed-by: unsigned\n---\n"
            f"# {raw or fallback_name}\n\n{desc}\n\nWhen to use it, how to explain its results, and what to check first: "
            f"write that here. This text is what a tool that only reads skills follows.\n\n## Examples\n"
            f"- (add input -> expected output pairs; a host runs these against the agent before using it)\n\n"
            f"## Agent\nThis block is text until a host checks it and decides to run it.\n\n```python\n{code}```\n")


def main(argv: list[str]) -> int:
    if len(argv) in (3, 4) and argv[1] == "from-agent":
        import pathlib
        src = pathlib.Path(argv[2])
        try:
            out_text = from_agent(src.read_text(encoding="utf-8"), src.stem.removesuffix("_agent"))
        except Refused as exc:
            print(f"refused: {exc}", file=sys.stderr); return 1
        out = pathlib.Path(argv[3]) if len(argv) == 4 else src.with_name(
            re.search(r"^name: (.+)$", out_text, re.M).group(1) + ".agent.md")
        if out.exists():
            print(f"refused: {out} already exists", file=sys.stderr); return 1
        out.write_text(out_text, encoding="utf-8"); print(f"wrote {out}"); return 0
    if len(argv) != 3 or argv[1] not in ("check", "extract"):
        print(__doc__.strip()); return 2
    text = open(argv[2], encoding="utf-8").read()
    try:
        info = check(text)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr); return 1
    print(code_block(text), end="") if argv[1] == "extract" else print(f"ok: {info['name']} {info['code-sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
