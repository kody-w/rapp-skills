# CAT Agent Skills as RAPP pairs

This collection assimilates every Agent Skill in
[`microsoft/cat-agent-skills`](https://github.com/microsoft/cat-agent-skills) at commit
[`147c2dd8`](https://github.com/microsoft/cat-agent-skills/commit/147c2dd84444299b6645f57a1251029f6523e171)
into the RAPP linked-pair shape:

```text
<slug>/
├── SKILL.md
└── <slug>_agent.py
```

The original agent-facing bundle (`scripts/`, `references/`, and `assets/`) is
preserved. The authored skill is synthesized into a RAPP launchpad agent, then
that agent is projected back into the final capsule-bearing `SKILL.md`. The
result works as an Agent Skill and restores the adjacent agent byte-identical.

## Inventory

| Item | Count |
|---|---:|
| Verified Agent Skill pairs | 76 |
| Unpacked source skills | 73 |
| Legacy zip skills assimilated | 3 |
| Skills with explicit typed parameters | 0 |
| Prose-only / untyped launchpads | 76 |
| Launchpads returning preserved instructions | 76 |
| Non-skill submissions recorded but excluded | 5 |

See [`catalog.json`](catalog.json) for every source path, source hash, final
hash, tool name, parameter count, supporting file, and exclusion.

## Use either surface

Install/read the skill:

```text
cat-agent-skills/<slug>/SKILL.md
```

Run or hot-load the RAPP cartridge:

```bash
python3 cat-agent-skills/<slug>/<slug_with_underscores>_agent.py --tool
python3 cat-agent-skills/<slug>/<slug_with_underscores>_agent.py '{}'
```

The synthesized agent intentionally does not invent behavior. It preserves the
skill instructions and explicit parameter/deterministic fences. A prose-only
skill returns its instructions and inputs for the host to follow.

## Rebuild and verify

```bash
python3 scripts/import_cat_agent_skills.py \
  --source /path/to/cat-agent-skills
python3 scripts/validate_skills.py
python3 scripts/roundtrip_fidelity.py
```

The importer validates each pair in both directions, byte-compares a fresh
projection, runs the agent's `--tool` contract, and writes the collection only
after every item passes.

## Deliberate exclusions

| Submission | Reason |
|---|---|
| `awaiting-reply` | Scout automation JSON is not an Agent Skill |
| `copilot-agents-news-scout` | Scout automation JSON is not an Agent Skill |
| `pattern-radar-automation` | Scout automation JSON is not an Agent Skill |
| `spend-more-time-with-friends-and-family` | Scout automation JSON is not an Agent Skill |
| `vacation-urgent-forwarder` | archive contains no SKILL.md |

These are not silently converted because doing so would fabricate an Agent
Skill contract that the source repository does not claim.
