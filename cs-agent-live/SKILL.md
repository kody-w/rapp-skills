---
name: "cs-agent-live"
description: "Take a Copilot Studio agent that was generated and deployed by the RAPP Factory and make it actually answer from its data \u2014 then make it presentable enough to film. Covers the MCP attach, the auth mode that everyone gets wrong, the silent name truncation, and the toggle that hides the build machinery. Trigger when a deployed agent \"has no data\", reports 404 from its data server, or looks machine-generated on screen."
---

# Making a deployed Copilot Studio agent live

A Factory deploy lands two solutions and publishes them, and the agent still
answers "I don't have access to that data". Nothing is broken. Four things are
missing, and only one of them is in the Factory's own manual steps.

**claude-in-chrome is the law here.** Never launch a separate browser to drive
Copilot Studio.

## The four gates, in order

### 1. Auth mode must be Maker, not User

This is the one that costs hours. Open the agent → **Tools** → click the MCP
server chip → **Edit MCP server** → **Authentication mode**.

It defaults to **User**. Under User auth the tools are attached, they appear in
the maker panel, the solution is published — and they **never reach the agent
runtime**. The agent truthfully reports it has no tools. Switch to **Maker**,
Confirm, publish.

Symptom you will see first: the agent says *"no MCP tools are connected to this
session"*, or it reaches for an unrelated tool (`list_bash`) because it is
pattern-matching your words against a toolset that does not contain what you
asked for.

### 2. Attach the MCP server to EVERY agent, parent and child

The Factory's manual steps say "once per agent" and mean it. A parent that
delegates to a connected child needs it on both — the 404 will surface as the
parent reporting failure when it is actually the child that cannot see the data.

### 3. The attach does not survive a failed publish

If a publish fails ("We couldn't publish your agent"), **go back and check
Tools** — the attach will be gone. Re-attach, then verify by reopening the panel
before publishing again. Do not assume it stuck.

Preview tests the **draft**, so you can verify the attach works before you
publish. Do that: attach → Preview → ask a real question → then publish.

### 4. Individual tool toggles are a red herring

Inside **Edit MCP server** each tool has its own switch, and they render greyed
out. They are `checked: true, disabled: true` — "Enable all tools" at the top is
on and forces them. Do not spend time trying to flip them.

## Making it presentable

### The name is capped at 30 characters and truncates SILENTLY

"Budget Estimates Briefing Agent" is 31 characters. It saves as
**"Budget Estimates Briefing Agen"** with no error and no warning. Count first,
or check the saved value after.

Factory-generated names are also embarrassing on camera —
`Estimatesbriefbuilder Generate Estimates Brief Agent Agent`, with the doubled
suffix. Rename before filming.

### End user preview hides the build machinery

The toggle sits top-right of the Preview pane and defaults **off**. On, it hides
the chain-of-thought rows and the raw tool identifiers
(`get_estimatesbriefbuildergeneratealternativebriefformatsagent`). Off, those
are on screen for the whole take and are instantly disqualifying for anything
customer-facing.

Verify per-response, not once — behaviour can differ between answers.

### Return does not submit

The chat box ignores Return. Click the send arrow at the input's right edge.
A whole take can be lost to this: the text sits in the box looking submitted.

## Verify before you believe it

Ask a question whose answer can only come from the data server, and read the
response for a real record id. "It replied" is not evidence — the agent will
happily explain that it cannot find anything, which is correct behaviour and
looks like success if you only glance.

Good probe: *"List the briefing records you can see for <topic>."*

## Related

