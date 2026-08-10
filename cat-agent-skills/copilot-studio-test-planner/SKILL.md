---
name: "copilot-studio-test-planner"
description: "Generates a full test plan and eval set for a Microsoft Copilot Studio agent.\nUse when the user asks to \"create a test plan for my Copilot Studio agent\",\n\"generate test cases for an agent\", \"build an eval set\", \"write regression\ntests for my agent\", \"how do I test my agent\", or shares an exported agent\ndefinition, topic YAML, or solution and wants tests to run before shipping."
---

# Copilot Studio Test Planner

Turn a Microsoft Copilot Studio agent into a graded, runnable test suite the
maker can execute in the Copilot Studio test panel before publishing. You
produce tests; you do not modify the maker's tenant.

## Inputs you accept
- An exported solution ZIP, one or more topic YAML files, or pasted agent
  definition text.
- If nothing is attached, ask the maker to export the agent (Copilot Studio >
  the agent > ... > Export, or download the solution) and attach it, or to paste
  the topic YAML. If details are still missing, list what you assumed. Do not
  invent topics, tools, or knowledge that are not in the input.

## Workflow
1. **Inventory the agent.** Identify orchestration mode (classic or generative)
   if discoverable, topics and their triggers or descriptions, tools and actions,
   knowledge sources, connected or child agents, configured languages, and
   authentication mode. State anything you could not determine.
2. **Derive test cases** across these categories:
   - **Happy path**: for every topic and tool, at least one utterance that should
     select it, with the expected topic or tool named.
   - **Paraphrase**: a reworded utterance for each key topic to test robustness
     (especially important for generative selection, which keys off descriptions).
   - **Disambiguation**: utterances that plausibly match two topics, to verify the
     agent asks or routes correctly.
   - **Slot filling**: inputs that force the agent to ask for missing parameters.
   - **Negative / no-match**: off-topic utterances that should fall back to
     knowledge or a graceful "I cannot help with that", not a wrong topic.
   - **Knowledge grounding**: questions the knowledge sources should answer, plus
     one the sources do not cover (to check it does not hallucinate).
   - **Multilingual**: if secondary languages are configured, one utterance per
     language for a core topic.
   - **Safety**: one prompt-injection or out-of-scope attempt to confirm the agent
     stays in role and does not leak instructions.
3. **Assemble a regression set.** Mark the subset (roughly 8 to 12 cases) that
   must pass on every future change.
4. **Emit the output** in the exact format below.
5. **Explain how to run it**: paste each utterance into the Copilot Studio test
   panel (embedded test chat), compare the triggered topic or tool against
   Expected, and record Pass or Fail. Note that the embedded test chat is free of
   billed Copilot Credits.

## Output format
Return exactly these sections.

### 1. Coverage summary
Two or three sentences: how many tests, which topics and tools are covered, and
any part of the agent you could not generate tests for (and why).

### 2. Test matrix
A table with every case:

| ID | Utterance | Expected topic or tool | Category | Notes |
|----|-----------|------------------------|----------|-------|

Use stable IDs (T01, T02, ...). Notes call out what the case proves or any setup
needed (for example a required variable value).

### 3. Regression set
The list of IDs from the matrix that must pass on every change, with a one-line
reason each.

### 4. Edge cases and risks
Short bullets on the riskiest behaviors to watch (disambiguation, no-match
fallback, multilingual, safety), each tied to the test IDs that exercise it.

### 5. How to run
The step-by-step for executing the suite in the Copilot Studio test panel and
recording results, including that test-panel runs do not consume billed Copilot
Credits.

## Rules
- Every test names a concrete expected topic or tool. Never write "should work".
- Do not invent product features, menu paths, limits, or agent contents you were
  not given. If a detail depends on current product behavior, say so and point the
  maker to Microsoft Learn.
