---
name: "ecosystem-audit"
description: "Audit a GitHub owner's whole ecosystem and prove or disprove the invariants its own docs assert: repo inventory and family shape, commit velocity in a window, star traction, declared-core-versus-actual-effort mismatch, and a mirror drift audit that catches silently diverged canonical documents. Use when asked to audit, map, heal, or health-check a multi-repo ecosystem, to find out whether a spec's mirrors still agree, or when a canonical doc may have drifted from the authority file it claims to render."
allowed-tools: "Bash, Read, Write"
license: "MIT"
---

# Ecosystem Audit

Answer one question with evidence: **is this ecosystem actually what its
documentation says it is?**

A sprawling multi-repo project fails quietly. Nothing breaks, no test goes red,
no build fails. Two files simply stop agreeing, a canonical document keeps
rendering a spec that was replaced, and a repo the docs call load-bearing stops
receiving commits. None of that is visible in a star count or a CI run. This
skill makes it cheap enough to check on a schedule.

## Inputs

Treat the user's request or `$ARGUMENTS` as the target. Derive:

- `OWNER` — the GitHub user or org. Required.
- `FAMILY` — a regex matched against repo name and description to define the
  family under audit (e.g. `rapp|brainstem`). Optional; omit to audit everything.
- `DAYS` — window size. Default 30.
- `CORE_REPOS` — the repos the documentation calls canonical, Tier 1, or
  load-bearing. These are the claims being tested.
- `MIRRORS` — URLs that some document asserts are byte-identical copies of one
  another. This is the highest-value input; supply it whenever the project
  claims a mirrored spec, registry, or manifest.

Make reasonable assumptions and proceed. Ask only when the owner is genuinely
ambiguous.

## Honesty contract

1. Report what was **measured**, never what was inferred from the measurement.
   A mirror that returns 404 is `unreachable`, not `drifted` — those are
   different failures with different fixes.
2. Never call a claim verified because the request succeeded. Verify the
   content, not the status code.
3. An unprobed repo is reported as `not probed`, never as inactive.
4. Distinguish public from total. `gh repo list` includes private repos for the
   authenticated owner; the REST users endpoint does not. Inflating a public
   count with private repos is the most common reporting error here.
5. State the token situation. An unauthenticated run has a 60 req/hr ceiling and
   may silently truncate; say so rather than presenting a partial sweep as full.

## Step 1 — Locate the runtime agent

The deterministic implementation ships beside this skill at
`references/github_ecosystem_agent.py`. It is a single-file RAPP agent: stdlib
only, no LLM, no API key required, read-only network. Prefer it over hand-rolled
`gh` one-liners — a hand-rolled sweep is how the failure modes below get missed.

```bash
SKILL_DIR="$(dirname "$0")"          # or the directory this SKILL.md lives in
AGENT="${SKILL_DIR}/references/github_ecosystem_agent.py"
```

If the agent is absent, fall back to `gh api` calls that reproduce the same four
stages, and say in the report that you did so.

## Step 2 — Run the audit

```bash
python3 - <<'PY'
import json, sys
sys.path.insert(0, "SKILL_DIR/references")
from github_ecosystem_agent import GitHubEcosystem

report = GitHubEcosystem().perform(
    owner="OWNER",
    family="FAMILY",
    days=30,
    velocity_limit=12,
    core_repos=["CORE_REPO_1", "CORE_REPO_2"],
    mirrors=[
        {"label": "MIRROR_A", "url": "https://raw.githubusercontent.com/.../spec.json"},
        {"label": "MIRROR_B", "url": "https://raw.githubusercontent.com/.../spec.json"},
    ],
)
print(json.dumps(report, indent=2))
PY
```

Substitute `SKILL_DIR`, `OWNER`, `FAMILY`, and the core/mirror lists. Omit
`mirrors` entirely when the project asserts no mirrored document; the drift stage
degrades to a clean skip rather than inventing a finding.

The agent returns four stages plus a one-line `headline`:

| stage | proves |
|---|---|
| `inventory` | public repo count, family match, created-in-window, dormancy |
| `velocity` | commits per repo in the window; pinned core repos always probed |
| `traction` | star distribution, and declared-core versus actual-effort |
| `drift` | whether asserted-identical mirrors are in fact identical |

On failure it returns `{"status": "error", "failed_stage": ..., "detail": ...,
"completed_stages": [...]}`. Report the failed stage. Never let an HTTP error
become a finding.

## Step 3 — Read the drift verdict first

`drift.verdict` is the highest-signal field in the whole report. It takes one of
four shapes:

