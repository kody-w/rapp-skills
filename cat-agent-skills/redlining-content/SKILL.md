---
name: "redlining-content"
description: "Use when the user asks to redline, track changes, or compare differences in a file. Compares an uploaded .docx or .pdf against a provided .dotx/.docx template and returns a redlined .docx where every textual difference is a Word tracked change (insertion/deletion) authored by \"Copilot Studio AI\". No visual conversion \u2014 built directly on the template."
---

# Redlining Content Skill

Reimplements "Word Compare" for the new Copilot Studio orchestrator. The
template is already a perfect Word document, so the output **is** the template
body with revisions injected as OOXML `<w:ins>` / `<w:del>` elements. Accepting
all changes yields the submission's wording; rejecting all keeps the template.

Changes are authored by **`Copilot Studio AI`** and the output has Track
Changes turned on so Word keeps tracking any further human edits.

## Requirements

- `lxml` (always)
- `pdfplumber` (PDF submissions; `pypdfium2` used as a fallback)

All are present in the Copilot Studio sandbox — no `pip install` required.
`.docx`/`.dotx` handling is pure `lxml` + standard library.

## Inputs

1. **Template** — the canonical baseline. Bundled with this skill in
   `assets/` (any single `.dotx`/`.docx` file — the name doesn't matter) and
   used automatically. A different template (`.dotx` or `.docx`) may be
   supplied explicitly to override it.
2. **Submission** — the user-uploaded file to compare against the template,
   either a `.docx` or a `.pdf`.

## Steps

1. Run from this skill's directory:
   `python scripts/redline.py <submission.docx|.pdf> [output.docx]`
   The bundled template in `assets/` is auto-discovered and used as the
   baseline (whatever its file name).
   To override the template explicitly, pass it via `--template`:
   `python scripts/redline.py --template <template.dotx|.docx> <submission.docx|.pdf> [output.docx]`
2. Return the output `.docx` to the user. Output defaults to the submission
   name with a `_redlined.docx` suffix.

## How it works

One shared engine, two input readers — the only thing that differs by file
type is how the submission's words are read:

- `.docx` / `.dotx` → `read_docx_words()` (paragraph text from
  `word/document.xml`).
- `.pdf` → `read_pdf_words()` (**text extraction only — never converted** to
  DOCX; uses pdfplumber, then pypdfium2).

Both produce a single flat **word list** fed into the same pipeline:

1. **Word-level diff over the whole document.** The template's words and the
   submission's words are each flattened into one stream and compared once with
   `difflib.SequenceMatcher`. PDF line-wrapping and paragraph boundaries are
   therefore irrelevant — only real word differences matter.
2. Each template word is mapped back to its source paragraph. Paragraphs with no
   changes are kept **byte-for-byte** (all formatting preserved); only changed
   paragraphs are rebuilt, with differing words wrapped in `<w:ins>` / `<w:del>`.
3. **Tables.** For `.docx` submissions, template tables are diffed against the
   submission's tables **cell by cell** (aligned by position: table → row →
   cell), with `<w:ins>` / `<w:del>` injected directly into each cell while its
   `<w:tcPr>` (width, borders, shading) is preserved. For `.pdf` submissions
   there is no table structure to align, so template tables pass through
   untouched and their words are stripped from the extracted text so they aren't
   flagged as insertions.
4. Writes the output zip: replaces `word/document.xml`, adds `<w:trackChanges/>`
   to `settings.xml`, and converts the `.dotx` main-part content type to the
   `.docx` one so the result opens as a normal document.

## Per-input guidance

See the focused reference docs:

- `references/docx-submissions.md` — `.docx` handling, high-fidelity path.
- `references/pdf-submissions.md` — `.pdf` handling, why text is extracted (not
  converted), the word-level diff, and table handling.

## v1 limitations

- Inside a *changed* paragraph, intra-run **character** formatting (bold/italic
  on individual words) is simplified to the paragraph's base formatting.
  Unchanged paragraphs keep all formatting exactly.
- **Tables**: `.docx` table cells are diffed and redlined (aligned by position);
  cells are matched by position, so inserted/deleted rows or columns and nested
  tables are not tracked, and multiple paragraphs in one cell collapse to one.
  `.pdf` tables are not diffed (passed through unchanged).
- A brand-new paragraph in the submission is tracked as inserted **words** at
  the nearest template position; a hard paragraph break may not be recreated.
