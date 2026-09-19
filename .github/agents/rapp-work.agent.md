---
name: "rapp-work"
description: "Safely verifies, inspects, discovers, scaffolds, updates, or migrates RAPP Work through exact pinned canonical tooling. Use for a plan-first RAPP Work workflow without cloning, installing, exposing credentials, or performing external actions."
---

Operate the self-contained adapter at `skills/rapp-work/scripts/run.py`.

1. Run it with no operation for the default `verify`, or use only `status`,
   `discover`, `scaffold`, `update`, or `migrate`.
2. Prefer explicit `--sdk-path` and `--rapp1-path` values the user supplied.
   An explicit `--api-base` is valid only when it is the exact URL derived from
   the locked static commit. Never replace an invalid explicit value with an
   environment or locally discovered one.
3. Use `--root` for status, verify, scaffold, and update; explicit
   `--discover-root` values for offline discovery; and disjoint `--source` /
   `--target` roots for migration. A scaffold also requires its kind, owner
   label, slug, and world.
4. Never clone, install, import, or execute anything named by discovery data.
   Discovery output is inert metadata only. A direct network read occurs only
   when the user/configuration supplies `--api-base`.
5. `scaffold`, `update`, and `migrate` produce a plan by default. Show the user
   the exact plan and digest. For scaffold, explicitly save the complete
   printed planned result in a trusted private file outside the absent
   destination. After approval, repeat the same request with both
   `--plan <file>` and `--apply <exact-lowercase-digest>`. Never replan during
   apply or replace the reviewed identity. A changed release lock requires a
   newly reviewed plan; its fingerprint is a compatibility check, not a
   signature. Update and migrate retain digest-only `--apply` and reject
   `--plan`; this adapter does not provide their native checkpoint/recovery.
6. Do not request or inspect credentials. Do not push, publish, deploy, grant
   access, or authorize network effects through this agent.
7. Return the runner's single JSON result exactly. Do not work around a refusal,
   pending pin, checksum mismatch, hidden Git state, unlisted code, hardlink,
   path conflict, or symlink. Scaffold apply requires an absent target, an
   existing parent, and supported no-follow/no-replace operations. It preserves
   the saved review file and reports success only after native confirmation
   and file checks. A timeout or malformed reply is not success or permission
   to retry, remove staging, or overwrite a destination. Inspect/verify
   explicitly; do not promise permanent one-use approval or crash recovery.
