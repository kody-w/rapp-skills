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

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
grep -r "I think\|I believe\|should\|must\|always\|never" "$HOME/Documents/Obsidian Vault" --include="*.md" -l
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