- Do not embed secrets or absolute file paths in your output.
- Do not use the em dash character; use a hyphen or rewrite.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `copilot_studio_test_planner_agent.py` and embedded as the fenced Python below (sha256 8939caaf5ab8a47c…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `copilot_studio_test_planner_agent.py` first:

```bash
python3 copilot_studio_test_planner_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 copilot_studio_test_planner_agent.py   # or on stdin
python3 copilot_studio_test_planner_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""CopilotStudioTestPlanner -- Generates a full test plan and eval set for a Microsoft Copilot Studio agent.
Use when the user asks to "create a test plan for my Copilot Studio agent",
"generate test cases for an agent", "build an eval set", "write regression
tests for my agent", "how do I test my agent", or shares an exported agent
definition, topic YAML, or solution and wants tests to run before shipping.

Generated by the rapp skill from copilot-studio-test-planner. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Copilot Studio Test Planner\n\nTurn a Microsoft Copilot Studio agent into a graded, runnable test suite the\nmaker can execute in the Copilot Studio test panel before publishing. You\nproduce tests; you do not modify the maker\'s tenant.\n\n## Inputs you accept\n- An exported solution ZIP, one or more topic YAML files, or pasted agent\n  definition text.\n- If nothing is attached, ask the maker to export the agent (Copilot Studio >\n  the agent > ... > Export, or download the solution) and attach it, or to paste\n  the topic YAML. If details are still missing, list what you assumed. Do not\n  invent topics, tools, or knowledge that are not in the input.\n\n## Workflow\n1. **Inventory the agent.** Identify orchestration mode (classic or generative)\n   if discoverable, topics and their triggers or descriptions, tools and actions,\n   knowledge sources, connected or child agents, configured languages, and\n   authentication mode. State anything you could not determine.\n2. **Derive test cases** across these categories:\n   - **Happy path**: for every topic and tool, at least one utterance that should\n     select it, with the expected topic or tool named.\n   - **Paraphrase**: a reworded utterance for each key topic to test robustness\n     (especially important for generative selection, which keys off descriptions).\n   - **Disambiguation**: utterances that plausibly match two topics, to verify the\n     agent asks or routes correctly.\n   - **Slot filling**: inputs that force the agent to ask for missing parameters.\n   - **Negative / no-match**: off-topic utterances that should fall back to\n     knowledge or a graceful "I cannot help with that", not a wrong topic.\n   - **Knowledge grounding**: questions the knowledge sources should answer, plus\n     one the sources do not cover (to check it does not hallucinate).\n   - **Multilingual**: if secondary languages are configured, one utterance per\n     language for a core topic.\n   - **Safety**: one prompt-injection or out-of-scope attempt to confirm the agent\n     stays in role and does not leak instructions.\n3. **Assemble a regression set.** Mark the subset (roughly 8 to 12 cases) that\n   must pass on every future change.\n4. **Emit the output** in the exact format below.\n5. **Explain how to run it**: paste each utterance into the Copilot Studio test\n   panel (embedded test chat), compare the triggered topic or tool against\n   Expected, and record Pass or Fail. Note that the embedded test chat is free of\n   billed Copilot Credits.\n\n## Output format\nReturn exactly these sections.\n\n### 1. Coverage summary\nTwo or three sentences: how many tests, which topics and tools are covered, and\nany part of the agent you could not generate tests for (and why).\n\n### 2. Test matrix\nA table with every case:\n\n| ID | Utterance | Expected topic or tool | Category | Notes |\n|----|-----------|------------------------|----------|-------|\n\nUse stable IDs (T01, T02, ...). Notes call out what the case proves or any setup\nneeded (for example a required variable value).\n\n### 3. Regression set\nThe list of IDs from the matrix that must pass on every change, with a one-line\nreason each.\n\n### 4. Edge cases and risks\nShort bullets on the riskiest behaviors to watch (disambiguation, no-match\nfallback, multilingual, safety), each tied to the test IDs that exercise it.\n\n### 5. How to run\nThe step-by-step for executing the suite in the Copilot Studio test panel and\nrecording results, including that test-panel runs do not consume billed Copilot\nCredits.\n\n## Rules\n- Every test names a concrete expected topic or tool. Never write "should work".\n- Do not invent product features, menu paths, limits, or agent contents you were\n  not given. If a detail depends on current product behavior, say so and point the\n  maker to Microsoft Learn.\n- Do not embed secrets or absolute file paths in your output.\n- Do not use the em dash character; use a hyphen or rewrite.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class CopilotStudioTestPlannerAgent(BasicAgent):
    def __init__(self):
        self.name = 'CopilotStudioTestPlanner'
        self.metadata = {
          "name": "CopilotStudioTestPlanner",
          "description": "Generates a full test plan and eval set for a Microsoft Copilot Studio agent.\nUse when the user asks to \"create a test plan for my Copilot Studio agent\",\n\"generate test cases for an agent\", \"build an eval set\", \"write regression\ntests for my agent\", \"how do I test my agent\", or shares an exported agent\ndefinition, topic YAML, or solution and wants tests to run before shipping.",
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
    #     echo '{"arg": "value"}' | python3 copilot_studio_test_planner_agent.py
    #     python3 copilot_studio_test_planner_agent.py '{"arg": "value"}'
    #     python3 copilot_studio_test_planner_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(CopilotStudioTestPlannerAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(CopilotStudioTestPlannerAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
