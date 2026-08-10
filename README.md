# RAPP Skills

Portable Agent Skills backed by RAPP single-file agents.

Each capability is a pair:

```text
<skill>/
├── SKILL.md
└── <slug>_agent.py
```

The Python file is the executable cartridge. The `SKILL.md` is its Agent Skill
projection: complete Python inline, a checksum-verified capsule carrying the
byte-exact original, and instructions for hosts that can or cannot execute the
linked file. One pair moves unchanged between Copilot Studio, Cowork, Scout,
RAPP Brainstem, and other Agent Skill hosts.

## One engine

The repository vendors the exact
[`rapp-agent-converter`](engine/rapp-agent-converter/SKILL.md) skill submitted
to the CAT Agent Skills gallery:

```text
engine/rapp-agent-converter/
├── SKILL.md
├── scripts/toast.py
├── references/
└── assets/hello_rapp_agent.py
```

All conversion logic lives there. The root [`toast.py`](toast.py) is only a
launcher, so this repository cannot drift into a second implementation.

```bash
python3 toast.py convert <agent.py> --to skill -o out/SKILL.md
python3 toast.py convert <SKILL.md> --to agent
python3 toast.py roundtrip <agent.py>
python3 toast.py inspect <path>
python3 toast.py selftest
```

Python 3.9+, standard library only, fully offline. The converter parses agents
with `ast`; it never imports or executes a file to read it.

## What the pair guarantees

- `agent.py → SKILL.md → agent.py` restores the exact original bytes.
- The generated skill ships a byte-exact linked agent beside it.
- The complete Python also travels inside `SKILL.md`, so the skill remains
  self-contained if the linked file is separated.
- A checksum mismatch or edit inside the generated Python fence is an explicit
  refusal, not a best-effort recovery.
- Hosts with Python run the linked agent directly. Instruction-only hosts use
  the same code and parameter schema as the exact specification.

The old repo-wide "toast/soak/capability-id" laboratory is not the contract
here. Fidelity is the concrete property the submitted skill proves: the
canonical agent leaves and returns byte-identical.

## Verify the repository

```bash
python3 scripts/validate_skills.py
python3 scripts/roundtrip_fidelity.py
```

`roundtrip_fidelity.py` uses only the converter's public CLI. For every
committed capability it:

1. proves the agent round trip is byte-identical;
2. restores the agent from the companion `SKILL.md` and compares bytes;
3. runs `--tool` and validates the emitted function contract.

There are **99 verified capability pairs**: 23 RAPP-native pairs at the
repository root and 76 assimilated CAT Agent Skills under
[`cat-agent-skills/`](cat-agent-skills/). The converter under `engine/` is the
100th `SKILL.md`, but it is infrastructure and is not counted as a converted
capability pair.

## CAT Agent Skills catalog

[`cat-agent-skills/`](cat-agent-skills/) is the worked demonstration of this
pattern at ecosystem scale. It imports every actual Agent Skill from
`microsoft/cat-agent-skills`, preserves the complete agent-facing bundle, and
places the synthesized RAPP cartridge beside the final capsule-bearing
`SKILL.md`.

```text
cat-agent-skills/
├── catalog.json
├── README.md
└── <76 skill directories>/
    ├── SKILL.md
    ├── <slug>_agent.py
    └── scripts/ references/ assets/ ... when present
```

The catalog records source commit/path/hash, final skill and agent hashes,
tool-contract counts, supporting files, and the five non-skill submissions
that were deliberately excluded. All 76 source skills currently lack an
explicit `## Parameters` schema, so their agents are honestly recorded as
untyped launchpads instead of receiving invented contracts. Each launchpad was
also executed with `{}` and returned the preserved source instructions for its
host to follow. Rebuild it with:

```bash
python3 scripts/import_cat_agent_skills.py \
  --source /path/to/cat-agent-skills
```

## Skills

### RAPP and agent pipeline

- [`rapp-agent-bridge`](rapp-agent-bridge/SKILL.md) — consume a linked-agent
  pair without paraphrasing it.
- [`rapp-brainstem`](rapp-brainstem/SKILL.md) — drive the local brainstem over
  its single `/chat` endpoint.
- [`rapp-pipeline`](rapp-pipeline/SKILL.md) — transcript-to-agent pipeline and
  promotion outputs.
- [`rapp1-compliance-sweep`](rapp1-compliance-sweep/SKILL.md) — RAPP/1 estate
  compliance and remediation.
- [`brainstem-reset`](brainstem-reset/SKILL.md) — first-user clean-install
  verification.

### Research and knowledge

- [`deep-research`](deep-research/SKILL.md)
- [`transcript-miner`](transcript-miner/SKILL.md)
- [`obsidian-vault-steward`](obsidian-vault-steward/SKILL.md)
- [`harvest`](harvest/SKILL.md)
- [`digital-twin-builder`](digital-twin-builder/SKILL.md)
- [`kody-twin`](kody-twin/SKILL.md)

### Build, deploy, and prove

- [`demo-ship`](demo-ship/SKILL.md)
- [`mcs-deploy`](mcs-deploy/SKILL.md)
- [`ship`](ship/SKILL.md)
- [`exec-proof`](exec-proof/SKILL.md)
- [`flex-unbrick`](flex-unbrick/SKILL.md)
- [`film-m365`](film-m365/SKILL.md)
- [`estate-sweep`](estate-sweep/SKILL.md)

### Working style

- [`msft-deck`](msft-deck/SKILL.md)
- [`muscle`](muscle/SKILL.md)
- [`overnight`](overnight/SKILL.md)
- [`wow`](wow/SKILL.md)
- [`fy27-priority-agents`](fy27-priority-agents/SKILL.md)

## Use

Clone the repository and install or symlink the skill directory your host
should discover:

```bash
git clone https://github.com/kody-w/rapp-skills.git
ln -s "$PWD/rapp-skills/deep-research" ~/.claude/skills/deep-research
```

Install `engine/rapp-agent-converter` as a skill when the host should be able to
convert RAPP cartridges and Agent Skills itself.

## Add a capability

1. Write or add the canonical `*_agent.py`.
2. Project it with the repository engine:

   ```bash
   python3 toast.py convert path/to/foo_agent.py \
     --to skill -o foo/SKILL.md
   ```

3. Commit both files emitted in `foo/`.
4. Run:

   ```bash
   python3 scripts/validate_skills.py
   python3 scripts/roundtrip_fidelity.py
   ```

Never hand-edit generated content or the capsule. Edit the canonical agent and
project it again.

## License

MIT
