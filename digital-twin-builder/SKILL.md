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

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `digital_twin_builder_agent.py` and embedded as the fenced Python below (sha256 9a29f9a19ef106b0…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `digital_twin_builder_agent.py` first:

```bash
python3 digital_twin_builder_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 digital_twin_builder_agent.py   # or on stdin
python3 digital_twin_builder_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""DigitalTwinBuilder -- Analyzes vault content to build and maintain a digital twin profile of Kody. Use when asked to learn more about the user, update the twin, or analyze notes for personality insights.

Generated by agentshim from digital-twin-builder. The RCI capsule at the bottom of this file carries the full original; `agentshim.py convert` restores it byte-exact."""

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

# rci-capsule:v1:H4sIAAAAAAAC/8V66Y7bWJbmqwhRDXR20jZFUlzkQQ0gkRT3RZSohe3CJPd9EVeRWTnPPpcMhe3K7sIU5s8YcISke+5Zv7Mx9Pub3bVRWb99Lbos+/Tm+XXc221cFm9f//P3tzQuvLevb37R93b99uktiwv/7StJfnqr7NrOwVFU5j44aMvUB1fe/o3XFPbtj7/NnBq3jqt3Vm+7ws7GyW9Wvd1l7coti9Yv2lVbrpwuzryVXXir3I6LFvxf2SsvDuPWzlbtAN5WdRnEmb8qg5VUeuOXldn4qyHyAWGT+t7MJPPtuljlZe2vbKfsAOPIX3WNX39adZVnt/7ywczt06qsgbRFm1VRtkClAHxS+XVTgk/jdlzFRROHUdt8AXb5TzuvMr8B3gA2zcZWduh/eCsGZ29ff3/L7CIERlYjcGUBbjWtXzWLA9189l9Y+9Xqc7369iYAReIi/fbt78LK8bPY733wuonKLvPAi7xrWvDLzgZ7bMCLApzX397AxcWxMFO6XQ4c18Ca08RebBery+xQQPL5c1y4Wef5f/329uuX3Js/yn4K2R9/+wMoXDRt3blzUIB+b39ZMS9Hn2dH7+dQAHnFt+Jedit79uaqakY3KrMyjF1A94pFvQSsstvWB36vfbcMi3jmumpGYHz+ZQUY1KukdFZxMwfow+NzAP+9WX3X/h0OM7MXDgA08qr2QXSbuPf/WyB8mRX8y19W+gsXcukuiP1W/Pa//6mH4C8zC/iDRe799uKynP5rPD6uLLYpcdMsF74VNEBzXHRl12TjC4rvKJytXTnjy/q4CL9+K5Avq19/vUb2gtFxNdRx6//66+rz6lxWsdt8WvVAFafL7HoEWK3iYo7VtwKdr/Hl8Odbp3bM/E/AxQX4CZCcLxj+tHqPc1f73wrsHyU2dv9+VQA5WPtNC2RWdVwClrE/y7ezzgcSN/M1/T3EzXLB8N2uroEZM6N8pi2dxl/cAF77T5BEbQxyEwDHbl6+WhK/ASA4gHrhD2Wdvh/8ZQUcQZd53hXxu+tXL1kr9tnWtvseDbks09ks4Dhgqz9XDdf/YdyCnMwvwjYCNvgBsAecNzPx5bsbAUHvZwtpYtchkNQ1IIlnIjYvk3g5WVzXtrNxL1gvXL57HFiXzbVphmfmP4HD52gtJB2oO0AlEId3TrX/6IAa44ehIHRSUQ6Z74X+iinnMrdS7AqENvxWCB4wKg7GxcCz70bFkmd/cubql+F7/D40Gfws+4/5ljwjblb8z6T/Xs+u6rwRHMIg7ODXcuF74Fd98+UnUb+Astx0+cxqPnABu/b9zrshAEj6T3VSKF7+/la8QrYYcVnw87PGH+gC+Q/09nw3XiCz6KK9EL76pWlBnQZFpWyWStKsQKDevbwQ6n4LqjSIJCANalAna/ud7MMpwKJ3SrZoo66J7SYHLaVOgcYvZfynG88Ff0bvd6MAzPd+BJxT1sDv+vfYq6A3vAclzv3vmJg5gcazyFz882oi77bUoV3E0zua3wHxS/QBoO+YXUjPoOeWXRgVQOnVL55fAQCD/vbqi//x5+QBpQ7Aesmp6yy/7or3iL8Ivs4nS2U5Lf0K1HXQOEBIZytA8n4rVqv3BJ677nvb+2VO5vltAMrdbMBCIpdFCKDxQeP5oHPFH3j5IFJKQAEay9x9P5jNvReo7wJTvtMt0ldDDIwD5gPOPxW0V0l7IWfF9rE3Y+m7rscOXF41FUBLELsgAM2ctHPwQCRrgIO5G/1A408SfwTLdusS+DcHtTuevbLo+t3Q98oyKw08OBeW8T0f+jLr2ldpX2qn+T5CvPrNdw1fH4P7wbvuq2b2QrNy7AY4BmDAfxn1urDzgLv8Yamadf+C7+KdFmAM4D+vPrQ7ZHa4oKG2vfi9Xy/KAvY/abeUaMOvyrpdHcCoBiDxI9inLgfwn5NuAf8ASsPSm3zvRcCDKSebJ52fTQAjTV32/tL+XnQfJQoIn2vXjLvQrj4KPPs+If3A6rEDM6S/HP/222/AFxGgW9R7YWWxuPye99lHIH5MR2+fljcfA9Ly9jUjvQFs/X8bpxaT303J/i95EsxE/4qcArTF1Q8Z/tN3V4MLhK1+/2P17dv/WP191czx/Qw6499XkW97q8/o+idN6veknjtmvyTC/6vofEbh6jO5xO1PM9aPFGhLt8y+F6Jlun5NBB/z2fuQY8yafpSYjxF+qfFL5v+3uQAGxZnPRy0AORouKfiSXvugk9uAXeO7PyXPzOZjZl9yQihAaZ6N/ldyc65MywDxrcC/S/r2JtsguO/vZud8T9BvBfET1XuBey03M51bdkX78h39Q/gJCF/a/Vz7f/11DSL4669fwQxZxPnc7V+6fAIrTNOCITLs5rFqvjCTo8jnzUJ/Kn9uRcDEOgREnwAYh59Mfb+0QT4TyyV6zvrvt2YRYMb/x8L1foNAPlPvYt5r9Q+tIuDb/0JOIZ+R9UIPavhrXP9xBSTa+F/vfSvO0Z+G+vdknfMIxHdu4nPclsEZeDLOVhrgZGfZgqd4aZeg7boRcDsoasA0ECZi/WVZdEAeNN93sxncYMV5LTjzfvNab95ey6sP/NHM2xsA5zIB+cu7ZaEFv/9xf2Xmvdifh7syX/22pNZv84LpzRPNjFnvlWfgEzAi5vMgaC890l+R5KxeO1azPgBtIGRvf4BlbJ4T49r33nfL13npJADcb+AYTHntPJXOyriZDUrR/Aq4ohx873Nbltm8ws1u+bS6zvvApxXrxe2nFZeVDvgJvPlptQfldxG2eLbuZ2m/vzVpnC2Lq0NsAA9+0wi79380TCI3wpKdEy9DE+Hv/Of45DK25eURaWN1s9sZIrWT92tIETancGdYQ4MdJjWKYPoMhYVrOIKTF1wH22yAhMa90sqaGWGYkZ9QX9u0bu6C68GXtSm86F6wHiS+XttccOyMbGMf2EoPNeVi0IzMmGDa1NaP+02BqYzhEoW9ROPjaJjINtyq+3gXobwUPAtPs6v0wT5yK2LV/m6w20IRaukxUQN0NKdIiPaKzhmGeCZPJzdkWZNTnPRoSfzdSMerEHDSiKri+cJAIZpsnuzxULdnT+GkW5iGiH5PTydaJOOWE4ecY/izpevygHlbQqGv9rY66KkYSWyMBTXL7zJtffK4lmeI2CqI9MgFe+Ua5CLndzSkXtaRuhm9nCqf+3LiFD7PKlXBjWeXmOeTpUmtpsJKshfTcBuOBiLmwvZssKwh7iztxOXa9XSS0sygxHS/v59wI7QZ9lnj1zFcK9hWyuWrcd/19eas6xc1nQaLmQT6LqwrJ+R1TGV4imuxbaw227WEc5VJdWqNbTMR56z9hR4ifo250o5DFXit9y2qkzSExPWjmaB0Qx+CJ3lmT6aUAYLdfiAmie0pIissAzlUifA09KvOlYGWDbdtrhcbqisqj7qXlc2ZUJAbPndCpcbKqHshDkMTUcXFOEJGzN/pQ0Xrpyu/v8I9acjSk5Ly9T0KdkITRuWxwMNUtHLLCo/ItYaQDErwDXRXKPZ5TEv5kGs7QeVEtvZbKKpELt+Sti48bAT8UBKVFnanh0jQcWpxoRbyA29dd8/nkZl27MPP5OKhEeFeKDv2GpNCLPhBMJx3z/RurLljFMSG41tV9OTlTIvy23GXxclgT7jLPYWoJPCi9JEdcioGU3uk8hQrzq7kpz131EkqZ6jnhLe+cREH4j4asnc87ZJ9y16QwUOGVjL3vckq6u1Z5HdhfATe+caX5VMaz3TLimexvPE73u3h43G7a3dP/2Fs9seaNe+HMzHyiqEITXmaDpJeWpZ2R629qsadze1spUUH8nELqjuMm/JwIxVU3PUFNGF7sQzomO+3PpVCrBXHk5REaelOQ0Q9YAQvxJSiYE4vd4lopTvvwjLr6Zi11o2IdjvVagKau1/1Qnd91Ra6AirLQEpqdLsLuw2XjEi6iYBLBAxhqUKJxuPBC3UuFiVbjATu1OuCLN6ccn8qGbPk08QRS+1MHKGy5Yy9LJ9i7mE12ZWl6JIDY6qj6mdkX93Tx+kgObq9Y1QBMuhTLNDjjWC8q3KwDvVtdwxK/rg36ececWxcGyt1TYy0UG6CDZwybQkPAcb4617Szqe86gxJVlxTH7I+C0sjPtItqD3mBYJzBN7x1N5/AEy3x3F0RT6wYP72LPWpTaqDcNmtk4KNo+Sh80Yeoqw/mTm/RhUikGj1VMD2keNDb0QjQ2IZiQ/PjUFLpWnpNvPMsogVICZOBahSDwZy3MimyDqjiFi2tUtVgWX0EjbxM4PjxL08Gi76NNbyE+9cLBQrnQ13jZPjzDPi72ltnMzEZFTicsaTuu6RenMzJk/c71M1FMLnZDotnnUsQz1CMpVtibuYDDUVqQVfal0IBxhJ+oQonlU7TYQ3oDd8M52Oa0g4Pre787g7XvgJ2wGcKHJanqQ8vIhwaFSFdTQ3u2PIQFJxx6Vew25ZfMUjajwI8PGckRvyEkhdrNFCJUD8cRfS1AHzb/v7fkCzI9KHfQkVNSdo7VNu9GYLFRS8PeCMpExjxm4HA48damC8OE3Me4j7/Rja9YEKtcZL20ZhrZBPXOdWI1S0O+HNfntqxXF6KJKOJb0TKD01hkhJB9kGWtsURyWsmQW4gNHJVFt+wA14w7tT7VFZ0NeYDAdyKwQ3uR0YG668vsvg8hLIcvtktHHXT1QJj35cQJjDU0M9QpuWWStDv6Wols+1fhg4iOp8DJ6gGHu4EwzA3SXU6LjZMU7HTGkUmcIvQZ5N1IThMXvpqMu+TbFneUViLL10vKuPksoQt0SWHAeWxzsD0jJvTV+mqv6AT128pmIFpn0D4fvURWlYNicETg/YsbNVUcVRxHpc7QCGzleGwVIb6XlzrYotk0NZldO7e5uU5Qln8OOoHuUrVEvmbSPvDLq681B6IhLsIOoQ6xSYS8hlqhj8RIWCD6lIF0EHLB/WmEruR3YaG2k9tc6m27Ie6JFnTkyIzdrViP783Dy9O74W3DXHU1ttd641T6Sjzku37HZPnapWoeE275+34JwgAr2Jd8pYDPv6eYSfyC2wYa7D+kTLk6CFYuOxOwQd1h7UgNClHr77xp46QB6VHxwd97sGAoPB0DLNRGKiDWMbpnsEpNPenRzOiSRIjgFp7EoRR8eWJRE4rPFhIqZ9gg1uxjH7rZcwdzshTKkLLSWU6UjJNuoWFmFoE5iXzU6C2QCsqTKtTXAVC0qobbUY1gW6XuPmURQlXkTTyxE2A54rTtZRKEfVSDCXQaAHx59MltclZhiwEbul/PYuJ/XEwxCEwWYjn0opi7JQv0R1HxGRm+g3tO66RhjsYDjQOn3Ii3h/IGSh24nCbSINa8Ns/Qihaet5lG5JfsyKIICRgYF2Am5jPeJuYf/Qpc+nHo7Pybicd1IubZEbBmUkplyxu/Hg8a16a1wx2pFtvQ3Oh4Tb8vW4Me0rPHR+3169dekeWUrvgKM92IYngtBjOEVK9tHVLPzgzTNGnKUnnQlrZq8WpnLKn7th8HVJJNb3k1D75JjtHlN48516TclFx5d3aHgoaXvZ75PzPT4ka/nsiIxMH62OUrZS9IQPJK6vVcmuE8MgD3K4o6FApDCYgphNCRcZnmwONm1ZLJ1rwfbgxP608fUg19bB+eElGJWYa5QxMCw/8BKCRg+urTjQ9ix//zCtm3wheipHh06lroN/yx+aH2NWVg+nzXaLVbREwbkBHaPn/bHpvBx0QvR5b7XRmAaSJ3x/Utv64ZjPqveymnMLGCDmceYM9OToGc7vrrAXEb1K87mueYheiTLrZF7Ho4/NQ4bF+K7iqXlFDrXDBzeOEERn5xRSgJ6zioecB9mhF7BBHnr6Hozinpzcze7s1pkaTwiY1m60e82pjXQ5kGT0AB0ISzfwjZDJg5GQObQWsP5RTw53QFAotm2xp7cHd5Pe6zMk1aQLPXuE0whH1Kw4kbDuHAuCAyGNJ2SUeWsdHKybl+5O9uv0IeOTnXXTzSNPh4eGWpf22pwZ7QE9h8wKYp6/bYUn5Uep4k0b8UmSMZk08bVb+6k7VZpuKp5/zZ4Y27NcRKVYlHZNrsJ5fyVjx+H7S+HUZ4uQthbVk2a3JUTNzBSRpRJhsgiiDxAu2110RUUpSdzHUGNCV1wyap1uj0ipKHAUJ/TRt7U0ZLbrFq8f+w2tBYx+jPOjcX3khXrCwAAp3xGUjGlFaXv4GkUJpqwvLZ+pDQgn2pcMleKEteGOZ+2MR+olBb2ovIGdA3PvF7S5CLdDOEl+cpz48tneLlrx4KnJQsKU3XgcucXrcuNESD24KEc66ZZsEFZ4enJQWCy+PbTiMS10DWm9wDlKkN8R9cmhub4cikBx9paXhCrtiPYNA5JjNZhsGTol09RLV662kWFyL9yYEbrD4zjqnwX0Uldh60T0RsNP0mlz3SODSCCau4/XMBIeme3knp2b741EHt4kjDkX9gG9Y5vLLSYZ5LoF4OxqxfSuqOYTyPgI15fUHrFhqLHHFa2PZoJ0uRgW23io42Tqp35EkuuGqbwUtprqSqIFZTuaLqpKu4tVZSKaQ3uIpuqYJG7uPXtDgxX1cExvRRuq9fYee+IpktaXa47zLeGsL4dLS06dkxq9iGAytSX9qbMLsomJ1svG9rjxHDJxpeKp8/De6aHGi27pOEq6jF9i68TcC5zETL5ERE/rynZQA4wNLogRt+csNE2Ml+vSP0xUfX5cImFt3qTOPft1ZJA6ctoOfnLqb4EgVnRCrZEpSwLIrK+eV5w9UlBQI6+lxEUyTzk1hwfiDFNh3ycseGpgPC2N1puM+nHOLN91okeDj6gXYVDpy43Yj3m167entRR4W2sLB5V95TmM25WyiSR2cCyyNRmfQaEgMFlCT2uiZuAIaZ+hRjKYgfuTlYPsJ2P7JuKenjIehT+c22i3UzeiPShnnYWQNHbdkF5J0d32Ym/q++3kXU8Yb/bcdN+zqI1bIaLChaFDpexuMSWjMrAnDhhV1bccY70o6QWiT3Is96SgTfpzXEIdkneg2AZMJbXdISiuYITJNCuUx971NBYx0JQsdPWBJilXN25OFSneZ5BtMCJfmcMgkS5KSofgHKCG1SKxee/4wT1eOq4872v17vbd5Dw6XGlOWqw52ilCDsWNywrQrkY2Kdz25Hp76RiimjatHXmERupqMxdctj2rzVod3ts1nbktK+H1oD4xE6Z8/DIhtXV/woqH5UT+XOspWXbiWChM9fTUw8BHSo57mOA86ryxIfjweCCQFl4MFKVATbKHrkS5ddZJDXEZAaZGhOCoOhBvOM7QHuawGyLQtqOJl5Xb0+oOSzqmEqnrfmK0Gxi4a5k689cOaXmezck+gawbXKBefZXGHsdDvqsueGbUJCY19DW9wwF7NVWtUZ+ycructtbk68qx0K94dWWFHm/jDaappIi4cluD0eGg1xdHb9G9dh6x/b3l/PPTcNrMRXY8tGFLG50UA07w7NbE6CW4e6qhpvvzOHZ5f3o85e5sclsY6y/3UoKtdlecJtvp+A1UDkNBTnV31uzbnoGUUVPyjekhNlYx61z38qAOaQHL7c04OVfFCpzLtYEGH8HR4OLcG8uLOIQcfVIKeH8r+tPOzZ4i74VFn8B73E3PmWqdtD7QkK0SedO6PV2p+qYnKuGHbrNHbmCtlrDzyR49ss00LcOCE4gMCGw9hjJvNrX+bNESQY8ml+NmeZfFuxgTDYQ1rXdkqyobJYsnMTqrOubctsHj8gxUF5HISu+e5ySoOne4iLSb+X5zU56CtqMU13NhwTkSNbFx5Mzpkgxghzg+4oLeEsFRRKfH8e6f8JsX9MzD36/3m0rCSVeENby1TC1mWqVryQPdm0qxvUskbib5uj8HVyZJHTIkGVEKAqV8OFJc3yv8IQ15t14/bKbjx8mi99DQ70HwCLbAYA3ADGrRaqtmOSmRiGa1qlxIKcUU3kbNWKocwJAlP5Qxy073NNqqnVnZl9pF67TD7ANSuNJ2SvsdkhPINWQOp87eONPggQ0CpJJaKughDG5K5BLiY29ReO1XbR045HjF714qPEZbme7mSGGX7XbPPWCxk0dWNsxOtXploHcRfOtjx43giexsiH36Jbb2J5By1oPEOpvB1UuBddf8LKdrIt2sE98l2rLdViXpiYl8TctiDV0Eo4quJ2KbnIZzR2ropSLtSfEjYRTihJUyjsYarDjT6YTX6ZqdLtke7yPstiPPxwe6kXbbOgJTjGSCjRcsmmTL9s+6WuPFhT1maNNP2dlMc6RPc1mUJ1Mrbr1jytBTYW3FMoMyu2jryX1a6enBQDfu5ukOKKhO6LX2UPs5tmZ0erTPWdIFRE9nj+6mo2gdXNeuIcH4hIrQ8xplPoyi9vEmmVWA6kXYdBOR3zy2RkJLXLsYtz44R/x+3afryVAD7aySjpJYlrpuY4rAkQO38ayuPTkddtQU4M4+9zvcMuvM40yxd5yzih+T0ZM7UvBlQXRP24cz3Ucfq0sV6/Z2Fw9rc+9PMKf5PtiGhjA9+Y15tMXBgwSabbP+VkAH0hmtG0dy4W739ult/ivL68n36yn75/kp+2fn/dk3DJ8kQZa/5N78LaXIRnECUG5ce70htsHGd1Fni4F8d7YoFmwJnyQ3DqjxLgI+cVHXIwjSd0lks0YxHCGcwENx1PFeD5jLHoguXCD7P99q3/a+Lo+Zv/4ksS3tpv3qvZ6lL0/hm78iq+XrUn9F3j79k2tuWfR+3X79/D/fH1z/DRC6MVAc+bJeLi3fGSjr8ePZf5N14T/xwGz38hWl/7X8rf3Zftxp7fD1La/5L+fvT/0BfyDhj/8Dp+BfTSUnAAA=
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
