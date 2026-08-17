---
name: "rapplication-egg"
description: "Build a RAPPlication twin, pack it as a .egg, cubby it in a private egg hub (the batcave), and hatch it back on a clean path to prove it works. Use when asked to make something repeatable, \"hatch it as a twin\", cubby something, or ship a local-first app that takes a use case and produces a prototype."
---

# Building and cubbying a RAPPlication

Repo: your private egg hub (`<owner>/<egg-hub-repo>` — the author calls his the
"batcave"). Reference implementation to copy the shape from: a
`rapplications/<slug>/` directory in that repo.

## The two manifests

There are **two different manifests** and confusing them wastes a cycle.

| File | Schema | Where |
|---|---|---|
| `manifest.json` in the rapplication dir | `rapp-application/1.0` | repo |
| `<slug>.json` sidecar | `rapp-egg-hub-entry/1.0` | repo |
| `manifest.json` **inside** the egg | `brainstem-egg/2.1` | zip root |

Egg layout is `repo/<file>…` plus a root `manifest.json`. Nothing else.

## Generate the manifests from the bytes, never by hand

`build_egg.py` should pack, then compute `sha256` and `size_bytes` from the file
it just wrote and rewrite both manifests. Hand-maintained digests drift and the
hatch then fails its own verification for no reason.

Refuse to pack if a declared engine file is missing — a silently incomplete egg
hatches and then fails at runtime, which is much harder to diagnose.

## Local-first is a hard boundary

The egg carries **the engine only**. The user's use cases, information and
outputs live on device (`~/.rapp/<slug>/…`) and never enter the repo or the egg.
State that in `soul.md` and enforce it in the packer's file list.

## The hatch is the proof, and it must be hostile to itself

`hatch.sh` must:

1. `git clone --depth 1` the batcave **fresh from GitHub** into a path that did
   not exist when the script started
2. Verify the egg's sha256 against the published `manifest.json` and **exit
   non-zero on mismatch**
3. Unpack, start the server, and drive every endpoint in the contract
4. Reuse **nothing** from the build tree

A pass that touches the build tree is not a pass. Prove the clean path by
refusing to run into an existing directory.

Drive at least two probes with opposite expectations — one input that should
succeed and one that should be refused. A hatch that only shows the happy path
proves half of what you need.

## Build it by fan-out with blind critics

Freeze a `CONTRACT.md` first — file ownership, the exact API surface, the data,
the laws. Then one agent per component, each with a **separate harsh critic** who
blind-compares against the real artifact. The orchestrator lays the foundation;
parallel agents that start before the contract is frozen produce pieces that
don't fit together.

Findings this actually caught, all of which the builders missed:

- A record citing a source that **did not exist** had its figure printed and was
  stamped "lodgeable" — the check tested that a source id was non-empty, never
  that it resolved
- An untraceable number escaped through a free-text field, printing the figure
  on the line that claimed to withhold it
- Two components each invented their own "validated dataset" and disagreed on
  every figure; one file's parts summed to $3.86B beside its own $4.82B total
- An engine that looked brilliant because its author had written the answers into
  his own test fixture as bullet points

That last one is the lesson: **never accept a sample the builder authored as
evidence the builder works.** Supply the real input yourself.

## One dataset module, proving itself at import

Put the canonical data in one module with a `verify()` that asserts the
arithmetic closes, and **call it at import time**. Two components can then never
disagree, because breaking a figure fails everything loudly and immediately.

Ship deliberately defective records if the product's whole claim is about
handling them — one unsourced, one citing a source that is not held — so the law
is visible on every run without needing a test.

## Prefer refusal to a confident guess

If a deterministic path genuinely cannot do the job, make it **refuse and say
what it needs**, naming what it saw. An honest floor beats a mad-lib. A good
refusal names the actor, the source of truth, the nouns it found, and asks for
one line per action.

## Related

