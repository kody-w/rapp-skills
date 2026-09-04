# Hosts

Each host is one JSON adapter in `hosts/`. Adding an ecosystem is adding a file.

| Host | Verified version | Verified on | Skills read from | Plugin manifest | Marketplace | Agents |
|---|---|---|---|---|---|---|
| Claude Code | 2.1.260 | 2026-09-04 | `~/.claude/skills/<name>/SKILL.md`, `<project>/.claude/skills/<name>/SKILL.md`, `<plugin>/skills/<name>/SKILL.md` | `.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` | `agents/*.md` |
| GitHub Copilot CLI | 1.0.83 | 2026-09-04 | `~/.copilot/skills/<name>/SKILL.md`, `<project>/.github/skills/<name>/SKILL.md`, `<project>/.claude/skills/<name>/SKILL.md`, `<project>/.agents/skills/<name>/SKILL.md` | `plugin.json` | `.github/plugin/marketplace.json` | `.github/agents/*.agent.md` |

## Install

**Claude Code**

```
/plugin marketplace add kody-w/rapp-skills
/plugin install rapp-skills@rapp-skills
```

Skill invocation: `/rapp-skills:<skill> or a plain request that matches the skill description`. Instruction files read: `CLAUDE.md`. Docs: https://code.claude.com/docs/en/skills

Verified: 2026-09-04, Claude Code 2.1.260, `claude -p` with `skills/hello-world` copied to `<project>/.claude/skills/`: the skill was selected, `scripts/run.py --json '{"name": "Kody"}'` ran, and the exact output `Hello, Kody! Welcome to the RAPP Agent ecosystem.` was reported. No plugin installed.

**GitHub Copilot CLI**

```
/plugin marketplace add kody-w/rapp-skills
/plugin install rapp-skills@rapp-skills
```

Skill invocation: `/<skill> or a plain request that matches the skill description`. Instruction files read: `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`. Docs: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills

Verified: 2026-09-04, GitHub Copilot CLI 1.0.83, `copilot -p -s --allow-all-tools` with `skills/hello-world` copied to `<project>/.github/skills/`: the skill was selected, `cd .github/skills/hello-world && python3 scripts/run.py --json '{"name": "Kody"}'` ran, and the exact output was reported. No plugin installed. A copy under `~/.copilot/skills` was read but its scripts were execution-restricted outside the working directory; the project path is the reliable one.
