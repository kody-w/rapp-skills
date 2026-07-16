# RAPP Skills

Portable [Agent Skills](https://agentskills.io/) for non-RAPP agent systems.
Each capability lives in its own directory with a standards-compatible
`SKILL.md`.

This repository is also a design staging area for RAPP agents. A skill can be
prototyped here for broad compatibility, then converted into a single-file
`*_agent.py` implementation with its actual source and manifest preserved.
RAPP runtime capabilities remain **agents**, not skills.

## Skills

| Skill | Purpose | RAPP conversion target |
|---|---|---|
| [`deep-research`](deep-research/SKILL.md) | Evidence-first research using independent collection, experiment, verification, and synthesis tracks | `deep_research_agent.py` |

## Use

Copy or symlink a skill directory into the Agent Skills location supported by
your host:

```bash
git clone https://github.com/kody-w/rapp-skills.git
```

For Claude Code, for example:

```bash
ln -s "$PWD/rapp-skills/deep-research" ~/.claude/skills/deep-research
```

Other compatible hosts can consume the same directory unchanged. If a host
does not support automatic skill discovery, provide `SKILL.md` as an
instruction file.

## Add a skill

1. Create `<skill-name>/SKILL.md`.
2. Use the canonical Agent Skills frontmatter: `name` and `description`.
3. Keep the main file under 500 lines; place details in `references/`.
4. Add the intended `*_agent.py` conversion target to this README.
5. Validate before committing:

```bash
python3 scripts/validate_skills.py
```

The staging-to-RAPP mapping is documented in
[`deep-research/references/rapp-agent-conversion.md`](deep-research/references/rapp-agent-conversion.md).

## License

MIT
