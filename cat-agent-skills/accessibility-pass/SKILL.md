---
name: "accessibility-pass"
description: "Use this skill whenever the user asks to check, review, or fix the accessibility of a PowerPoint deck, Word document, HTML page, or Markdown file, and before handing over any deck or document this agent just generated, so it does not ship with missing alt text, untitled slides, or unreadable colour contrast."
---

Review the artefact against Microsoft's Accessibility Checker rules, report what
fails, and fix it on request. Use the rule names below verbatim. They are the
same ones the author sees when they run the checker themselves in Office, so the
findings are recognisable and searchable.

## Instructions

1. Get the file. Supported: `.pptx`, `.docx`, `.html`, `.md`. If the user pasted
   raw HTML or Markdown instead, save it to a file first.

2. Run the bundled checker when a Python environment is available, from the
   skill's own root directory (the folder containing `scripts/`), so the
   relative path resolves:

   ```bash
   python scripts/a11y_check.py <file> --json
   ```

   It needs `python-pptx` for `.pptx` and `python-docx` for `.docx`; HTML and
   Markdown need nothing beyond the standard library. If the environment has
   no Python, or the import fails: for HTML and Markdown, read the file
   directly and check it against the rules below by hand. For `.pptx` and
   `.docx`, that fallback doesn't really work, these are zipped Office XML,
   not something to eyeball as text, so instead say plainly that the file
   couldn't be checked, and ask the user to run Office's own Accessibility
   Checker (File > Info > Check for Issues > Check Accessibility) and share
   what it reports.

3. Add the judgement calls the script deliberately does not make:

   - **Alt text that exists but is useless.** `"image1.png"`, `"chart"`, or a
     filename is a failure even though the attribute is populated. Read every
     alt string and judge whether someone who cannot see the image learns the
     same thing from it.
   - **Wrongly decorative.** Anything marked decorative that actually carries
     information is a failure the script cannot see.
   - **Reading order that is flagged but fine.** The script compares screen-reader
     order with visual top-left order; deliberate multi-column layouts trip it.
     Confirm before reporting.
   - **Meaning carried by colour alone**, such as red/green status dots or "the
     items in orange," which no file-level check can detect.
   - **Captions and transcripts** for embedded audio or video.
   - **Contrast the script skipped.** It only compares explicit RGB values.
     Theme colours, gradients, and picture fills come back unchecked. Report
     them as unchecked, never as passing.

4. Report findings grouped by severity, worst first, one row each:

   | Severity | Rule | Where | Fix |
   | --- | --- | --- | --- |
   | Error | All slides have titles | Slide 4 | Add a title in the title placeholder |

   Open with a one-line count (`3 errors, 5 warnings, 1 tip`). If nothing fails,
   say so and list what could not be checked mechanically.

5. Offer to apply the fixes. Apply directly: adding a missing slide title, adding
   a table header row, rewriting vague link text, adding `lang` to `<html>`,
   fixing heading-level jumps. Ask first before writing alt text for an image
   whose content is uncertain, marking anything decorative, changing colours, or
   restructuring merged tables, since each of those changes meaning or design.

6. Re-run the checker after fixing and report what is left.

## The rules

**Errors**: content that is unusable for someone relying on assistive tech.

