---
name: "rapp-skills"
description: "Turn a Python agent file into a skill anyone can use, turn a skill into one Python file that can run on a server, check a skill for problems, show nothing was lost either way, and run a skill's code locally. Use when a user hands over an agent file or a skill and wants to use it here, share it as one file, or take it somewhere else."
license: "MIT"
compatibility: "Requires python3 (3.11+). No other dependencies."
metadata:
  source: "converter"
---

# RAPP Skills

What you can do with this, in plain words:

- **Use a skill.** Put a skill's folder, or just its `SKILL.md`, where your AI tool reads skills and
  ask for it. It carries its own code and a small launcher, so it just runs.
- **Share a skill.** One `SKILL.md` file is the whole thing. Send it.
- **Take a skill somewhere else.** When it needs to run on a server or be shared with a team as one
  Python file, make it one. Nothing is lost, and you can turn it back into a skill any time.

All commands run from this skill's directory with `python3 scripts/rapp_skills.py <command>`.

| Command | What it does for the user |
|---|---|
| `to-skill <agent.py> [--out skills] [--origin URL] [--license MIT]` | makes a skill anyone can use out of a Python agent file, with the code and a launcher inside |
| `to-agent <skill or SKILL.md> [--out agents]` | makes one Python file out of a skill: the original code back, unchanged, or, for a skill written as steps, a file whose `perform` hands those steps and the inputs to whichever AI is running it |
| `check <skill> ...` | finds problems: a name that will not load, a missing field, code that does not match its checksum, inputs that do not match |
| `prove <agent.py or skill>` | shows nothing is lost going there and back; prints PASS or FAIL |
| `run <skill> --json '{...}'` | runs the skill's code here and prints the result |

How to choose: someone has an agent file and wants to use or share it: `to-skill`, then `check`.
Someone has a skill and needs it on a server or as one Python file: `check`, then `to-agent`.
Either way finish with `prove` and show its line.

Talk to the user in capabilities, never in concepts. They should not need to learn a single term
to get their result.
