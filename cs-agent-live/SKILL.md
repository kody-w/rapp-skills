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

"Regional Revenue Briefing Agent" is 31 characters. It saves as
**"Regional Revenue Briefing Agen"** with no error and no warning. Count first,
or check the saved value after.

Factory-generated names are also embarrassing on camera —
`Revenuebriefbuilder Generate Revenue Brief Agent Agent`, with the doubled
suffix. Rename before filming.

### End user preview hides the build machinery

The toggle sits top-right of the Preview pane and defaults **off**. On, it hides
the chain-of-thought rows and the raw tool identifiers
(`get_revenuebriefbuildergeneratealternativebriefformatsagent`). Off, those
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

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `cs_agent_live_agent.py` and embedded as the fenced Python below (sha256 5a5286fa31623faf…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `cs_agent_live_agent.py` first:

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
INSTRUCTIONS = '# Making a deployed Copilot Studio agent live\n\nA Factory deploy lands two solutions and publishes them, and the agent still\nanswers "I don\'t have access to that data". Nothing is broken. Four things are\nmissing, and only one of them is in the Factory\'s own manual steps.\n\n**claude-in-chrome is the law here.** Never launch a separate browser to drive\nCopilot Studio.\n\n## The four gates, in order\n\n### 1. Auth mode must be Maker, not User\n\nThis is the one that costs hours. Open the agent → **Tools** → click the MCP\nserver chip → **Edit MCP server** → **Authentication mode**.\n\nIt defaults to **User**. Under User auth the tools are attached, they appear in\nthe maker panel, the solution is published — and they **never reach the agent\nruntime**. The agent truthfully reports it has no tools. Switch to **Maker**,\nConfirm, publish.\n\nSymptom you will see first: the agent says *"no MCP tools are connected to this\nsession"*, or it reaches for an unrelated tool (`list_bash`) because it is\npattern-matching your words against a toolset that does not contain what you\nasked for.\n\n### 2. Attach the MCP server to EVERY agent, parent and child\n\nThe Factory\'s manual steps say "once per agent" and mean it. A parent that\ndelegates to a connected child needs it on both — the 404 will surface as the\nparent reporting failure when it is actually the child that cannot see the data.\n\n### 3. The attach does not survive a failed publish\n\nIf a publish fails ("We couldn\'t publish your agent"), **go back and check\nTools** — the attach will be gone. Re-attach, then verify by reopening the panel\nbefore publishing again. Do not assume it stuck.\n\nPreview tests the **draft**, so you can verify the attach works before you\npublish. Do that: attach → Preview → ask a real question → then publish.\n\n### 4. Individual tool toggles are a red herring\n\nInside **Edit MCP server** each tool has its own switch, and they render greyed\nout. They are `checked: true, disabled: true` — "Enable all tools" at the top is\non and forces them. Do not spend time trying to flip them.\n\n## Making it presentable\n\n### The name is capped at 30 characters and truncates SILENTLY\n\n"Regional Revenue Briefing Agent" is 31 characters. It saves as\n**"Regional Revenue Briefing Agen"** with no error and no warning. Count first,\nor check the saved value after.\n\nFactory-generated names are also embarrassing on camera —\n`Revenuebriefbuilder Generate Revenue Brief Agent Agent`, with the doubled\nsuffix. Rename before filming.\n\n### End user preview hides the build machinery\n\nThe toggle sits top-right of the Preview pane and defaults **off**. On, it hides\nthe chain-of-thought rows and the raw tool identifiers\n(`get_revenuebriefbuildergeneratealternativebriefformatsagent`). Off, those\nare on screen for the whole take and are instantly disqualifying for anything\ncustomer-facing.\n\nVerify per-response, not once — behaviour can differ between answers.\n\n### Return does not submit\n\nThe chat box ignores Return. Click the send arrow at the input\'s right edge.\nA whole take can be lost to this: the text sits in the box looking submitted.\n\n## Verify before you believe it\n\nAsk a question whose answer can only come from the data server, and read the\nresponse for a real record id. "It replied" is not evidence — the agent will\nhappily explain that it cannot find anything, which is correct behaviour and\nlooks like success if you only glance.\n\nGood probe: *"List the briefing records you can see for <topic>."*\n\n## Related\n\n`/tab-film` for capturing the result. `/mcs-deploy` for the deploy itself.'

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
