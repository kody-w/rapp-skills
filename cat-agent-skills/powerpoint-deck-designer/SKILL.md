---
name: "powerpoint-deck-designer"
description: "Creates polished PowerPoint decks from a JSON specification using python-pptx. Designed as a Copilot Studio Skill that runs natively inside the agent container."
license: "MIT"
compatibility: "Copilot Studio Skills Container with Python support"
metadata: {"platforms": ["Copilot Studio"], "author": "Ferran Chopo"}
---

# PowerPoint Deck Designer

## When to activate this skill
Activate whenever the user asks to build, generate, draft, improve or restyle any kind of slide deck or PowerPoint file. Typical triggers include: "create a deck about X", "build me a pitch deck", "draft a training presentation", "make a proposal in PowerPoint", "restyle these slides with our brand", "visualise these numbers as a slide".

Do NOT activate for:
- Word documents or PDF reports (use the doc skill instead)
- Editing an existing uploaded .pptx (unless the user explicitly wants a full rebuild)

## How this skill runs
This agent runs inside a Copilot Studio **Skills container** with a Python interpreter. `python-pptx` is available out of the box. To use the skill:

1. Build a JSON deck specification (see `references/input_schema.md`).
2. Pick a theme slug from `assets/themes.json` (see `references/layouts.md` for available layouts).
3. Save the JSON as `/tmp/spec.json` and run the renderer:
   ```bash
   python scripts/generate_presentation.py \
       --input /tmp/spec.json \
       --output /tmp/deck.pptx \
       --theme <theme-slug> \
       --validate
   ```
4. Return `/tmp/deck.pptx` to the user as a downloadable artifact.

## Design principles the agent must follow
- Consider the subject matter: audience, tone, industry, mood.
- Check for branding: prefer official brand colours when the user names an organisation. If none, pick a theme whose palette matches the topic.
- Use web-safe fonts only (already baked into the themes): Arial, Calibri, Verdana, Georgia, Trebuchet MS, Tahoma.
- Clear hierarchy: title -> section -> content -> closing.
- Readability: minimum body font 14 pt, minimum title 28 pt, contrast >= 4.5:1.

## Charts
This skill can generate native PowerPoint charts (real, editable Office charts - not images). Supported types:
- `column` and `bar` - category comparisons (multiple series allowed). Set `stacked: true` or `stacked: "100"` for stacked / 100% stacked variants.
- `line` - trends over time (multiple series supported; up to ~12 points recommended).
- `pie` and `donut` - parts of a whole (single series only).

Series and slices are colour-coded from the active theme palette (primary, secondary, accent, muted). See `references/input_schema.md` for the JSON shape.

## Colour palette selection
- Corporate / executive briefing -> `executive-blue`
- Tech / product launch on dark background -> `modern-slate`
- Sustainability / environmental -> `sustain-green`
- Startup / creative pitch -> `vibrant-pitch`
- Editorial / minimalist -> `minimal-mono`

## Workflow the agent must follow
1. Understand the objective, audience, tone, and source material.
2. Draft a short storyline (3-15 slides) *before* writing JSON.
3. State your theme choice and reasoning to the user in one line.
4. Build a JSON deck spec following `references/input_schema.md`.
5. Run the script in the container with `--validate`.
6. If validation warnings appear, shorten text or switch to a layout with more room (see `references/layouts.md`), then re-render.
7. Return the .pptx to the user; offer to iterate on colours, wording, layout or chart type.

## Quality rules
- One main message per slide.
- <= 6 bullets per slide, <= 14 words per bullet.
- Use `agenda` for agendas, `cards` for short concepts, `chart` for numeric data.
- Do not invent numbers. Mark assumptions in `notes` (speaker notes).

## Activation examples
- "Create a 10-slide investor pitch for our KONE modernisation offering" -> theme `executive-blue`
- "Draft an internal training deck on Power Platform governance" -> theme `minimal-mono`
- "Build a bold launch deck for our new sustainability product" -> theme `sustain-green`
- "Visualise Q1-Q4 backlog progression as a stacked column chart" -> `chart` layout, `stacked: true`

