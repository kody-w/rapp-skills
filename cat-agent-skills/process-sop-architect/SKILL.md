---
name: "process-sop-architect"
description: "Use this skill whenever the user asks to document, map, standardize, redesign, or improve a business process from notes, transcripts, interviews, or requirements, especially when they need an editable SOP, process map, RACI, controls, improvement backlog, or polished PowerPoint briefing."
---

# Process & SOP Architect

## When to activate this skill
Activate when the user asks to document, map, redesign, standardize, or improve a business process. Typical triggers include: "turn these notes into an SOP", "map our onboarding process", "create a RACI", "document the current state", "identify process gaps", or "create a future-state workflow".

Do NOT activate when:
- The user wants a software architecture diagram rather than a business process.
- The request is only to summarize a meeting without building an operating procedure.
- The user has not supplied enough information to identify the process scope and actors.

## How this skill runs
1. Review the user's source material and build a process specification using `references/process_spec_schema.md`.
2. Ask targeted questions for missing trigger, scope, roles, decisions, exceptions, controls, or outputs. Ask one question at a time.
3. From the skill's root directory (the folder that contains `scripts/` and `references/`), save the specification as `process_spec.json`, and run the commands below from that same directory so the `scripts/` paths resolve. Use this directory rather than `/tmp`, which is not reliably writable in the sandbox.
4. Validate it:
   ```bash
   python scripts/validate_process_spec.py --input process_spec.json
   ```
5. Generate the process pack, including the polished executive PowerPoint briefing:
   ```bash
   python scripts/generate_process_pack.py \
      --input process_spec.json \
      --output-dir process_pack
   ```
6. Return the generated SOP, process map, RACI workbook, improvement backlog, executive summary, and PowerPoint briefing.

## Requirements
- `python-docx` (Word SOP)
- `openpyxl` (Excel RACI and control register)
- `python-pptx` (PowerPoint executive briefing)

These packages are present in the Copilot Studio sandbox — no `pip install` is required. The generators import them at startup and fail fast with a clear error if a dependency is missing, so a partial pack is never reported as complete.

## Required outputs
- Editable Word SOP
- SVG process flow that can be opened in a browser or inserted into Office
- Excel RACI and control register
- CSV improvement backlog
- Markdown executive summary and unresolved-question log
- Editable PowerPoint executive briefing with title slide, snapshot, process flow, role handoffs, controls, risks, roadmap, chart, and next steps

## Workflow the agent must follow
1. Establish whether the user wants current state, future state, or both.
2. Define the process boundary: trigger, start, end, inputs, outputs, and exclusions.
3. Identify roles, systems, decisions, handoffs, exceptions, controls, and evidence.
4. Separate observed facts from assumptions and recommendations.
5. Build a complete process specification.
6. Run validation and resolve errors before generation.
7. Review generated deliverables for traceability and usability.
8. Ensure the PowerPoint uses assertion-style slide titles, separates facts from recommendations, and does not introduce unsupported claims.

## Quality rules
- Use verb-object wording for process steps, such as `Validate request` or `Approve payment`.
- Every step must have an owner.
- Every decision must define both yes and no paths.
- Every control must identify purpose, owner, frequency, and evidence.
- Do not invent policy, legal, regulatory, service-level, or approval requirements.
- Label missing information as `TBD` and include it in the unresolved-question log.
- Distinguish current-state problems from future-state recommendations.
- Do not automate a process merely because automation is possible.
- The presentation must summarize the SOP; it must not replace the SOP or invent new process facts.
- PowerPoint slides should be leadership-ready, concise, and editable.

## Activation examples
- "Create an SOP from this onboarding workshop transcript."
- "Map the complaint-management process and identify control gaps."
- "Turn these process notes into a RACI and future-state improvement plan."
- "Document our invoice exception process for training and audit."

