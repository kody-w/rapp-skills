---
name: "style-analyzer"
description: "Analyze the user's communication style across their Teams chats and emails to build a reusable mimicry profile \u2014 greetings, tone, length, punctuation, sign-offs, common phrases, and quirks. Use this skill when the user asks to capture or analyze their writing style, or before configuring an assistant (e.g. an OOO auto-responder) that should write in their voice."
---

# Style Analyzer

Analyze the user's communication patterns across Teams and Outlook and build a
style profile that other skills or automations (e.g. an out-of-office
auto-responder) can use to write in the user's voice. Save the profile to memory
so it's available across sessions.

> **Tool names.** This skill refers to Microsoft 365 tools as `m365_*` and to
> memory as remember/recall tools. If your host exposes these under different
> names, map them to the equivalent capability.

## Data collection

### 1. Gather sent emails (20–30 samples)

- List the last ~30 emails in the **Sent** folder.
- For emails with real body content (not just meeting accepts/declines), fetch
  the full text body.

### 2. Gather Teams chat messages

- List recent chats (~50).
- For each relevant chat (prioritize active 1:1 and group chats), fetch the last
  ~30 messages.
- Filter to messages **from the current user** (match the `from` field to the
  user's display name).

### 3. Sample diversity

Aim for:

- 10+ sent emails with body content
- 50+ Teams messages across **20–25 different chats**
- A mix of 1:1, group, and meeting chats
- Both internal and external conversations where available

## Analysis framework

Analyze the collected messages across these dimensions:

- **A. Greetings** — how they address people (first name, "Hi [Name]", "Hey",
  formal titles); patterns by relationship type (internal vs external).
- **B. Tone & formality** — professional/casual/mixed; direct vs hedging; warmth
  indicators.
- **C. Message length** — average sentence count; frequency of one-word replies;
  when they write longer messages.
- **D. Punctuation & grammar** — consistency; common typos (e.g. lowercase "i");
  emoji usage (none / occasional / frequent).
- **E. Sign-offs** — email signature style; Teams message endings; closing
  phrases ("Thanks", "Regards", etc.).
- **F. Common phrases** — frequently used expressions for agreement ("sounds
  good", "makes sense"), requests ("can you", "would you mind"), availability,
  and FYI/context-setting.
- **G. Technical communication** — how they explain technical concepts; level of
  detail; hedging vs confidence.
- **H. Action patterns** — how they delegate, loop others in, and schedule
  meetings.

## Output

### 1. Display a summary

Present findings as a formatted table:

```markdown
## Communication Style Profile for [Name]

| Dimension | Pattern |
|-----------|---------|
| Greetings | ... |
| Tone | ... |
| Length | ... |
| Emojis | ... |
| Sign-offs | ... |
| Technical | ... |

### Common phrases
- "..."
- "..."

### Quirks & notes
- ...
```

### 2. Save to memory

Store the style guide in memory. Use two entries to stay within any per-fact
length limits:

- **Entry 1** — greetings, tone, brevity, punctuation, emojis.
- **Entry 2** — common phrases, delegation style, technical communication,
  quirks.

Tag both as a preference so they persist and can be recalled later.

### 3. Confirm storage

Tell the user:

- The style profile has been saved to memory.
- It can be recalled with a query like "writing style".
- It's available to other assistants and automations that write in their voice.

## Usage notes

- Re-run periodically (e.g. quarterly) to keep the profile current.
- Pairs well with an OOO / auto-responder skill that should mimic the user's
  voice.

## Privacy

All analysis happens inside the user's own agent environment against their own
Microsoft 365 data. No communication content is sent to any third party. The
saved profile describes *how* the user writes, not *what* they wrote — do not
store verbatim private message content in the profile.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `style_analyzer_agent.py` and embedded as the fenced Python below (sha256 3cb0e67c9a1ad1bd…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `style_analyzer_agent.py` first:

```bash
python3 style_analyzer_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 style_analyzer_agent.py   # or on stdin
python3 style_analyzer_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""StyleAnalyzer -- Analyze the user's communication style across their Teams chats and emails to build a reusable mimicry profile — greetings, tone, length, punctuation, sign-offs, common phrases, and quirks. Use this skill when the user asks to capture or analyze their writing style, or before configuring an assistant (e.g. an OOO auto-responder) that should write in their voice.

Generated by the rapp skill from style-analyzer. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Style Analyzer\n\nAnalyze the user\'s communication patterns across Teams and Outlook and build a\nstyle profile that other skills or automations (e.g. an out-of-office\nauto-responder) can use to write in the user\'s voice. Save the profile to memory\nso it\'s available across sessions.\n\n> **Tool names.** This skill refers to Microsoft 365 tools as `m365_*` and to\n> memory as remember/recall tools. If your host exposes these under different\n> names, map them to the equivalent capability.\n\n## Data collection\n\n### 1. Gather sent emails (20–30 samples)\n\n- List the last ~30 emails in the **Sent** folder.\n- For emails with real body content (not just meeting accepts/declines), fetch\n  the full text body.\n\n### 2. Gather Teams chat messages\n\n- List recent chats (~50).\n- For each relevant chat (prioritize active 1:1 and group chats), fetch the last\n  ~30 messages.\n- Filter to messages **from the current user** (match the `from` field to the\n  user\'s display name).\n\n### 3. Sample diversity\n\nAim for:\n\n- 10+ sent emails with body content\n- 50+ Teams messages across **20–25 different chats**\n- A mix of 1:1, group, and meeting chats\n- Both internal and external conversations where available\n\n## Analysis framework\n\nAnalyze the collected messages across these dimensions:\n\n- **A. Greetings** — how they address people (first name, "Hi [Name]", "Hey",\n  formal titles); patterns by relationship type (internal vs external).\n- **B. Tone & formality** — professional/casual/mixed; direct vs hedging; warmth\n  indicators.\n- **C. Message length** — average sentence count; frequency of one-word replies;\n  when they write longer messages.\n- **D. Punctuation & grammar** — consistency; common typos (e.g. lowercase "i");\n  emoji usage (none / occasional / frequent).\n- **E. Sign-offs** — email signature style; Teams message endings; closing\n  phrases ("Thanks", "Regards", etc.).\n- **F. Common phrases** — frequently used expressions for agreement ("sounds\n  good", "makes sense"), requests ("can you", "would you mind"), availability,\n  and FYI/context-setting.\n- **G. Technical communication** — how they explain technical concepts; level of\n  detail; hedging vs confidence.\n- **H. Action patterns** — how they delegate, loop others in, and schedule\n  meetings.\n\n## Output\n\n### 1. Display a summary\n\nPresent findings as a formatted table:\n\n```markdown\n## Communication Style Profile for [Name]\n\n| Dimension | Pattern |\n|-----------|---------|\n| Greetings | ... |\n| Tone | ... |\n| Length | ... |\n| Emojis | ... |\n| Sign-offs | ... |\n| Technical | ... |\n\n### Common phrases\n- "..."\n- "..."\n\n### Quirks & notes\n- ...\n```\n\n### 2. Save to memory\n\nStore the style guide in memory. Use two entries to stay within any per-fact\nlength limits:\n\n- **Entry 1** — greetings, tone, brevity, punctuation, emojis.\n- **Entry 2** — common phrases, delegation style, technical communication,\n  quirks.\n\nTag both as a preference so they persist and can be recalled later.\n\n### 3. Confirm storage\n\nTell the user:\n\n- The style profile has been saved to memory.\n- It can be recalled with a query like "writing style".\n- It\'s available to other assistants and automations that write in their voice.\n\n## Usage notes\n\n- Re-run periodically (e.g. quarterly) to keep the profile current.\n- Pairs well with an OOO / auto-responder skill that should mimic the user\'s\n  voice.\n\n## Privacy\n\nAll analysis happens inside the user\'s own agent environment against their own\nMicrosoft 365 data. No communication content is sent to any third party. The\nsaved profile describes *how* the user writes, not *what* they wrote — do not\nstore verbatim private message content in the profile.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class StyleAnalyzerAgent(BasicAgent):
    def __init__(self):
        self.name = 'StyleAnalyzer'
        self.metadata = {
          "name": "StyleAnalyzer",
          "description": "Analyze the user's communication style across their Teams chats and emails to build a reusable mimicry profile \u2014 greetings, tone, length, punctuation, sign-offs, common phrases, and quirks. Use this skill when the user asks to capture or analyze their writing style, or before configuring an assistant (e.g. an OOO auto-responder) that should write in their voice.",
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
    #     echo '{"arg": "value"}' | python3 style_analyzer_agent.py
    #     python3 style_analyzer_agent.py '{"arg": "value"}'
    #     python3 style_analyzer_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(StyleAnalyzerAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(StyleAnalyzerAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
