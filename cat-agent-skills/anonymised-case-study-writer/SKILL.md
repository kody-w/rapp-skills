---
name: "anonymised-case-study-writer"
description: "Use this skill when the user asks to create, improve, anonymise, structure, or publish a client case study, success story, engagement summary, or transformation story."
---

# Anonymised Case Study Writer

Use this skill to create credible, anonymised case studies from engagement notes, interview notes, project summaries, outcomes, or source documents.

## Core rules

1. **Protect confidentiality.** Remove or generalise names, client identifiers, locations, internal programme names, system names, and commercially sensitive details unless the user explicitly says they are public.
2. **Do not invent outcomes.** Only include outcomes, metrics, timelines, and benefits that appear in the source material or are supplied by the user.
3. **Preserve credibility.** Prefer specific operational detail over vague marketing claims, while keeping the client anonymised.
4. **Make the story reusable.** Structure the case study so it can be used in proposals, webpages, thought leadership, sales conversations, and internal learning.
5. **Separate unknowns.** If outcomes or proof points are missing, include a short "Evidence gaps" section rather than fabricating.

## Default anonymisation pattern

Use neutral descriptors such as:

- A large public sector organisation.
- A global consumer goods company.
- A regulated financial services organisation.
- A national healthcare provider.
- A multinational energy business.

Only describe sector, scale, geography, and technology where the source material supports it and doing so does not identify the client.

## Workflow

1. Read all supplied source material.
2. Extract the engagement context, problem, constraints, intervention, outcomes, and lessons.
3. Identify any confidential or identifying details and replace them with safe descriptors.
4. Draft the case study using the structure below.
5. Check every claim against the source material.
6. Add evidence gaps or suggested follow-up questions only where needed.
7. Return copy-ready Markdown.

## Default structure

```markdown
# [Case study title]

## At a glance

| Field | Summary |
|---|---|
| Client type | [Anonymised descriptor] |
| Sector | [Sector if known] |
| Challenge | [One-sentence challenge] |
| Work delivered | [One-sentence intervention] |
| Outcome | [Evidence-backed outcome or "Outcome evidence not provided"] |

## Context

[What was happening and why it mattered.]

## The challenge

[The specific business, operating, adoption, governance, delivery, or technology problem.]

## What we did

[Practical work performed. Use bullets only where they improve clarity.]

## What changed

[Evidence-backed outcomes, capability shifts, decisions enabled, delivery improvements, or learning generated.]

## Why it mattered

[Business relevance and wider lesson.]

## Reusable insight

[The portable lesson other organisations can learn from this case.]

## Evidence gaps

- [Only include if relevant.]
```

## Style guidance

- Write in a human, experienced, consultancy-literate voice.
- Avoid exaggerated sales language.
- Avoid implying certainty where the source only suggests possibility.
- Make the piece useful even if formal metrics are unavailable.
- Keep paragraphs short enough for web reading.


## References

This skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.

- `references/anonymisation-checklist.md` - use this when additional structure, examples, or checks are useful for the task.

## Quality checklist

Before responding, check:

