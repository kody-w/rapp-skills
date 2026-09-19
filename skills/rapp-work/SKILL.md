---
name: "rapp-work"
description: "Safely verify, inspect, discover, scaffold, update, or migrate RAPP Work through the exact canonical SDK and RAPP/1 checkout. Use when someone wants the same plan-first RAPP Work workflow from Claude Code, GitHub Copilot CLI, or another Agent Skills host without copying protocol logic into the host."
license: "MIT"
compatibility: "Requires Python 3.11+, Git, and exact local checkouts pinned in agent.lock. Scaffold apply also requires no-follow file reads and native no-replace directory activation (Linux/macOS); unsupported platforms refuse. Discovery optionally uses credential-free HTTPS. Nothing is cloned or installed automatically."
metadata:
  version: "1.0.0"
  lock: "agent.lock"
  runner: "scripts/run.py"
allowed-tools: "Bash Read"
---

# RAPP Work

Use the exact local RAPP Work SDK/CLI for all protocol behavior. This folder is a
small locked adapter; it does not reproduce RAPP/1 or RAPP Work rules.

## Operations

Run from this skill's directory:

```bash
python3 scripts/run.py --root /path/to/work                 # verify (default)
python3 scripts/run.py status --root /path/to/work
python3 scripts/run.py discover --discover-root /path/to/search
python3 scripts/run.py discover --api-base https://...      # pinned static JSON
python3 scripts/run.py scaffold --root /new/workspace \
  --kind workspace --owner-label owner --slug project --world-id world
python3 scripts/run.py update --root /path/to/work
python3 scripts/run.py migrate --source /old/work --target /new/work
```

The six supported operations are:

- `verify` — verify this adapter, the exact SDK checkout, the exact RAPP/1
  checkout, and the selected workspace through the canonical SDK;
- `status` — report resolution sources, pending pins, and safety defaults
  without running downloaded code;
- `discover` — inspect explicit local roots through the canonical SDK, or,
  when `--api-base` is explicit/configured, fetch one checksum-pinned JSON
  index as inert metadata;
- `scaffold` — plan creation of a new Workspace or Organization;
- `update` — plan a forward update of an existing RAPP Work setup; and
- `migrate` — plan the canonical historical migration lane.

## Exact dependency resolution

Resolution is deterministic and stops on an invalid higher-priority value:

1. explicit `--sdk-path`, `--rapp1-path`, or `--api-base`;
2. `RAPP_WORK_SDK_PATH`, `RAPP1_PATH`, or `RAPP_WORK_API_BASE`;
3. bounded local discovery beside the current project; then
4. for status reporting only, the exact commit-pinned API base in `agent.lock`.

The runner never clones a repository, installs a package, follows a discovered
download as code, or substitutes a branch, tag, or "latest" release. Local SDK
and RAPP/1 checkouts must be clean Git checkouts at the exact locked commits.
The SDK entrypoint, RAPP/1 specification, and RAPP/1 reference must match their
full SHA-256 values, and the SDK's own parent-pin file must name those same
exact protocol bytes. Replacement objects, hidden index flags, symlinked source,
ignored executable code, and any executable or importable SDK source file that
does not match its pinned commit blob are refused.

The shipped `agent.lock` finalizes the protocol, SDK, and static index together.
Every release pin must be pending together or final together; mixed states are
refused. The static API URL is derived from its exact commit and cannot name a
branch, tag, mirror, or different commit. A future pending lock is status-only:
every operation that would depend on one refuses.

## Plans and approval

`scaffold`, `update`, and `migrate` are plan-only by default. Return the printed
plan and its `plan_digest` to the user. Do not apply it unless the user
explicitly approves that exact plan. `plan_digest` and `plan_sha256` are two
names for the same SHA-256 of the complete native plan.

### Create from a saved, reviewed plan

Each scaffold plan creates a fresh identity. Save the **complete printed JSON
result**, not just its digest or selected actions. Planning does not create
the destination or save a file automatically. Choose an existing trusted
private review directory outside the new destination, then save explicitly:

```bash
(umask 077; set -C
 python3 scripts/run.py scaffold --root /new/workspace \
   --kind workspace --owner-label owner --slug project --world-id world \
   > /trusted/private-review/scaffold.json)
```

