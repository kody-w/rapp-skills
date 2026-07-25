---
name: "transcript-miner"
description: "Mine Claude Code session history for usage patterns, mistakes, and automation candidates. Use when Kody says \"audit my sessions\", \"what am I doing wrong in Claude Code\", \"usage audit\", \"mine my transcripts\", \"analyze my Claude Code history\", \"what should be a skill\", or asks how he's using Claude Code across past sessions. Extracts tool stats, error signatures, Read:Edit ratios, my-message categories (corrections/rejections), and permission denials from ~/.claude/projects JSONL — with evidence, never vibes."
---

# transcript-miner

Turns the raw `~/.claude/projects/<project>/<session>.jsonl` archive into a
usage audit. One JSON message per line (type, content blocks, tool_use,
timestamps). Sessions are large — this NEVER reads whole transcripts into
context; it runs a streaming extractor and returns aggregates.

## Run it

```
python3 ~/.claude/skills/transcript-miner/scripts/mine.py --window 40 --json /tmp/audit.json
```

Flags: `--window N` (last N substantial sessions), `--min-bytes N` (size floor,
default 200KB), `--project SUBSTR` (filter to one project), `--json OUT` (full
per-session rows).

## Turn signals into findings

The script gives you the numbers; you write the audit. Rules:
- **Every claim cites a session file + excerpt.** No uncited findings.
- **Rank by frequency × cost**, label single-anecdote vs recurring.
- **Findings schema:** `{finding, evidence, frequency, impact, confidence, fix}`.
- **Fixes are behavioral rules, not principles** — "never `cd`, pass absolute
  paths" not "be tidy". Each recurring failure → one rule / skill / hook.
- Read:Edit ratio: >6 = research-first (good), <2 = edit-first — but bulk
  file-generation sessions (estate sweeps) skew it low legitimately; note that.
- Always include a "could not verify / out of scope" section.

## Output

An evidence-backed report + draft SKILL.md for the top skill candidates + hook
configs for the top automations. See the P2 audit for the reference shape.

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
cd
python3 ~/.claude/skills/transcript-miner/scripts/mine.py --window 40 --json /tmp/audit.json
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