- No client-confidential detail has leaked.
- Every outcome is backed by supplied evidence.
- The case study has a clear before / intervention / after shape.
- The writing is credible and not generic.
- Evidence gaps are visible rather than hidden.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `anonymised_case_study_writer_agent.py` and embedded as the fenced Python below (sha256 df30ec64bf2a16ee…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `anonymised_case_study_writer_agent.py` first:

```bash
python3 anonymised_case_study_writer_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 anonymised_case_study_writer_agent.py   # or on stdin
python3 anonymised_case_study_writer_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""AnonymisedCaseStudyWriter -- Use this skill when the user asks to create, improve, anonymise, structure, or publish a client case study, success story, engagement summary, or transformation story.

Generated by the rapp skill from anonymised-case-study-writer. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Anonymised Case Study Writer\n\nUse this skill to create credible, anonymised case studies from engagement notes, interview notes, project summaries, outcomes, or source documents.\n\n## Core rules\n\n1. **Protect confidentiality.** Remove or generalise names, client identifiers, locations, internal programme names, system names, and commercially sensitive details unless the user explicitly says they are public.\n2. **Do not invent outcomes.** Only include outcomes, metrics, timelines, and benefits that appear in the source material or are supplied by the user.\n3. **Preserve credibility.** Prefer specific operational detail over vague marketing claims, while keeping the client anonymised.\n4. **Make the story reusable.** Structure the case study so it can be used in proposals, webpages, thought leadership, sales conversations, and internal learning.\n5. **Separate unknowns.** If outcomes or proof points are missing, include a short "Evidence gaps" section rather than fabricating.\n\n## Default anonymisation pattern\n\nUse neutral descriptors such as:\n\n- A large public sector organisation.\n- A global consumer goods company.\n- A regulated financial services organisation.\n- A national healthcare provider.\n- A multinational energy business.\n\nOnly describe sector, scale, geography, and technology where the source material supports it and doing so does not identify the client.\n\n## Workflow\n\n1. Read all supplied source material.\n2. Extract the engagement context, problem, constraints, intervention, outcomes, and lessons.\n3. Identify any confidential or identifying details and replace them with safe descriptors.\n4. Draft the case study using the structure below.\n5. Check every claim against the source material.\n6. Add evidence gaps or suggested follow-up questions only where needed.\n7. Return copy-ready Markdown.\n\n## Default structure\n\n```markdown\n# [Case study title]\n\n## At a glance\n\n| Field | Summary |\n|---|---|\n| Client type | [Anonymised descriptor] |\n| Sector | [Sector if known] |\n| Challenge | [One-sentence challenge] |\n| Work delivered | [One-sentence intervention] |\n| Outcome | [Evidence-backed outcome or "Outcome evidence not provided"] |\n\n## Context\n\n[What was happening and why it mattered.]\n\n## The challenge\n\n[The specific business, operating, adoption, governance, delivery, or technology problem.]\n\n## What we did\n\n[Practical work performed. Use bullets only where they improve clarity.]\n\n## What changed\n\n[Evidence-backed outcomes, capability shifts, decisions enabled, delivery improvements, or learning generated.]\n\n## Why it mattered\n\n[Business relevance and wider lesson.]\n\n## Reusable insight\n\n[The portable lesson other organisations can learn from this case.]\n\n## Evidence gaps\n\n- [Only include if relevant.]\n```\n\n## Style guidance\n\n- Write in a human, experienced, consultancy-literate voice.\n- Avoid exaggerated sales language.\n- Avoid implying certainty where the source only suggests possibility.\n- Make the piece useful even if formal metrics are unavailable.\n- Keep paragraphs short enough for web reading.\n\n\n## References\n\nThis skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.\n\n- `references/anonymisation-checklist.md` - use this when additional structure, examples, or checks are useful for the task.\n\n## Quality checklist\n\nBefore responding, check:\n\n- No client-confidential detail has leaked.\n- Every outcome is backed by supplied evidence.\n- The case study has a clear before / intervention / after shape.\n- The writing is credible and not generic.\n- Evidence gaps are visible rather than hidden.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class AnonymisedCaseStudyWriterAgent(BasicAgent):
    def __init__(self):
        self.name = 'AnonymisedCaseStudyWriter'
        self.metadata = {
          "name": "AnonymisedCaseStudyWriter",
          "description": "Use this skill when the user asks to create, improve, anonymise, structure, or publish a client case study, success story, engagement summary, or transformation story.",
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
    #     echo '{"arg": "value"}' | python3 anonymised_case_study_writer_agent.py
    #     python3 anonymised_case_study_writer_agent.py '{"arg": "value"}'
    #     python3 anonymised_case_study_writer_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(AnonymisedCaseStudyWriterAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(AnonymisedCaseStudyWriterAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