`/cs-agent-live`, `/tab-film` for the cloud half and the film.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `rapplication_egg_agent.py` and embedded as the fenced Python below (sha256 805ce138cad3a5cf…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `rapplication_egg_agent.py` first:

```bash
python3 rapplication_egg_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 rapplication_egg_agent.py   # or on stdin
python3 rapplication_egg_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""RapplicationEgg -- Build a RAPPlication twin, pack it as a .egg, cubby it in a private egg hub (the batcave), and hatch it back on a clean path to prove it works. Use when asked to make something repeatable, "hatch it as a twin", cubby something, or ship a local-first app that takes a use case and produces a prototype.

Generated by the rapp skill from rapplication-egg. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE a brainstem -- stay executable anyway.
    class BasicAgent:  # noqa: D101 - minimal stand-in, same contract
        def __init__(self, name=None, metadata=None):
            if name:
                self.name = name
            if metadata:
                self.metadata = metadata

        def perform(self, **kwargs):
            return "Not implemented."

        def system_context(self):
            return None

        def to_tool(self):
            return {"type": "function", "function": {
                "name": self.name,
                "description": self.metadata.get("description", ""),
                "parameters": self.metadata.get("parameters", {})}}

# The procedural layer, verbatim from the source capability.
INSTRUCTIONS = '# Building and cubbying a RAPPlication\n\nRepo: your private egg hub (`<owner>/<egg-hub-repo>` — the author calls his the\n"batcave"). Reference implementation to copy the shape from: a\n`rapplications/<slug>/` directory in that repo.\n\n## The two manifests\n\nThere are **two different manifests** and confusing them wastes a cycle.\n\n| File | Schema | Where |\n|---|---|---|\n| `manifest.json` in the rapplication dir | `rapp-application/1.0` | repo |\n| `<slug>.json` sidecar | `rapp-egg-hub-entry/1.0` | repo |\n| `manifest.json` **inside** the egg | `brainstem-egg/2.1` | zip root |\n\nEgg layout is `repo/<file>…` plus a root `manifest.json`. Nothing else.\n\n## Generate the manifests from the bytes, never by hand\n\n`build_egg.py` should pack, then compute `sha256` and `size_bytes` from the file\nit just wrote and rewrite both manifests. Hand-maintained digests drift and the\nhatch then fails its own verification for no reason.\n\nRefuse to pack if a declared engine file is missing — a silently incomplete egg\nhatches and then fails at runtime, which is much harder to diagnose.\n\n## Local-first is a hard boundary\n\nThe egg carries **the engine only**. The user\'s use cases, information and\noutputs live on device (`~/.rapp/<slug>/…`) and never enter the repo or the egg.\nState that in `soul.md` and enforce it in the packer\'s file list.\n\n## The hatch is the proof, and it must be hostile to itself\n\n`hatch.sh` must:\n\n1. `git clone --depth 1` the batcave **fresh from GitHub** into a path that did\n   not exist when the script started\n2. Verify the egg\'s sha256 against the published `manifest.json` and **exit\n   non-zero on mismatch**\n3. Unpack, start the server, and drive every endpoint in the contract\n4. Reuse **nothing** from the build tree\n\nA pass that touches the build tree is not a pass. Prove the clean path by\nrefusing to run into an existing directory.\n\nDrive at least two probes with opposite expectations — one input that should\nsucceed and one that should be refused. A hatch that only shows the happy path\nproves half of what you need.\n\n## Build it by fan-out with blind critics\n\nFreeze a `CONTRACT.md` first — file ownership, the exact API surface, the data,\nthe laws. Then one agent per component, each with a **separate harsh critic** who\nblind-compares against the real artifact. The orchestrator lays the foundation;\nparallel agents that start before the contract is frozen produce pieces that\ndon\'t fit together.\n\nFindings this actually caught, all of which the builders missed:\n\n- A record citing a source that **did not exist** had its figure printed and was\n  stamped "lodgeable" — the check tested that a source id was non-empty, never\n  that it resolved\n- An untraceable number escaped through a free-text field, printing the figure\n  on the line that claimed to withhold it\n- Two components each invented their own "validated dataset" and disagreed on\n  every figure; one file\'s parts summed to $3.86B beside its own $4.82B total\n- An engine that looked brilliant because its author had written the answers into\n  his own test fixture as bullet points\n\nThat last one is the lesson: **never accept a sample the builder authored as\nevidence the builder works.** Supply the real input yourself.\n\n## One dataset module, proving itself at import\n\nPut the canonical data in one module with a `verify()` that asserts the\narithmetic closes, and **call it at import time**. Two components can then never\ndisagree, because breaking a figure fails everything loudly and immediately.\n\nShip deliberately defective records if the product\'s whole claim is about\nhandling them — one unsourced, one citing a source that is not held — so the law\nis visible on every run without needing a test.\n\n## Prefer refusal to a confident guess\n\nIf a deterministic path genuinely cannot do the job, make it **refuse and say\nwhat it needs**, naming what it saw. An honest floor beats a mad-lib. A good\nrefusal names the actor, the source of truth, the nouns it found, and asks for\none line per action.\n\n## Related\n\n`/cs-agent-live`, `/tab-film` for the cloud half and the film.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class RapplicationEggAgent(BasicAgent):
    def __init__(self):
        self.name = 'RapplicationEgg'
        self.metadata = {
          "name": "RapplicationEgg",
          "description": "Build a RAPPlication twin, pack it as a .egg, cubby it in a private egg hub (the batcave), and hatch it back on a clean path to prove it works. Use when asked to make something repeatable, \"hatch it as a twin\", cubby something, or ship a local-first app that takes a use case and produces a prototype.",
          "parameters": {
            "type": "object",
            "properties": {},
            "required": []
          }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        return json.dumps({"status": "ok", "instructions": INSTRUCTIONS,
                           "inputs": kwargs,
                           "note": "Prose-only capability: follow INSTRUCTIONS "
                                   "with the given inputs."}, indent=2)

if __name__ == "__main__":
    #     echo '{"arg": "value"}' | python3 rapplication_egg_agent.py
    #     python3 rapplication_egg_agent.py '{"arg": "value"}'
    #     python3 rapplication_egg_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(RapplicationEggAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(RapplicationEggAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