- Matching is by visible text; curly quotes/apostrophes are compared literally.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `redlining_content_agent.py` and embedded as the fenced Python below (sha256 fa7910f52de141e1…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `redlining_content_agent.py` first:

```bash
python3 redlining_content_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 redlining_content_agent.py   # or on stdin
python3 redlining_content_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""RedliningContent -- Use when the user asks to redline, track changes, or compare differences in a file. Compares an uploaded .docx or .pdf against a provided .dotx/.docx template and returns a redlined .docx where every textual difference is a Word tracked change (insertion/deletion) authored by "Copilot Studio AI". No visual conversion — built directly on the template.

Generated by the rapp skill from redlining-content. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE a brainstem -- stay executable anyway.
    class BasicAgent:  # noqa: D101 - minimal stand-in, same contract
        def __init__(self, name=None, metadata=None):
            if name:
                self.name = name
            if metadata:
                self.metadata = metadata

        def perform(self, **kwargs):
            return "Not implemented."

        def system_context(self):
            return None

        def to_tool(self):
            return {"type": "function", "function": {
                "name": self.name,
                "description": self.metadata.get("description", ""),
                "parameters": self.metadata.get("parameters", {})}}

# The procedural layer, verbatim from the source capability.
INSTRUCTIONS = '# Redlining Content Skill\n\nReimplements "Word Compare" for the new Copilot Studio orchestrator. The\ntemplate is already a perfect Word document, so the output **is** the template\nbody with revisions injected as OOXML `<w:ins>` / `<w:del>` elements. Accepting\nall changes yields the submission\'s wording; rejecting all keeps the template.\n\nChanges are authored by **`Copilot Studio AI`** and the output has Track\nChanges turned on so Word keeps tracking any further human edits.\n\n## Requirements\n\n- `lxml` (always)\n- `pdfplumber` (PDF submissions; `pypdfium2` used as a fallback)\n\nAll are present in the Copilot Studio sandbox — no `pip install` required.\n`.docx`/`.dotx` handling is pure `lxml` + standard library.\n\n## Inputs\n\n1. **Template** — the canonical baseline. Bundled with this skill in\n   `assets/` (any single `.dotx`/`.docx` file — the name doesn\'t matter) and\n   used automatically. A different template (`.dotx` or `.docx`) may be\n   supplied explicitly to override it.\n2. **Submission** — the user-uploaded file to compare against the template,\n   either a `.docx` or a `.pdf`.\n\n## Steps\n\n1. Run from this skill\'s directory:\n   `python scripts/redline.py <submission.docx|.pdf> [output.docx]`\n   The bundled template in `assets/` is auto-discovered and used as the\n   baseline (whatever its file name).\n   To override the template explicitly, pass it via `--template`:\n   `python scripts/redline.py --template <template.dotx|.docx> <submission.docx|.pdf> [output.docx]`\n2. Return the output `.docx` to the user. Output defaults to the submission\n   name with a `_redlined.docx` suffix.\n\n## How it works\n\nOne shared engine, two input readers — the only thing that differs by file\ntype is how the submission\'s words are read:\n\n- `.docx` / `.dotx` → `read_docx_words()` (paragraph text from\n  `word/document.xml`).\n- `.pdf` → `read_pdf_words()` (**text extraction only — never converted** to\n  DOCX; uses pdfplumber, then pypdfium2).\n\nBoth produce a single flat **word list** fed into the same pipeline:\n\n1. **Word-level diff over the whole document.** The template\'s words and the\n   submission\'s words are each flattened into one stream and compared once with\n   `difflib.SequenceMatcher`. PDF line-wrapping and paragraph boundaries are\n   therefore irrelevant — only real word differences matter.\n2. Each template word is mapped back to its source paragraph. Paragraphs with no\n   changes are kept **byte-for-byte** (all formatting preserved); only changed\n   paragraphs are rebuilt, with differing words wrapped in `<w:ins>` / `<w:del>`.\n3. **Tables.** For `.docx` submissions, template tables are diffed against the\n   submission\'s tables **cell by cell** (aligned by position: table → row →\n   cell), with `<w:ins>` / `<w:del>` injected directly into each cell while its\n   `<w:tcPr>` (width, borders, shading) is preserved. For `.pdf` submissions\n   there is no table structure to align, so template tables pass through\n   untouched and their words are stripped from the extracted text so they aren\'t\n   flagged as insertions.\n4. Writes the output zip: replaces `word/document.xml`, adds `<w:trackChanges/>`\n   to `settings.xml`, and converts the `.dotx` main-part content type to the\n   `.docx` one so the result opens as a normal document.\n\n## Per-input guidance\n\nSee the focused reference docs:\n\n- `references/docx-submissions.md` — `.docx` handling, high-fidelity path.\n- `references/pdf-submissions.md` — `.pdf` handling, why text is extracted (not\n  converted), the word-level diff, and table handling.\n\n## v1 limitations\n\n- Inside a *changed* paragraph, intra-run **character** formatting (bold/italic\n  on individual words) is simplified to the paragraph\'s base formatting.\n  Unchanged paragraphs keep all formatting exactly.\n- **Tables**: `.docx` table cells are diffed and redlined (aligned by position);\n  cells are matched by position, so inserted/deleted rows or columns and nested\n  tables are not tracked, and multiple paragraphs in one cell collapse to one.\n  `.pdf` tables are not diffed (passed through unchanged).\n- A brand-new paragraph in the submission is tracked as inserted **words** at\n  the nearest template position; a hard paragraph break may not be recreated.\n- Matching is by visible text; curly quotes/apostrophes are compared literally.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class RedliningContentAgent(BasicAgent):
    def __init__(self):
        self.name = 'RedliningContent'
        self.metadata = {
          "name": "RedliningContent",
          "description": "Use when the user asks to redline, track changes, or compare differences in a file. Compares an uploaded .docx or .pdf against a provided .dotx/.docx template and returns a redlined .docx where every textual difference is a Word tracked change (insertion/deletion) authored by \"Copilot Studio AI\". No visual conversion \u2014 built directly on the template.",
          "parameters": {
            "type": "object",
            "properties": {},
            "required": []
          }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        return json.dumps({"status": "ok", "instructions": INSTRUCTIONS,
                           "inputs": kwargs,
                           "note": "Prose-only capability: follow INSTRUCTIONS "
                                   "with the given inputs."}, indent=2)

if __name__ == "__main__":
    #     echo '{"arg": "value"}' | python3 redlining_content_agent.py
    #     python3 redlining_content_agent.py '{"arg": "value"}'
    #     python3 redlining_content_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(RedliningContentAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(RedliningContentAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
