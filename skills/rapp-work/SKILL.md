---
name: "rapp-work"
description: "Safely verify, inspect, discover, scaffold, update, or migrate RAPP Work through the exact canonical SDK and RAPP/1 checkout. Use when someone wants the same plan-first RAPP Work workflow from Claude Code, GitHub Copilot CLI, or another Agent Skills host without copying protocol logic into the host."
license: "MIT"
compatibility: "Requires Python 3.11+, Git, and exact local checkouts pinned in agent.lock. Discovery optionally uses credential-free HTTPS. Nothing is cloned or installed automatically."
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
explicitly approves that exact plan. Apply only by repeating the command with:

```bash
python3 scripts/run.py <operation> ... --apply <exact-plan-digest>
```

The runner recomputes the current plan before apply and refuses a different,
shortened, uppercase, stale, or malformed digest. It also refuses traversal,
symlinks, overlapping migration roots, a non-empty scaffold or migration
destination, multiply linked or conflicting managed files, protected paths,
unexpected file actions, and any plan that requests network effects, push,
publication, or deployment. Approved file bytes are staged beside their target
and published atomically; an existing inode is never opened for writing or
truncated.

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
