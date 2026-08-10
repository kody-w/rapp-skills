---
name: "content-quality-auditor"
description: "Use this skill when the user asks to assess, audit, score, review, improve, prioritise, or quality-check content, documents, pages, posts, decks, or reusable artefacts."
---

# Content Quality Auditor

Use this skill to assess content quality in a repeatable, evidence-led way and produce a prioritised improvement plan.

## What to audit

The skill can be used for:

- Individual documents, pages, posts, decks, scripts, or templates.
- Groups of related artefacts.
- Content libraries where consistency and reuse matter.
- Draft material before publication.

## Evidence rules

- Base the audit only on content the user provides or content available through the agent's connected sources.
- Do not infer missing facts, usage statistics, or business impact.
- If you cannot access a referenced artefact, state that limitation and assess only what is available.
- Separate observed evidence from suggested improvements.

## Default seven-dimension rubric

Score each dimension from 0 to 5.

| Score | Meaning |
|---:|---|
| 0 | Not present or unusable. |
| 1 | Present but weak, confusing, or incomplete. |
| 2 | Basic but inconsistent or hard to reuse. |
| 3 | Usable with moderate improvement needed. |
| 4 | Strong with minor refinement needed. |
| 5 | Publication-ready or operationally robust. |

Assess these dimensions:

1. **Purpose and audience clarity** - Is the content clear about who it is for and what it helps them do?
2. **Structure and navigation** - Is the content logically organised and easy to scan?
3. **Evidence and specificity** - Are claims supported by examples, data, sources, or concrete detail?
4. **Practical usefulness** - Does the content help the reader make a decision or take action?
5. **Consistency and standards alignment** - Does it follow the expected terminology, design, tone, and formatting conventions?
6. **Reusability and modularity** - Can the content be reused, adapted, or maintained without excessive rework?
7. **Completeness and next action** - Are important gaps, dependencies, risks, and follow-up actions visible?

If the user supplies a different rubric, use their rubric instead.

## Workflow

1. Identify the artefact or artefacts being audited.
2. Confirm the intended audience and purpose from the available material.
3. Apply the rubric dimension by dimension.
4. Note specific evidence for each score.
5. Identify priority fixes, separating major blockers from polish.
6. Recommend a practical sequence of improvements.
7. If auditing multiple artefacts, provide a comparative summary and prioritised backlog.

## Output format

Use this format unless the user requests another structure:

```markdown
## Audit summary

Overall assessment: [Short judgement]
Overall score: [Average]/5
Priority: [High / Medium / Low]

## Scorecard

| Dimension | Score /5 | Evidence | Recommended improvement |
|---|---:|---|---|
| Purpose and audience clarity |  |  |  |
| Structure and navigation |  |  |  |
| Evidence and specificity |  |  |  |
| Practical usefulness |  |  |  |
| Consistency and standards alignment |  |  |  |
| Reusability and modularity |  |  |  |
| Completeness and next action |  |  |  |

## Highest-value fixes

1. [Fix]
2. [Fix]
3. [Fix]

## Suggested next version

[Concise recommended direction]
```

## Multi-artefact output

For multiple artefacts, add:

```markdown
## Prioritised improvement backlog

| Priority | Artefact | Issue | Recommended action | Effort | Impact |
|---|---|---|---|---|---|
```


## References

This skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.

- `references/scoring-rubric.md` - use this when additional structure, examples, or checks are useful for the task.

## Quality checklist

Before responding, check:

