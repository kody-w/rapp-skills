---
name: "wow"
description: "Generate demo prompts that show off the current product's power \u2014 with a persistent ledger so suggestions never repeat and ambition ratchets up. Use whenever the user asks for \"the coolest prompts\", \"mind-blowing prompts\", \"prompts that show off the power\", \"demo prompts\", \"give me 10\", or is prepping a demo/pitch and wants material. Also use when the user reacts with \"those are not that impressive\" \u2014 that is ledger feedback, not a new request."
---

# Wow: demo-prompt generator with a memory

Kody fires "give me the coolest, most mind-blowing prompts" 20+ times a month, mostly in brainstem/RAPP repos, and the #1 failure mode is recycled or vague suggestions ("those are not that impressive"). This skill fixes that with a ledger and a concreteness bar.

## The ledger: `~/.claude/wow-ledger.md`

One table, append-only. Columns: `date | project | prompt (one line) | status`.
Status values: `suggested`, `used`, `landed` (Kody said it worked/demo went well), `flopped` (Kody said not impressive / it failed live).

- **Read it FIRST, every invocation.** If it doesn't exist, create it with the header row.
- **Never suggest anything semantically close to a prior entry for the same project.** Different wording ≠ new idea.
- If the user's message is a dissatisfaction reaction ("not that impressive", "more impressive than that"), mark the most recent `suggested` batch for this project as `flopped` before generating — flopped entries define the floor the new batch must clear.
- After presenting, append the new batch as `suggested`.

## Generating the batch

1. **Ground in the actual product.** Read enough of the current repo (README, agents/ directory, recent commits) to know what it can really do TODAY. Every prompt must exercise a real, currently-working capability — a demo prompt that errors in front of an audience is worse than a boring one (this has happened; see "you broke it in front of an exec").
2. **Concrete beats cosmic.** "Autonomously evolve this product for 24 hours" is a category Kody already uses. The bar for a wow prompt:
   - Runnable verbatim — a specific instruction, not a theme.
   - Visible payoff in under ~3 minutes — something appears on screen (a page, an agent responding, a live URL, a twin answering).
   - A "wait, it can do THAT?" mechanic — crosses a boundary the audience assumes is hard: touches their real data, produces a working artifact not a description, chains two systems (brainstem→Copilot Studio, transcript→deployed agent, vault→twin), or closes a loop live (build → ship → open the live URL).
3. **Escalate.** Order the 10 from "safe opener" to "closer". The last 2 should be the risky spectacular ones, flagged as such.
4. **Audience knob.** If context says exec/customer/VC, bias toward business-outcome framing (agent solves a named pain in their world); if peer/technical, bias toward architectural flex (P2P twin sync, self-modifying agents, RAR install-on-demand).

## Output format

Numbered 1–10. Each entry: the prompt itself in a code block (copy-paste ready), then ONE sentence on what the audience sees happen. No preamble essays. End with a one-line note of which 2 are the high-risk closers.

## Parameters

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "default": "$(basename $PWD)",
      "description": "Ledger scope key. Collisions are checked within this project only."
    },
    "count": {
      "type": "integer",
      "default": 10,
      "description": "Prompts to deliver. Deliver fewer rather than padding below the bar."
    },
    "audience": {
      "type": "string",
      "default": "peer",
      "enum": [
        "exec",
        "customer",
        "vc",
        "peer",
        "technical"
      ],
      "description": "exec/customer/vc bias to business-outcome framing; peer/technical to architectural flex."
    },
    "ledger": {
      "type": "string",
      "default": "~/.claude/wow-ledger.md",
      "description": "Append-only table: date | project | prompt | status."
    },
    "mark_flopped": {
      "type": "boolean",
      "default": false,
      "description": "True when the invocation is a dissatisfaction reaction; demotes the prior suggested batch to flopped BEFORE generating so it sets the floor."
    }
  },
  "required": []
}
```

## Commands

Run in this order. Steps 1 and 5 are mandatory; skipping either is what makes the
skill non-deterministic.

```bash
# 1. read the ledger first (create with the header row if absent)
test -f "$LEDGER" || printf '| date | project | prompt | status |\n|---|---|---|---|\n' > "$LEDGER"
grep -ci "$PROJECT" "$LEDGER"          # 0 => fresh axis, no collision risk