## Run example
```bash
python scripts/validate_process_spec.py --input assets/example_process_spec.json
python scripts/generate_process_pack.py \
  --input assets/example_process_spec.json \
  --output-dir vendor_onboarding_pack

# Generate only the PowerPoint briefing
python scripts/generate_presentation.py \
  --input assets/example_process_spec.json \
  --output-dir vendor_onboarding_pack
```

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `process_sop_architect_agent.py` and embedded as the fenced Python below (sha256 256c90c49138693c…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `process_sop_architect_agent.py` first:

```bash
python3 process_sop_architect_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 process_sop_architect_agent.py   # or on stdin
python3 process_sop_architect_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""ProcessSopArchitect -- Use this skill whenever the user asks to document, map, standardize, redesign, or improve a business process from notes, transcripts, interviews, or requirements, especially when they need an editable SOP, process map, RACI, controls, improvement backlog, or polished PowerPoint briefing.

Generated by the rapp skill from process-sop-architect. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Process & SOP Architect\n\n## When to activate this skill\nActivate when the user asks to document, map, redesign, standardize, or improve a business process. Typical triggers include: "turn these notes into an SOP", "map our onboarding process", "create a RACI", "document the current state", "identify process gaps", or "create a future-state workflow".\n\nDo NOT activate when:\n- The user wants a software architecture diagram rather than a business process.\n- The request is only to summarize a meeting without building an operating procedure.\n- The user has not supplied enough information to identify the process scope and actors.\n\n## How this skill runs\n1. Review the user\'s source material and build a process specification using `references/process_spec_schema.md`.\n2. Ask targeted questions for missing trigger, scope, roles, decisions, exceptions, controls, or outputs. Ask one question at a time.\n3. From the skill\'s root directory (the folder that contains `scripts/` and `references/`), save the specification as `process_spec.json`, and run the commands below from that same directory so the `scripts/` paths resolve. Use this directory rather than `/tmp`, which is not reliably writable in the sandbox.\n4. Validate it:\n   ```bash\n   python scripts/validate_process_spec.py --input process_spec.json\n   ```\n5. Generate the process pack, including the polished executive PowerPoint briefing:\n   ```bash\n   python scripts/generate_process_pack.py \\\n      --input process_spec.json \\\n      --output-dir process_pack\n   ```\n6. Return the generated SOP, process map, RACI workbook, improvement backlog, executive summary, and PowerPoint briefing.\n\n## Requirements\n- `python-docx` (Word SOP)\n- `openpyxl` (Excel RACI and control register)\n- `python-pptx` (PowerPoint executive briefing)\n\nThese packages are present in the Copilot Studio sandbox — no `pip install` is required. The generators import them at startup and fail fast with a clear error if a dependency is missing, so a partial pack is never reported as complete.\n\n## Required outputs\n- Editable Word SOP\n- SVG process flow that can be opened in a browser or inserted into Office\n- Excel RACI and control register\n- CSV improvement backlog\n- Markdown executive summary and unresolved-question log\n- Editable PowerPoint executive briefing with title slide, snapshot, process flow, role handoffs, controls, risks, roadmap, chart, and next steps\n\n## Workflow the agent must follow\n1. Establish whether the user wants current state, future state, or both.\n2. Define the process boundary: trigger, start, end, inputs, outputs, and exclusions.\n3. Identify roles, systems, decisions, handoffs, exceptions, controls, and evidence.\n4. Separate observed facts from assumptions and recommendations.\n5. Build a complete process specification.\n6. Run validation and resolve errors before generation.\n7. Review generated deliverables for traceability and usability.\n8. Ensure the PowerPoint uses assertion-style slide titles, separates facts from recommendations, and does not introduce unsupported claims.\n\n## Quality rules\n- Use verb-object wording for process steps, such as `Validate request` or `Approve payment`.\n- Every step must have an owner.\n- Every decision must define both yes and no paths.\n- Every control must identify purpose, owner, frequency, and evidence.\n- Do not invent policy, legal, regulatory, service-level, or approval requirements.\n- Label missing information as `TBD` and include it in the unresolved-question log.\n- Distinguish current-state problems from future-state recommendations.\n- Do not automate a process merely because automation is possible.\n- The presentation must summarize the SOP; it must not replace the SOP or invent new process facts.\n- PowerPoint slides should be leadership-ready, concise, and editable.\n\n## Activation examples\n- "Create an SOP from this onboarding workshop transcript."\n- "Map the complaint-management process and identify control gaps."\n- "Turn these process notes into a RACI and future-state improvement plan."\n- "Document our invoice exception process for training and audit."\n\n## Run example\n```bash\npython scripts/validate_process_spec.py --input assets/example_process_spec.json\npython scripts/generate_process_pack.py \\\n  --input assets/example_process_spec.json \\\n  --output-dir vendor_onboarding_pack\n\n# Generate only the PowerPoint briefing\npython scripts/generate_presentation.py \\\n  --input assets/example_process_spec.json \\\n  --output-dir vendor_onboarding_pack\n```'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class ProcessSopArchitectAgent(BasicAgent):
    def __init__(self):
        self.name = 'ProcessSopArchitect'
        self.metadata = {
          "name": "ProcessSopArchitect",
          "description": "Use this skill whenever the user asks to document, map, standardize, redesign, or improve a business process from notes, transcripts, interviews, or requirements, especially when they need an editable SOP, process map, RACI, controls, improvement backlog, or polished PowerPoint briefing.",
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
    #     echo '{"arg": "value"}' | python3 process_sop_architect_agent.py
    #     python3 process_sop_architect_agent.py '{"arg": "value"}'
    #     python3 process_sop_architect_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(ProcessSopArchitectAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(ProcessSopArchitectAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