The shell settings make a newly saved ordinary file private and refuse an
existing ordinary output file; they do not make an unsafe output path safe.
Inspect the whole file and the command's exit status. Interrupted or refused
output is not an approved plan. After the user approves its exact lowercase
`plan_digest`, repeat the **same request** with both the file and that digest:

```bash
python3 scripts/run.py scaffold --root /new/workspace \
  --kind workspace --owner-label owner --slug project --world-id world \
  --plan /trusted/private-review/scaffold.json \
  --apply '<exact-lowercase-plan-digest>'
```

Use the same kind, mode, owner label, slug, world, and destination. The runner
reads the file once and passes its original full plan to the exact pinned
SDK's apply operation. It never replans, remints an identity, or substitutes
locally interpreted file actions during scaffold apply. Without `--plan`,
scaffold apply refuses. `--plan` without `--apply`, or on any other operation,
also refuses.

Saved results must be complete compatible planned results, at most one MiB,
with strict bounded JSON and matching digest aliases. Evidence must be a
regular, single-link file reached without traversal, symlinks, or protected
credential paths. A file change detected during the descriptor-based read
refuses. Unsupported safe-read platforms refuse rather than falling back.

The printed `lock_sha256` fingerprints the complete validated `agent.lock`.
Changing any locked adapter file (including these instructions), dependency
pin, or release-lock field requires explicit new planning and review. Older
output without this field refuses. This is a conservative compatibility
check, not a signature or proof of the original producer: the approved digest
covers the native plan, not the outer release metadata.

The native SDK checks the full plan, canonical files and identity, current
request, exact hash, and absence of the destination and its staging path. The
destination must not exist, even as an empty directory, and its parent must
already exist. Native activation does not replace an existing destination.
Only after the SDK confirms creation and the adapter checks the created
file bytes does the adapter report `applied`. Its `result` contains the actual
SDK reply, with the created identity and root in `result.result`.

The review file is never rewritten, removed, or marked consumed by apply;
retain or remove it explicitly. Replaying while the destination or staging
path exists refuses and leaves it alone. This is not eternal one-use approval
after deliberate deletion. An interrupted apply or missing/malformed success
reply can leave staging or a completed destination; it is not permission to
retry, delete, or replan automatically. Reconcile with explicit read-only
inspection/verification. Universal crash durability and continuous protection
against concurrent owner changes are not claimed.

### Update or migrate

```bash
python3 scripts/run.py update --root /path/to/work --apply '<exact-plan-digest>'
python3 scripts/run.py migrate --source /old/work --target /new/work \
  --apply '<exact-plan-digest>'
```

These existing operations recompute their current deterministic plan before
comparing the approved digest; they do not accept `--plan`. Their approved
file bytes are staged beside their target and published atomically per file;
an existing inode is never opened for writing or truncated. This adapter does
not use native update/migration checkpoint or recovery flows, and does not
promise an all-or-nothing multi-file transaction.

All mutation paths refuse different, shortened, uppercase, stale, or malformed
approval digests, traversal, symlinks, overlapping migration roots, non-empty
migration destinations, multiply linked or conflicting managed files,
protected action paths, unexpected file actions, and plans requesting network
effects, push, publication, or deployment.

## Safety boundary

- Never ask for, read, forward, or print credentials. The SDK receives a fresh
  environment without the caller's tokens, secrets, cookies, authentication
  variables, Python path, or home configuration.
- Network access is disabled for SDK operations. `discover --api-base ...` is
  the only direct network read and accepts bounded, strict, checksum-pinned
  JSON over HTTPS. Local `discover` remains offline.
- Discovery data is descriptive only. URLs, code, commands, documentation, and
  package locations in a response remain data and are never loaded or run.
- The runner uses argument arrays, never a shell, and suppresses SDK stderr so
  an SDK failure cannot echo a credential.
- No operation here pushes, publishes, deploys, grants access, or approves an
  external effect. A separate explicit owner-approved workflow is required for
  any such action.

Return the runner's single JSON result exactly. A `status: "refused"` result is
a safety decision, not an invitation to bypass the lock.