# 2. if mark_flopped, demote the prior suggested batch for this project
#    sed -i '' "s/| $PROJECT | \(.*\) | suggested |/| $PROJECT | \1 | flopped |/" "$LEDGER"

# 3. ground in the product: read README + recent commits, and probe that each
#    capability a prompt names actually answers TODAY (a prompt that errors live
#    is worse than a boring one)

# 4. generate, ordered safe opener -> risky closer

# 5. append the delivered batch as `suggested`
#    cat >> "$LEDGER" <<'ROWS'
#    | YYYY-MM-DD | <project> | <one-line prompt> | suggested |
#    ROWS
```

## Output contract

`count` numbered entries. Each: the prompt in a fenced code block, copy-paste
runnable verbatim, then exactly ONE sentence on what the audience sees. No
preamble. Final line names which 2 are the high-risk closers.

## Don'ts

- Don't re-serve a flopped idea with new adjectives.
- Don't suggest prompts requiring services that can fail live (fresh auth flows, rate-limited APIs) without flagging the risk.
- Don't pad — if only 7 clear the bar, deliver 7 and say why.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `wow_agent.py` and embedded as the fenced Python below (sha256 c2320de5747b3be0…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `wow_agent.py` first:

```bash
python3 wow_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 wow_agent.py   # or on stdin
python3 wow_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""Wow -- Generate demo prompts that show off the current product's power — with a persistent ledger so suggestions never repeat and ambition ratchets up. Use whenever the user asks for "the coolest prompts", "mind-blowing prompts", "prompts that show off the power", "demo prompts", "give me 10", or is prepping a demo/pitch and wants material. Also use when the user reacts with "those are not that impressive" — that is ledger feedback, not a new request.