## Run example (executes inside the Copilot Studio Skills container)
```bash
python scripts/generate_presentation.py \
    --input assets/example_request.json \
    --output /tmp/kone_adoption.pptx \
    --theme executive-blue \
    --validate
```

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `powerpoint_deck_designer_agent.py` and embedded as the fenced Python below (sha256 d076d5955a1c94e4…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `powerpoint_deck_designer_agent.py` first:

```bash
python3 powerpoint_deck_designer_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 powerpoint_deck_designer_agent.py   # or on stdin
python3 powerpoint_deck_designer_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""PowerpointDeckDesigner -- Creates polished PowerPoint decks from a JSON specification using python-pptx. Designed as a Copilot Studio Skill that runs natively inside the agent container.

Generated by the rapp skill from powerpoint-deck-designer. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# PowerPoint Deck Designer\n\n## When to activate this skill\nActivate whenever the user asks to build, generate, draft, improve or restyle any kind of slide deck or PowerPoint file. Typical triggers include: "create a deck about X", "build me a pitch deck", "draft a training presentation", "make a proposal in PowerPoint", "restyle these slides with our brand", "visualise these numbers as a slide".\n\nDo NOT activate for:\n- Word documents or PDF reports (use the doc skill instead)\n- Editing an existing uploaded .pptx (unless the user explicitly wants a full rebuild)\n\n## How this skill runs\nThis agent runs inside a Copilot Studio **Skills container** with a Python interpreter. `python-pptx` is available out of the box. To use the skill:\n\n1. Build a JSON deck specification (see `references/input_schema.md`).\n2. Pick a theme slug from `assets/themes.json` (see `references/layouts.md` for available layouts).\n3. Save the JSON as `/tmp/spec.json` and run the renderer:\n   ```bash\n   python scripts/generate_presentation.py \\\n       --input /tmp/spec.json \\\n       --output /tmp/deck.pptx \\\n       --theme <theme-slug> \\\n       --validate\n   ```\n4. Return `/tmp/deck.pptx` to the user as a downloadable artifact.\n\n## Design principles the agent must follow\n- Consider the subject matter: audience, tone, industry, mood.\n- Check for branding: prefer official brand colours when the user names an organisation. If none, pick a theme whose palette matches the topic.\n- Use web-safe fonts only (already baked into the themes): Arial, Calibri, Verdana, Georgia, Trebuchet MS, Tahoma.\n- Clear hierarchy: title -> section -> content -> closing.\n- Readability: minimum body font 14 pt, minimum title 28 pt, contrast >= 4.5:1.\n\n## Charts\nThis skill can generate native PowerPoint charts (real, editable Office charts - not images). Supported types:\n- `column` and `bar` - category comparisons (multiple series allowed). Set `stacked: true` or `stacked: "100"` for stacked / 100% stacked variants.\n- `line` - trends over time (multiple series supported; up to ~12 points recommended).\n- `pie` and `donut` - parts of a whole (single series only).\n\nSeries and slices are colour-coded from the active theme palette (primary, secondary, accent, muted). See `references/input_schema.md` for the JSON shape.\n\n## Colour palette selection\n- Corporate / executive briefing -> `executive-blue`\n- Tech / product launch on dark background -> `modern-slate`\n- Sustainability / environmental -> `sustain-green`\n- Startup / creative pitch -> `vibrant-pitch`\n- Editorial / minimalist -> `minimal-mono`\n\n## Workflow the agent must follow\n1. Understand the objective, audience, tone, and source material.\n2. Draft a short storyline (3-15 slides) *before* writing JSON.\n3. State your theme choice and reasoning to the user in one line.\n4. Build a JSON deck spec following `references/input_schema.md`.\n5. Run the script in the container with `--validate`.\n6. If validation warnings appear, shorten text or switch to a layout with more room (see `references/layouts.md`), then re-render.\n7. Return the .pptx to the user; offer to iterate on colours, wording, layout or chart type.\n\n## Quality rules\n- One main message per slide.\n- <= 6 bullets per slide, <= 14 words per bullet.\n- Use `agenda` for agendas, `cards` for short concepts, `chart` for numeric data.\n- Do not invent numbers. Mark assumptions in `notes` (speaker notes).\n\n## Activation examples\n- "Create a 10-slide investor pitch for our KONE modernisation offering" -> theme `executive-blue`\n- "Draft an internal training deck on Power Platform governance" -> theme `minimal-mono`\n- "Build a bold launch deck for our new sustainability product" -> theme `sustain-green`\n- "Visualise Q1-Q4 backlog progression as a stacked column chart" -> `chart` layout, `stacked: true`\n\n## Run example (executes inside the Copilot Studio Skills container)\n```bash\npython scripts/generate_presentation.py \\\n    --input assets/example_request.json \\\n    --output /tmp/kone_adoption.pptx \\\n    --theme executive-blue \\\n    --validate\n```'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class PowerpointDeckDesignerAgent(BasicAgent):
    def __init__(self):
        self.name = 'PowerpointDeckDesigner'
        self.metadata = {
          "name": "PowerpointDeckDesigner",
          "description": "Creates polished PowerPoint decks from a JSON specification using python-pptx. Designed as a Copilot Studio Skill that runs natively inside the agent container.",
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
    #     echo '{"arg": "value"}' | python3 powerpoint_deck_designer_agent.py
    #     python3 powerpoint_deck_designer_agent.py '{"arg": "value"}'
    #     python3 powerpoint_deck_designer_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(PowerpointDeckDesignerAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(PowerpointDeckDesignerAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
