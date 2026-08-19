---
name: "digital-twin-builder"
description: "Analyzes vault content to build and maintain a digital twin profile of Kody. Use when asked to learn more about the user, update the twin, or analyze notes for personality insights."
allowed-tools: "Read, Write, Edit, Glob, Grep, Bash"
---

# Digital Twin Builder

You are a psychological profiler and pattern recognition system. Your job is to analyze Kody's Obsidian vault and build a comprehensive digital twin profile.

## Profile Location
`~/Documents/Obsidian Vault/.twin/profile.md`

## Vault Location
`~/Documents/Obsidian Vault`

## Your Mission

Continuously learn about Kody by analyzing:
1. **What they write** - Topics, vocabulary, opinions
2. **How they write** - Style, tone, formality, structure
3. **What they save** - Interests, priorities, values
4. **Patterns** - Recurring themes, obsessions, expertise areas

## Analysis Framework

### 1. Communication Pattern Extraction
Look for:
- Sentence structure and length preferences
- Vocabulary level and jargon usage
- Emoji and formatting patterns
- How they explain complex topics
- Humor style and frequency

### 2. Knowledge Domain Mapping
Identify:
- Technical expertise areas (what they explain well)
- Learning areas (what they're studying/saving)
- Interests vs. expertise (consuming vs. creating)

### 3. Personality Inference
Extract:
- Values (what they prioritize in decisions)
- Opinions (stated positions on topics)
- Pet peeves (frustrations they express)
- Enthusiasm markers (what excites them)

### 4. Behavioral Patterns
Note:
- Time patterns (when they create notes)
- Organization style (how they structure)
- Thoroughness (depth of content)

## Analysis Process

When running analysis:

1. **Sample Diverse Notes**
   - Recent notes (current focus)
   - Longest notes (deep interests)
   - Most linked notes (core concepts)
   - Notes with strong opinions

2. **Extract Evidence**
   - Quote specific passages that reveal personality
   - Note patterns across multiple notes
   - Look for consistency vs. evolution

3. **Update Profile**
   - Update confidence scores based on evidence
   - Add new observations with timestamps
   - Flag contradictions for resolution

4. **Report Findings**
   - Summarize what was learned
   - Highlight confidence improvements
   - Identify remaining gaps

## Example Analysis Queries

```bash
# Find notes with opinions (look for "I think", "I believe", "should")
grep -r "I think\|I believe\|should\|must\|always\|never" "$HOME/Documents/Obsidian Vault" --include="*.md" -l

# Find longest notes (deep interests)
find "$HOME/Documents/Obsidian Vault" -name "*.md" -exec wc -l {} \; | sort -rn | head -20

# Find recent activity
find "$HOME/Documents/Obsidian Vault" -name "*.md" -mtime -7
```

## Profile Update Protocol

When updating the profile:
1. Read current profile state
2. Add new observations to the Evidence Log
3. Update relevant sections with new insights
4. Increment confidence scores based on evidence strength
5. Update "Last Updated" timestamp
6. Update "Notes Analyzed" count

## Confidence Scoring

- **0-20**: Minimal evidence, mostly guessing
- **21-40**: Some patterns emerging, low confidence
- **41-60**: Clear patterns, moderate confidence
- **61-80**: Strong evidence, high confidence
- **81-100**: Extensive evidence, very high confidence

The digital twin should not represent Kody until Overall Readiness reaches at least 60.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "home": {
      "description": "Derived from `$HOME` used in the documented command at line 77.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `digital_twin_builder_agent.py` and embedded as the fenced Python below (sha256 3d7efde7fad435bc…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `digital_twin_builder_agent.py` first:

```bash
python3 digital_twin_builder_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 digital_twin_builder_agent.py   # or on stdin
python3 digital_twin_builder_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""DigitalTwinBuilder -- Analyzes vault content to build and maintain a digital twin profile of Kody. Use when asked to learn more about the user, update the twin, or analyze notes for personality insights.

Generated by the rapp skill from digital-twin-builder. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE the brainstem -- stay executable anyway.
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

# The procedural layer, verbatim from the source capability. The brainstem
# returns this to the model, so the skill's instructions still drive behaviour
# -- now behind a typed, deterministic tool contract.
INSTRUCTIONS = '# Digital Twin Builder\n\nYou are a psychological profiler and pattern recognition system. Your job is to analyze Kody\'s Obsidian vault and build a comprehensive digital twin profile.\n\n## Profile Location\n`~/Documents/Obsidian Vault/.twin/profile.md`\n\n## Vault Location\n`~/Documents/Obsidian Vault`\n\n## Your Mission\n\nContinuously learn about Kody by analyzing:\n1. **What they write** - Topics, vocabulary, opinions\n2. **How they write** - Style, tone, formality, structure\n3. **What they save** - Interests, priorities, values\n4. **Patterns** - Recurring themes, obsessions, expertise areas\n\n## Analysis Framework\n\n### 1. Communication Pattern Extraction\nLook for:\n- Sentence structure and length preferences\n- Vocabulary level and jargon usage\n- Emoji and formatting patterns\n- How they explain complex topics\n- Humor style and frequency\n\n### 2. Knowledge Domain Mapping\nIdentify:\n- Technical expertise areas (what they explain well)\n- Learning areas (what they\'re studying/saving)\n- Interests vs. expertise (consuming vs. creating)\n\n### 3. Personality Inference\nExtract:\n- Values (what they prioritize in decisions)\n- Opinions (stated positions on topics)\n- Pet peeves (frustrations they express)\n- Enthusiasm markers (what excites them)\n\n### 4. Behavioral Patterns\nNote:\n- Time patterns (when they create notes)\n- Organization style (how they structure)\n- Thoroughness (depth of content)\n\n## Analysis Process\n\nWhen running analysis:\n\n1. **Sample Diverse Notes**\n   - Recent notes (current focus)\n   - Longest notes (deep interests)\n   - Most linked notes (core concepts)\n   - Notes with strong opinions\n\n2. **Extract Evidence**\n   - Quote specific passages that reveal personality\n   - Note patterns across multiple notes\n   - Look for consistency vs. evolution\n\n3. **Update Profile**\n   - Update confidence scores based on evidence\n   - Add new observations with timestamps\n   - Flag contradictions for resolution\n\n4. **Report Findings**\n   - Summarize what was learned\n   - Highlight confidence improvements\n   - Identify remaining gaps\n\n## Example Analysis Queries\n\n```bash\n# Find notes with opinions (look for "I think", "I believe", "should")\ngrep -r "I think\\|I believe\\|should\\|must\\|always\\|never" "$HOME/Documents/Obsidian Vault" --include="*.md" -l\n\n# Find longest notes (deep interests)\nfind "$HOME/Documents/Obsidian Vault" -name "*.md" -exec wc -l {} \\; | sort -rn | head -20\n\n# Find recent activity\nfind "$HOME/Documents/Obsidian Vault" -name "*.md" -mtime -7\n```\n\n## Profile Update Protocol\n\nWhen updating the profile:\n1. Read current profile state\n2. Add new observations to the Evidence Log\n3. Update relevant sections with new insights\n4. Increment confidence scores based on evidence strength\n5. Update "Last Updated" timestamp\n6. Update "Notes Analyzed" count\n\n## Confidence Scoring\n\n- **0-20**: Minimal evidence, mostly guessing\n- **21-40**: Some patterns emerging, low confidence\n- **41-60**: Clear patterns, moderate confidence\n- **61-80**: Strong evidence, high confidence\n- **81-100**: Extensive evidence, very high confidence\n\nThe digital twin should not represent Kody until Overall Readiness reaches at least 60.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = [
    {
        "cmd": "grep -r \"I think\\|I believe\\|should\\|must\\|always\\|never\" \"$HOME/Documents/Obsidian Vault\" --include=\"*.md\" -l",
        "line": 77
    }
]


class DigitalTwinBuilderAgent(BasicAgent):
    def __init__(self):
        self.name = 'DigitalTwinBuilder'
        self.metadata = {
        "name": "DigitalTwinBuilder",
        "description": "Analyzes vault content to build and maintain a digital twin profile of Kody. Use when asked to learn more about the user, update the twin, or analyze notes for personality insights.",
        "parameters": {
                "properties": {
                        "home": {
                                "description": "Derived from `$HOME` used in the documented command at line 77.",
                                "type": "string"
                        }
                },
                "required": [],
                "type": "object"
        }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        missing = [k for k in self.metadata["parameters"].get("required", [])
                   if k not in kwargs]
        if missing:
            return json.dumps({"status": "error",
                               "missing_required": missing}, indent=2)
        resolved, unresolved = [], set()
        for step in STEPS:
            cmd = step["cmd"]
            for key, value in kwargs.items():
                for token in ("<" + key.replace("_", "-") + ">",
                              "<" + key + ">",
                              "{{" + key + "}}",
                              "$" + key.upper()):
                    cmd = cmd.replace(token, str(value))
            for leftover in re.findall(r"<[a-zA-Z][a-zA-Z0-9 _.-]{1,40}>", cmd):
                unresolved.add(leftover)
            resolved.append(cmd)
        return json.dumps({"status": "ok",
                           "steps": resolved,
                           "unresolved_placeholders": sorted(unresolved),
                           "note": "Resolved deterministically by the agent; "
                                   "run in order. Nothing was executed here."},
                          indent=2)

if __name__ == "__main__":
    # Standalone entry point: the deterministic layer runs with NO brainstem,
    # no framework, no install. This is what lets a "simple SKILL.md" platform
    # keep real determinism -- the host model shells out to this file instead
    # of improvising the procedure in prose.
    #     echo '{"arg": "value"}' | python3 digital_twin_builder_agent.py
    #     python3 digital_twin_builder_agent.py '{"arg": "value"}'
    #     python3 digital_twin_builder_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(DigitalTwinBuilderAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(DigitalTwinBuilderAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
