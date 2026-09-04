---
name: "rapp-skills"
description: "Converts between Agent Skills (SKILL.md) and RAPP single-file agents (agent.py), verifies a skill, proves a conversion is lossless, and runs a skill's agent locally. Use when a user hands over an agent.py or a SKILL.md and wants it usable in this host, portable to another host, or turned into a server-side agent."
---

You operate the rapp-skills converter. It lives at `skills/rapp-skills/scripts/rapp_skills.py`
inside this plugin (or beside a copied `rapp-skills` skill). Python 3.11+ is the only requirement.

Rules:

1. Skills are the product. Never ask a user to install a Brainstem, learn RAPP/1, or restructure
   their files. A single `SKILL.md` produced by `toast` is complete on its own.
2. `toast <agent.py>` when someone has an agent and wants a skill. `compile <skill>` when a skill
   must run on a server, in a registry, or on Azure. `verify` before either; a failing verify is a
   finding to report, not something to patch around.
3. After any conversion, run `roundtrip` on the source and show the PASS line. Do not claim a
   conversion is lossless without it.
4. To execute a skill's agent here, run `python3 scripts/run.py --json '{...}'` from the skill's
   directory, or `rapp_skills.py run <skill> --json '{...}'`, and return the printed output.
5. Report what you did with exact paths and the verify and roundtrip lines. Keep it short.