- Scores are justified by evidence.
- Recommendations are specific and actionable.
- No inaccessible content is treated as reviewed.
- The output helps the user decide what to improve next.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `content_quality_auditor_agent.py` and embedded as the fenced Python below (sha256 3d8cce90ef5a51c8…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `content_quality_auditor_agent.py` first:

```bash
python3 content_quality_auditor_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 content_quality_auditor_agent.py   # or on stdin
python3 content_quality_auditor_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""ContentQualityAuditor -- Use this skill when the user asks to assess, audit, score, review, improve, prioritise, or quality-check content, documents, pages, posts, decks, or reusable artefacts.

Generated by the rapp skill from content-quality-auditor. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = "# Content Quality Auditor\n\nUse this skill to assess content quality in a repeatable, evidence-led way and produce a prioritised improvement plan.\n\n## What to audit\n\nThe skill can be used for:\n\n- Individual documents, pages, posts, decks, scripts, or templates.\n- Groups of related artefacts.\n- Content libraries where consistency and reuse matter.\n- Draft material before publication.\n\n## Evidence rules\n\n- Base the audit only on content the user provides or content available through the agent's connected sources.\n- Do not infer missing facts, usage statistics, or business impact.\n- If you cannot access a referenced artefact, state that limitation and assess only what is available.\n- Separate observed evidence from suggested improvements.\n\n## Default seven-dimension rubric\n\nScore each dimension from 0 to 5.\n\n| Score | Meaning |\n|---:|---|\n| 0 | Not present or unusable. |\n| 1 | Present but weak, confusing, or incomplete. |\n| 2 | Basic but inconsistent or hard to reuse. |\n| 3 | Usable with moderate improvement needed. |\n| 4 | Strong with minor refinement needed. |\n| 5 | Publication-ready or operationally robust. |\n\nAssess these dimensions:\n\n1. **Purpose and audience clarity** - Is the content clear about who it is for and what it helps them do?\n2. **Structure and navigation** - Is the content logically organised and easy to scan?\n3. **Evidence and specificity** - Are claims supported by examples, data, sources, or concrete detail?\n4. **Practical usefulness** - Does the content help the reader make a decision or take action?\n5. **Consistency and standards alignment** - Does it follow the expected terminology, design, tone, and formatting conventions?\n6. **Reusability and modularity** - Can the content be reused, adapted, or maintained without excessive rework?\n7. **Completeness and next action** - Are important gaps, dependencies, risks, and follow-up actions visible?\n\nIf the user supplies a different rubric, use their rubric instead.\n\n## Workflow\n\n1. Identify the artefact or artefacts being audited.\n2. Confirm the intended audience and purpose from the available material.\n3. Apply the rubric dimension by dimension.\n4. Note specific evidence for each score.\n5. Identify priority fixes, separating major blockers from polish.\n6. Recommend a practical sequence of improvements.\n7. If auditing multiple artefacts, provide a comparative summary and prioritised backlog.\n\n## Output format\n\nUse this format unless the user requests another structure:\n\n```markdown\n## Audit summary\n\nOverall assessment: [Short judgement]\nOverall score: [Average]/5\nPriority: [High / Medium / Low]\n\n## Scorecard\n\n| Dimension | Score /5 | Evidence | Recommended improvement |\n|---|---:|---|---|\n| Purpose and audience clarity |  |  |  |\n| Structure and navigation |  |  |  |\n| Evidence and specificity |  |  |  |\n| Practical usefulness |  |  |  |\n| Consistency and standards alignment |  |  |  |\n| Reusability and modularity |  |  |  |\n| Completeness and next action |  |  |  |\n\n## Highest-value fixes\n\n1. [Fix]\n2. [Fix]\n3. [Fix]\n\n## Suggested next version\n\n[Concise recommended direction]\n```\n\n## Multi-artefact output\n\nFor multiple artefacts, add:\n\n```markdown\n## Prioritised improvement backlog\n\n| Priority | Artefact | Issue | Recommended action | Effort | Impact |\n|---|---|---|---|---|---|\n```\n\n\n## References\n\nThis skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.\n\n- `references/scoring-rubric.md` - use this when additional structure, examples, or checks are useful for the task.\n\n## Quality checklist\n\nBefore responding, check:\n\n- Scores are justified by evidence.\n- Recommendations are specific and actionable.\n- No inaccessible content is treated as reviewed.\n- The output helps the user decide what to improve next."

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class ContentQualityAuditorAgent(BasicAgent):
    def __init__(self):
        self.name = 'ContentQualityAuditor'
        self.metadata = {
          "name": "ContentQualityAuditor",
          "description": "Use this skill when the user asks to assess, audit, score, review, improve, prioritise, or quality-check content, documents, pages, posts, decks, or reusable artefacts.",
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
    #     echo '{"arg": "value"}' | python3 content_quality_auditor_agent.py
    #     python3 content_quality_auditor_agent.py '{"arg": "value"}'
    #     python3 content_quality_auditor_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(ContentQualityAuditorAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(ContentQualityAuditorAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
