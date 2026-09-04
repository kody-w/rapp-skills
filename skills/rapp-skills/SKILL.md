---
name: "rapp-skills"
description: "Convert an Agent Skill (SKILL.md) to a RAPP single-file agent (agent.py) or back, verify a skill against the open Agent Skills standard, prove the conversion is lossless, and run a skill's bundled agent locally. Use when a user hands over an agent.py or a SKILL.md and wants it usable here, portable to another AI host, or turned into a server-side agent."
license: "MIT"
compatibility: "Requires python3 (3.11+). No other dependencies."
metadata:
  rapp-skills: "1.0.0"
  source: "converter"
---

# RAPP Skills

Skills are the unit. A skill produced here is a plain Agent Skill: it works in Claude Code,
GitHub Copilot CLI, and any other host that reads `SKILL.md`, with or without a plugin. When a
skill has to scale beyond one host (a server, a team registry, Azure, a Brainstem), it converts to
a RAPP single-file `agent.py` without loss, and back again.

All commands run from this skill's directory with `python3 scripts/rapp_skills.py <command>`.

## Commands

| Command | What it does |
|---|---|
| `toast <agent.py> [--out skills] [--origin URL] [--license MIT]` | agent.py to `skills/<name>/SKILL.md` with the agent and a runner embedded, plus `scripts/agent.py` and `scripts/run.py` |
| `compile <skill-dir or SKILL.md> [--out agents]` | skill to `<name>_agent.py`. A skill with an agent gives back the agent byte-identically; a hand-written skill becomes a playbook agent whose `perform` returns the skill text rendered with the inputs |
| `verify <skill> ...` | frontmatter within the six standard fields, name and directory agree, parameters are a JSON object schema, embedded agent matches its sha256 and loads |
| `roundtrip <agent.py or skill>` | proves `compile(toast(x)) == x` or `toast(compile(skill)) == skill`; prints PASS or FAIL |
| `run <skill> --json '{...}'` | executes the skill's agent locally and prints the result |

## How to decide

- The user has an `agent.py` and wants to use it here or hand it to someone: `toast`, then `verify`.
- The user has a `SKILL.md` and needs it on a server, shared, versioned, or in a Brainstem: `verify`, then `compile`.
- Either way, finish with `roundtrip` and show its line. Do not claim lossless without it.

## What a toasted skill contains

Frontmatter with only `name`, `description`, `license`, `compatibility`, `metadata`
(strings: the tool name, the agent's sha256, version, author, origin). Then the parameters as a
JSON block, run instructions, an optional one-paragraph note on scaling, the agent itself between
`<!-- rapp-agent -->` markers, and the runner between `<!-- rapp-runner -->` markers. A user handed
only that file can run it: save the two blocks and `python3 run.py --json '{...}'`.
