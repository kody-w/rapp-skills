# rapp-skills

**One `SKILL.md` is all a user needs.** Every skill here is a plain
[Agent Skill](https://agentskills.io) that works in Claude Code, GitHub Copilot CLI, and any other
host that reads `SKILL.md`, with or without a plugin. When a skill has to scale beyond one host,
it converts losslessly into a RAPP single-file `agent.py` and back.

```
agent.py  ──toast───▶  SKILL.md          runs in any skill host, no server, no install
SKILL.md  ──compile─▶  agent.py          runs in a Brainstem, a registry, Azure, Copilot Studio
```

`compile(toast(agent.py))` is byte-identical to the original. `toast(compile(SKILL.md))` gives the
same skill back. The tests prove both on every commit.

## Use a skill

Copy one skill folder, or just its `SKILL.md`, into wherever your host reads skills:

| Host | Put it in |
|---|---|
| Claude Code | `~/.claude/skills/<name>/SKILL.md` or `<project>/.claude/skills/<name>/SKILL.md` |
| GitHub Copilot CLI | `~/.copilot/skills/<name>/SKILL.md` or `<project>/.github/skills/<name>/SKILL.md` |
| Anything else that reads Agent Skills | its skills directory |

Then ask for it in plain words. The skill carries its own agent and a small runner, so the host
runs the exact same code a RAPP Brainstem would. No Brainstem, no plugin, no account.

Or install the plugin, which adds the converter skill and a subagent:

```
/plugin marketplace add kody-w/rapp-skills
/plugin install rapp-skills@rapp-skills
```

The same two lines work in Claude Code and in Copilot CLI. See [HOSTS.md](HOSTS.md) for every host,
the version it was verified on, and the paths it reads.

## Convert

```bash
python3 rapp_skills.py toast path/to/my_agent.py            # -> skills/my-agent/SKILL.md (+ scripts/)
python3 rapp_skills.py compile skills/my-agent               # -> agents/my_agent_agent.py, byte-identical
python3 rapp_skills.py compile path/to/handwritten-skill     # -> a playbook agent: perform() returns the skill, rendered
python3 rapp_skills.py verify skills/*                       # standard fields, name, schema, embedded agent sha256
python3 rapp_skills.py roundtrip path/to/my_agent.py         # PASS or FAIL
python3 rapp_skills.py run skills/hello-world --json '{"name": "Ada"}'
```

Python 3.11 or newer, nothing else.

## What a toasted skill looks like

Frontmatter with only the six standard fields. The parameters as a JSON block. How to run it.
Then the agent itself, byte-exact between `<!-- agent -->` markers with its sha256, and the runner
between `<!-- runner -->` markers. Nothing in the file names this project or any other platform:
a host is fed one ordinary skill, and the agent inside it is simply how the skill runs. See
[`skills/hello-world/SKILL.md`](skills/hello-world/SKILL.md).

A hand-written skill with no agent compiles to a playbook agent: `perform` returns the skill text
rendered with the inputs, for whichever model is hosting it to carry out.

## Where RAPP comes in

Nowhere, until it is needed. The skill format never carries a RAPP-only field. When a user wants
a skill on a server, shared with a team, versioned and verified, or running in a Brainstem, `compile`
produces the `agent.py` and the [RAPP](https://github.com/kody-w/RAPP) side takes over. Wrapping a
skill in a verifiable jacket or packing an agent as a RAPP/1 egg are later, opt-in steps that reuse
[rapp-1](https://github.com/kody-w/rapp-1) rather than re-implementing it.

## Layout

```
skills/rapp-skills/          the converter skill (SKILL.md + scripts/rapp_skills.py)
skills/<name>/               shipped skills, each self-contained
agents/rapp-skills.md        the subagent; projected to .github/agents/ for Copilot CLI
hosts/<host>.json            one adapter per host: paths, manifest, install, verified version
plugin.json                  plugin manifest; projected to .claude-plugin/ and .github/plugin/
tests/                       round-trip, standard-conformance, drift
```

Generated files are rebuilt by `python3 rapp_skills.py manifests`; CI fails if they drift.

## License

MIT.