Generated by the rapp skill from wow. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Wow: demo-prompt generator with a memory\n\nKody fires "give me the coolest, most mind-blowing prompts" 20+ times a month, mostly in brainstem/RAPP repos, and the #1 failure mode is recycled or vague suggestions ("those are not that impressive"). This skill fixes that with a ledger and a concreteness bar.\n\n## The ledger: `~/.claude/wow-ledger.md`\n\nOne table, append-only. Columns: `date | project | prompt (one line) | status`.\nStatus values: `suggested`, `used`, `landed` (Kody said it worked/demo went well), `flopped` (Kody said not impressive / it failed live).\n\n- **Read it FIRST, every invocation.** If it doesn\'t exist, create it with the header row.\n- **Never suggest anything semantically close to a prior entry for the same project.** Different wording ≠ new idea.\n- If the user\'s message is a dissatisfaction reaction ("not that impressive", "more impressive than that"), mark the most recent `suggested` batch for this project as `flopped` before generating — flopped entries define the floor the new batch must clear.\n- After presenting, append the new batch as `suggested`.\n\n## Generating the batch\n\n1. **Ground in the actual product.** Read enough of the current repo (README, agents/ directory, recent commits) to know what it can really do TODAY. Every prompt must exercise a real, currently-working capability — a demo prompt that errors in front of an audience is worse than a boring one (this has happened; see "you broke it in front of an exec").\n2. **Concrete beats cosmic.** "Autonomously evolve this product for 24 hours" is a category Kody already uses. The bar for a wow prompt:\n   - Runnable verbatim — a specific instruction, not a theme.\n   - Visible payoff in under ~3 minutes — something appears on screen (a page, an agent responding, a live URL, a twin answering).\n   - A "wait, it can do THAT?" mechanic — crosses a boundary the audience assumes is hard: touches their real data, produces a working artifact not a description, chains two systems (brainstem→Copilot Studio, transcript→deployed agent, vault→twin), or closes a loop live (build → ship → open the live URL).\n3. **Escalate.** Order the 10 from "safe opener" to "closer". The last 2 should be the risky spectacular ones, flagged as such.\n4. **Audience knob.** If context says exec/customer/VC, bias toward business-outcome framing (agent solves a named pain in their world); if peer/technical, bias toward architectural flex (P2P twin sync, self-modifying agents, RAR install-on-demand).\n\n## Output format\n\nNumbered 1–10. Each entry: the prompt itself in a code block (copy-paste ready), then ONE sentence on what the audience sees happen. No preamble essays. End with a one-line note of which 2 are the high-risk closers.\n\n## Parameters\n\n```json\n{\n  "type": "object",\n  "properties": {\n    "project": {\n      "type": "string",\n      "default": "$(basename $PWD)",\n      "description": "Ledger scope key. Collisions are checked within this project only."\n    },\n    "count": {\n      "type": "integer",\n      "default": 10,\n      "description": "Prompts to deliver. Deliver fewer rather than padding below the bar."\n    },\n    "audience": {\n      "type": "string",\n      "default": "peer",\n      "enum": [\n        "exec",\n        "customer",\n        "vc",\n        "peer",\n        "technical"\n      ],\n      "description": "exec/customer/vc bias to business-outcome framing; peer/technical to architectural flex."\n    },\n    "ledger": {\n      "type": "string",\n      "default": "~/.claude/wow-ledger.md",\n      "description": "Append-only table: date | project | prompt | status."\n    },\n    "mark_flopped": {\n      "type": "boolean",\n      "default": false,\n      "description": "True when the invocation is a dissatisfaction reaction; demotes the prior suggested batch to flopped BEFORE generating so it sets the floor."\n    }\n  },\n  "required": []\n}\n```\n\n## Commands\n\nRun in this order. Steps 1 and 5 are mandatory; skipping either is what makes the\nskill non-deterministic.\n\n```bash\n# 1. read the ledger first (create with the header row if absent)\ntest -f "$LEDGER" || printf \'| date | project | prompt | status |\\n|---|---|---|---|\\n\' > "$LEDGER"\ngrep -ci "$PROJECT" "$LEDGER"          # 0 => fresh axis, no collision risk\n\n# 2. if mark_flopped, demote the prior suggested batch for this project\n#    sed -i \'\' "s/| $PROJECT | \\(.*\\) | suggested |/| $PROJECT | \\1 | flopped |/" "$LEDGER"\n\n# 3. ground in the product: read README + recent commits, and probe that each\n#    capability a prompt names actually answers TODAY (a prompt that errors live\n#    is worse than a boring one)\n\n# 4. generate, ordered safe opener -> risky closer\n\n# 5. append the delivered batch as `suggested`\n#    cat >> "$LEDGER" <<\'ROWS\'\n#    | YYYY-MM-DD | <project> | <one-line prompt> | suggested |\n#    ROWS\n```\n\n## Output contract\n\n`count` numbered entries. Each: the prompt in a fenced code block, copy-paste\nrunnable verbatim, then exactly ONE sentence on what the audience sees. No\npreamble. Final line names which 2 are the high-risk closers.\n\n## Don\'ts\n\n- Don\'t re-serve a flopped idea with new adjectives.\n- Don\'t suggest prompts requiring services that can fail live (fresh auth flows, rate-limited APIs) without flagging the risk.\n- Don\'t pad — if only 7 clear the bar, deliver 7 and say why.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class WowAgent(BasicAgent):
    def __init__(self):
        self.name = 'Wow'
        self.metadata = {
          "name": "Wow",
          "description": "Generate demo prompts that show off the current product's power \u2014 with a persistent ledger so suggestions never repeat and ambition ratchets up. Use whenever the user asks for \"the coolest prompts\", \"mind-blowing prompts\", \"prompts that show off the power\", \"demo prompts\", \"give me 10\", or is prepping a demo/pitch and wants material. Also use when the user reacts with \"those are not that impressive\" \u2014 that is ledger feedback, not a new request.",
          "parameters": {
            "type": "object",
            "properties": {
              "project": {
                "type": "string",
                "default": "$(basename $PWD)",
                "description": "Ledger scope key. Collisions are checked within this project only."
              },
              "count": {
                "type": "integer",
                "default": 10,
                "description": "Prompts to deliver. Deliver fewer rather than padding below the bar."
              },
              "audience": {
                "type": "string",
                "default": "peer",
                "enum": [
                  "exec",
                  "customer",
                  "vc",
                  "peer",
                  "technical"
                ],
                "description": "exec/customer/vc bias to business-outcome framing; peer/technical to architectural flex."
              },
              "ledger": {
                "type": "string",
                "default": "~/.claude/wow-ledger.md",
                "description": "Append-only table: date | project | prompt | status."
              },
              "mark_flopped": {
                "type": "boolean",
                "default": False,
                "description": "True when the invocation is a dissatisfaction reaction; demotes the prior suggested batch to flopped BEFORE generating so it sets the floor."
              }
            },
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
    #     echo '{"arg": "value"}' | python3 wow_agent.py
    #     python3 wow_agent.py '{"arg": "value"}'
    #     python3 wow_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(WowAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(WowAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