`/tab-film` for capturing the result. `/mcs-deploy` for the deploy itself.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `cs_agent_live_agent.py` and embedded as the fenced Python below (sha256 2a31cb0d9d8f3c2d…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `cs_agent_live_agent.py` first:

```bash
python3 cs_agent_live_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 cs_agent_live_agent.py   # or on stdin
python3 cs_agent_live_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""CsAgentLive -- Take a Copilot Studio agent that was generated and deployed by the RAPP Factory and make it actually answer from its data — then make it presentable enough to film. Covers the MCP attach, the auth mode that everyone gets wrong, the silent name truncation, and the toggle that hides the build machinery. Trigger when a deployed agent "has no data", reports 404 from its data server, or looks machine-generated on screen.

Generated by the rapp skill from cs-agent-live. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Making a deployed Copilot Studio agent live\n\nA Factory deploy lands two solutions and publishes them, and the agent still\nanswers "I don\'t have access to that data". Nothing is broken. Four things are\nmissing, and only one of them is in the Factory\'s own manual steps.\n\n**claude-in-chrome is the law here.** Never launch a separate browser to drive\nCopilot Studio.\n\n## The four gates, in order\n\n### 1. Auth mode must be Maker, not User\n\nThis is the one that costs hours. Open the agent → **Tools** → click the MCP\nserver chip → **Edit MCP server** → **Authentication mode**.\n\nIt defaults to **User**. Under User auth the tools are attached, they appear in\nthe maker panel, the solution is published — and they **never reach the agent\nruntime**. The agent truthfully reports it has no tools. Switch to **Maker**,\nConfirm, publish.\n\nSymptom you will see first: the agent says *"no MCP tools are connected to this\nsession"*, or it reaches for an unrelated tool (`list_bash`) because it is\npattern-matching your words against a toolset that does not contain what you\nasked for.\n\n### 2. Attach the MCP server to EVERY agent, parent and child\n\nThe Factory\'s manual steps say "once per agent" and mean it. A parent that\ndelegates to a connected child needs it on both — the 404 will surface as the\nparent reporting failure when it is actually the child that cannot see the data.\n\n### 3. The attach does not survive a failed publish\n\nIf a publish fails ("We couldn\'t publish your agent"), **go back and check\nTools** — the attach will be gone. Re-attach, then verify by reopening the panel\nbefore publishing again. Do not assume it stuck.\n\nPreview tests the **draft**, so you can verify the attach works before you\npublish. Do that: attach → Preview → ask a real question → then publish.\n\n### 4. Individual tool toggles are a red herring\n\nInside **Edit MCP server** each tool has its own switch, and they render greyed\nout. They are `checked: true, disabled: true` — "Enable all tools" at the top is\non and forces them. Do not spend time trying to flip them.\n\n## Making it presentable\n\n### The name is capped at 30 characters and truncates SILENTLY\n\n"Budget Estimates Briefing Agent" is 31 characters. It saves as\n**"Budget Estimates Briefing Agen"** with no error and no warning. Count first,\nor check the saved value after.\n\nFactory-generated names are also embarrassing on camera —\n`Estimatesbriefbuilder Generate Estimates Brief Agent Agent`, with the doubled\nsuffix. Rename before filming.\n\n### End user preview hides the build machinery\n\nThe toggle sits top-right of the Preview pane and defaults **off**. On, it hides\nthe chain-of-thought rows and the raw tool identifiers\n(`get_estimatesbriefbuildergeneratealternativebriefformatsagent`). Off, those\nare on screen for the whole take and are instantly disqualifying for anything\ncustomer-facing.\n\nVerify per-response, not once — behaviour can differ between answers.\n\n### Return does not submit\n\nThe chat box ignores Return. Click the send arrow at the input\'s right edge.\nA whole take can be lost to this: the text sits in the box looking submitted.\n\n## Verify before you believe it\n\nAsk a question whose answer can only come from the data server, and read the\nresponse for a real record id. "It replied" is not evidence — the agent will\nhappily explain that it cannot find anything, which is correct behaviour and\nlooks like success if you only glance.\n\nGood probe: *"List the briefing records you can see for <topic>."*\n\n## Related\n\n`/tab-film` for capturing the result. `/mcs-deploy` for the deploy itself.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class CsAgentLiveAgent(BasicAgent):
    def __init__(self):
        self.name = 'CsAgentLive'
        self.metadata = {
          "name": "CsAgentLive",
          "description": "Take a Copilot Studio agent that was generated and deployed by the RAPP Factory and make it actually answer from its data \u2014 then make it presentable enough to film. Covers the MCP attach, the auth mode that everyone gets wrong, the silent name truncation, and the toggle that hides the build machinery. Trigger when a deployed agent \"has no data\", reports 404 from its data server, or looks machine-generated on screen.",
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
    #     echo '{"arg": "value"}' | python3 cs_agent_live_agent.py
    #     python3 cs_agent_live_agent.py '{"arg": "value"}'
    #     python3 cs_agent_live_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(CsAgentLiveAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(CsAgentLiveAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