- `ALIGNED: N mirrors are byte-identical` — the invariant holds.
- `DRIFTED: N mirrors resolved to M distinct hashes` — the documents diverged.
  Find the newest one and treat the others as stale.
- `BROKEN: byte-identical claim is unverifiable -- K of N mirrors unreachable` —
  a mirror is missing. The invariant cannot hold; it was never testable.
- `BROKEN: no asserted mirror is reachable` — the claim is entirely unfounded.

Then read `drift.declared_identity`. Each reachable mirror reports its own
`schema`, `version`, and `status` fields. A document that has silently changed
its `schema` or flipped `status` to something like `quarantined-candidate`,
`deprecated`, or `disabled` is the finding — regardless of what any human-facing
doc says about it.

## Step 4 — Test the documentation's own claims

For every `CORE_REPO`, `traction.declared_core_check` reports one of:

- `declared core, active` — the docs and the effort agree.
- `declared core, but near-zero attention and low velocity -- docs and effort
  disagree` — the documentation is describing an aspiration, not the project.
- `declared core, but velocity could not be measured` — fix the probe before
  concluding anything.
- `declared core repo not found` — the docs reference a repo that does not exist
  publicly. Either it is private or the name is wrong; both matter.

Where a project states a conflict rule — for example *"where this document and
that JSON disagree, the JSON wins"* — apply it literally. If the JSON now
declares the ecosystem quarantined, then by the project's own rule the
human-facing document is currently overruled. Say that plainly.

## Known failure modes

These are the traps that make a hand-rolled audit wrong. The agent handles each;
if you fall back to `gh`, handle them yourself.

**The 404 sentinel.** `raw.githubusercontent.com` serves missing files as
**HTTP 200 with a 14-byte `404: Not Found` body**. Any check that trusts the
status code records a missing mirror as present and identical. Always inspect the
body. This single trap is what hides a deleted mirror indefinitely.

**Private-repo inflation.** `gh repo list <owner>` includes private repos when
you are that owner. `GET /users/{owner}/repos` returns public only. Mixing them
overstates the public footprint. Pick one and label it.

**The unprobed core.** Velocity sampling by most-recently-pushed will skip a
dormant repo — which is exactly the repo a core-repo check exists to catch.
Pinned repos must jump the probe queue, or the check is vacuous.

**Commit-count saturation.** The commits endpoint caps at 100 per page. Past
that the exact number stops carrying information. Report `100+`, never a
paginated total that implies precision the window does not support.

**Rate-limit truncation.** Unauthenticated, the sweep dies partway and looks
like a small ecosystem. Check `report.authenticated` before believing a low
count.

## Completion checks

Do not present the audit as complete until all of these hold:

- `status` is `ok` and `completed_stages` contains all four stages.
- `authenticated` is reported, and any unauthenticated run is disclosed.
- Every supplied `CORE_REPO` has a `commits_in_window` that is not
  `not probed`.
- Every supplied mirror appears in `drift.mirrors` with an explicit
  `reachable` boolean and, where reachable, a `sha256`.
- The report distinguishes public counts from total counts in words.

## Healing actions

An audit that only describes is half the job. When a finding lands, state the
specific repair:

- **Mirror unreachable** — republish the file at the asserted path, or amend the
  document to stop asserting a mirror that does not exist. Do not leave the claim
  standing.
- **Mirrors drifted** — identify the newest, republish it to the others, and add
  a CI job that fails when their hashes differ. The check is one `sha256` per
  mirror; there is no excuse for it being manual.
- **Status flipped** — propagate the new `status`/`schema` into every document
  that renders it, and date-stamp the render so staleness is visible.
- **Declared core is dormant** — either revive the repo or demote it in the
  documentation. A doc that calls a dead repo Tier 1 teaches every new reader
  something false.
- **Declared core not found** — correct the name, or mark it private explicitly
  so readers stop looking for it.

Re-run the audit after the repair and show the verdict changing. A fix that does
not move `drift.verdict` did not fix anything.

## Reporting

Lead with `headline` — it is one line and carries inventory, velocity, traction,
and the drift verdict together. Then report findings in severity order: drift
first, declared-core mismatches second, inventory and traction shape last.

Keep the numbers exact and attributed. `385 public repos` is a finding;
`hundreds of repos` is not. When a count comes from a capped probe, carry the
cap into the sentence.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "type": "object",
  "properties": {
    "owner": {
      "type": "string",
      "description": "Derived from `<owner>` used in the documented command at line 143."
    }
  },
  "required": []
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
gh repo list
gh
gh api
gh
gh repo list <owner>
python3 - <<'PY'
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