- All non-text content has alternative text (alt text)
- Tables specify column header information
- All slides have titles
- All sections have meaningful names *(the bundled script doesn't check this;
  ask the user or inspect the file's sections manually)*
- Document access is not restricted *(the bundled script doesn't check this;
  verify manually whether the file has IRM/password protection applied)*

**Warnings**: content that is hard to use.

- Sufficient contrast between text and background (WCAG AA: 4.5:1 normal text,
  3:1 for text 18pt+ or bold 14pt+)
- Table has a simple structure
- The reading order of the objects on a slide presentation is logical
- Closed captions are included for inserted audio and video
- Hyperlink text is meaningful

**Tips**: content that could be easier to use.

- Slide titles in a deck are unique
- Documents use heading styles
- Document language is set

## Guardrails

- Never invent alt text for an image whose content is unknown. Ask the user what
  it shows, or describe only what surrounding text supports and say the
  description needs confirming.
- Never mark an object decorative to clear a finding. Decorative means it carries
  no information; use it only when that is true.
- Never edit visible wording, layout, or branding beyond what a fix requires.
- Never report an unchecked item as a pass.
- Do not claim WCAG or EN 301 549 conformance. This is a pass over known rules,
  not a certification. A clean result means no *detected* issues.

## Tone

Direct and specific. Name the rule, the location, and the concrete fix. No
lecturing about why accessibility matters; the user already asked.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `accessibility_pass_agent.py` and embedded as the fenced Python below (sha256 dc6327456db3f696…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `accessibility_pass_agent.py` first:

```bash
python3 accessibility_pass_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 accessibility_pass_agent.py   # or on stdin
python3 accessibility_pass_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""AccessibilityPass -- Use this skill whenever the user asks to check, review, or fix the accessibility of a PowerPoint deck, Word document, HTML page, or Markdown file, and before handing over any deck or document this agent just generated, so it does not ship with missing alt text, untitled slides, or unreadable colour contrast.

Generated by the rapp skill from accessibility-pass. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = 'Review the artefact against Microsoft\'s Accessibility Checker rules, report what\nfails, and fix it on request. Use the rule names below verbatim. They are the\nsame ones the author sees when they run the checker themselves in Office, so the\nfindings are recognisable and searchable.\n\n## Instructions\n\n1. Get the file. Supported: `.pptx`, `.docx`, `.html`, `.md`. If the user pasted\n   raw HTML or Markdown instead, save it to a file first.\n\n2. Run the bundled checker when a Python environment is available, from the\n   skill\'s own root directory (the folder containing `scripts/`), so the\n   relative path resolves:\n\n   ```bash\n   python scripts/a11y_check.py <file> --json\n   ```\n\n   It needs `python-pptx` for `.pptx` and `python-docx` for `.docx`; HTML and\n   Markdown need nothing beyond the standard library. If the environment has\n   no Python, or the import fails: for HTML and Markdown, read the file\n   directly and check it against the rules below by hand. For `.pptx` and\n   `.docx`, that fallback doesn\'t really work, these are zipped Office XML,\n   not something to eyeball as text, so instead say plainly that the file\n   couldn\'t be checked, and ask the user to run Office\'s own Accessibility\n   Checker (File > Info > Check for Issues > Check Accessibility) and share\n   what it reports.\n\n3. Add the judgement calls the script deliberately does not make:\n\n   - **Alt text that exists but is useless.** `"image1.png"`, `"chart"`, or a\n     filename is a failure even though the attribute is populated. Read every\n     alt string and judge whether someone who cannot see the image learns the\n     same thing from it.\n   - **Wrongly decorative.** Anything marked decorative that actually carries\n     information is a failure the script cannot see.\n   - **Reading order that is flagged but fine.** The script compares screen-reader\n     order with visual top-left order; deliberate multi-column layouts trip it.\n     Confirm before reporting.\n   - **Meaning carried by colour alone**, such as red/green status dots or "the\n     items in orange," which no file-level check can detect.\n   - **Captions and transcripts** for embedded audio or video.\n   - **Contrast the script skipped.** It only compares explicit RGB values.\n     Theme colours, gradients, and picture fills come back unchecked. Report\n     them as unchecked, never as passing.\n\n4. Report findings grouped by severity, worst first, one row each:\n\n   | Severity | Rule | Where | Fix |\n   | --- | --- | --- | --- |\n   | Error | All slides have titles | Slide 4 | Add a title in the title placeholder |\n\n   Open with a one-line count (`3 errors, 5 warnings, 1 tip`). If nothing fails,\n   say so and list what could not be checked mechanically.\n\n5. Offer to apply the fixes. Apply directly: adding a missing slide title, adding\n   a table header row, rewriting vague link text, adding `lang` to `<html>`,\n   fixing heading-level jumps. Ask first before writing alt text for an image\n   whose content is uncertain, marking anything decorative, changing colours, or\n   restructuring merged tables, since each of those changes meaning or design.\n\n6. Re-run the checker after fixing and report what is left.\n\n## The rules\n\n**Errors**: content that is unusable for someone relying on assistive tech.\n\n- All non-text content has alternative text (alt text)\n- Tables specify column header information\n- All slides have titles\n- All sections have meaningful names *(the bundled script doesn\'t check this;\n  ask the user or inspect the file\'s sections manually)*\n- Document access is not restricted *(the bundled script doesn\'t check this;\n  verify manually whether the file has IRM/password protection applied)*\n\n**Warnings**: content that is hard to use.\n\n- Sufficient contrast between text and background (WCAG AA: 4.5:1 normal text,\n  3:1 for text 18pt+ or bold 14pt+)\n- Table has a simple structure\n- The reading order of the objects on a slide presentation is logical\n- Closed captions are included for inserted audio and video\n- Hyperlink text is meaningful\n\n**Tips**: content that could be easier to use.\n\n- Slide titles in a deck are unique\n- Documents use heading styles\n- Document language is set\n\n## Guardrails\n\n- Never invent alt text for an image whose content is unknown. Ask the user what\n  it shows, or describe only what surrounding text supports and say the\n  description needs confirming.\n- Never mark an object decorative to clear a finding. Decorative means it carries\n  no information; use it only when that is true.\n- Never edit visible wording, layout, or branding beyond what a fix requires.\n- Never report an unchecked item as a pass.\n- Do not claim WCAG or EN 301 549 conformance. This is a pass over known rules,\n  not a certification. A clean result means no *detected* issues.\n\n## Tone\n\nDirect and specific. Name the rule, the location, and the concrete fix. No\nlecturing about why accessibility matters; the user already asked.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class AccessibilityPassAgent(BasicAgent):
    def __init__(self):
        self.name = 'AccessibilityPass'
        self.metadata = {
          "name": "AccessibilityPass",
          "description": "Use this skill whenever the user asks to check, review, or fix the accessibility of a PowerPoint deck, Word document, HTML page, or Markdown file, and before handing over any deck or document this agent just generated, so it does not ship with missing alt text, untitled slides, or unreadable colour contrast.",
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
    #     echo '{"arg": "value"}' | python3 accessibility_pass_agent.py
    #     python3 accessibility_pass_agent.py '{"arg": "value"}'
    #     python3 accessibility_pass_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(AccessibilityPassAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(AccessibilityPassAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
