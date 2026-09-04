# rapp-skills

Skills you can use, share as one file, and take anywhere. Why: [CHARTER.md](CHARTER.md).

- **Use one.** Put a skill's folder, or just its `SKILL.md`, where your AI tool reads skills, then
  ask for it in plain words. It carries its own code and a small launcher, so it just runs.
- **Share one.** The `SKILL.md` file is the whole thing. Send it. Nothing to install.
- **Take one somewhere else.** When a skill needs to run on a server or be shared with a team as
  one Python file, make it one. Nothing is lost, and it turns back into a skill any time.

Works in Claude Code and GitHub Copilot CLI today, and in anything else that reads
[Agent Skills](https://agentskills.io). There is nothing to install, and nothing to uninstall:
delete a skill's folder and your AI is back to exactly how it was.

## Use a skill

| Your tool | Put the skill here |
|---|---|
| Claude Code | `~/.claude/skills/<name>/` or `<project>/.claude/skills/<name>/` |
| GitHub Copilot CLI | `~/.copilot/skills/<name>/` or `<project>/.github/skills/<name>/` |
| Anything else that reads skills | its skills folder |

Try it with [`skills/hello-world`](skills/hello-world): copy the folder, then ask your tool to
"use the hello-world skill to greet me".

## Let your AI make and move skills

Give your AI this one file and it can do the conversions for you:

```
https://raw.githubusercontent.com/kody-w/rapp-skills/main/skills/rapp-skills/SKILL.md
```

Tell it, for example, "get that file and turn my_agent.py into a skill I can send to a colleague".
The file carries its own code. Tools that fetch abilities on their own can also pick this
repository up directly; that just happens, and you never need to know how.

## Make and move skills yourself

Python 3.11 or newer, nothing else.

```bash
python3 rapp_skills.py to-skill path/to/my_agent.py     # a skill anyone can use, from a Python agent file
python3 rapp_skills.py to-agent skills/my-agent          # one Python file for a server; the original comes back unchanged
python3 rapp_skills.py to-agent path/to/steps-skill      # a skill written as steps becomes a Python file that hands those steps to the AI running it
python3 rapp_skills.py check skills/*                    # find problems before sharing
python3 rapp_skills.py prove path/to/my_agent.py         # shows nothing is lost there and back: PASS or FAIL
python3 rapp_skills.py run skills/hello-world --json '{"name": "Ada"}'
```

## Lock a file for travel

When a private file has to cross something public (a message, a shared drive), lock it. The
header stays readable so a host knows what it is; everything else is encrypted with a passphrase
only you know. Needs the `openssl` command, present on macOS, Linux, and Git for Windows.

```bash
SKILL_PASSPHRASE='...' python3 rapp_skills.py lock   my-skills/vbrainstem --out locked
SKILL_PASSPHRASE='...' python3 rapp_skills.py unlock locked/vbrainstem     --out unlocked   # byte-identical
```

The better lock for a person's own file is a private GitHub repository linked from their public
front door; see https://github.com/kody-w/vbrainstem. Use the passphrase lock when there is no
GitHub in the loop.

## Back up or restore a whole Brainstem

A Brainstem's agents are ordinary Python files in its `agents/` folder, and a skill dropped in
becomes one of them with no restart. So plain skill files are a complete backup of everything a
Brainstem knows how to do, readable by any AI, and a Brainstem can be rebuilt from them:

```bash
python3 rapp_skills.py to-skill ~/.brainstem/src/rapp_brainstem/agents --out ~/my-skills     # back up: every agent becomes a skill
python3 rapp_skills.py to-agent ~/my-skills --out ~/.brainstem/src/rapp_brainstem/agents      # restore: every skill is an agent again, unchanged
```

## What is inside a skill file

A short header your tool reads (name, description, what it needs). How to run it. Then the code
that does the work, unchanged, with its checksum, and the small launcher that runs it. The
launcher writes nothing anywhere. If a skill's code saves something, it goes under one folder,
`~/.agent-storage`, and deleting that folder erases it. Nothing in
the file names this project or any other platform. Open
[`skills/hello-world/SKILL.md`](skills/hello-world/SKILL.md) to see one.

## For builders

`hosts/<tool>.json` describes each AI tool this works in: where it reads skills, how it fetches
abilities on its own, and the version it was verified on with evidence. Supporting a new tool is
adding a file; `python3 rapp_skills.py sync` rewrites every tool-specific file from it, including the
converter skill's embedded copy of its own code, and CI fails if anything drifts. See
[HOSTS.md](HOSTS.md).

Deeper capabilities (verifiable packaging, a server runtime) exist in the wider
[RAPP](https://github.com/kody-w/RAPP) project and are reached from the one Python file
`to-agent` makes. They are never required, and nothing here mentions them to a user.

MIT.
