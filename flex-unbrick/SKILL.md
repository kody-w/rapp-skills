---
name: "flex-unbrick"
description: "Unbrick an Azure Flex Consumption function app after a tenant security-policy sweep silently re-disables storage public network access (app 403/503s, PNA=Disabled). Runs the proven 2026-07-09 runbook — PNA check, SecurityControl=Ignore tag, re-enable PNA, full stop/start, bounded health poll."
allowed-tools: "Bash(az:*), Bash(curl:*), Bash(bash:*), Read"
---

# flex-unbrick — the storage-PNA outage runbook as one verb

Root cause: a management-group policy silently flips the function app's storage
account to `publicNetworkAccess: Disabled`, which kills Flex Consumption apps.
The fix sequence was re-derived by hand once (169 az calls, 573-minute session) —
this skill replays it.

## 1 — Diagnose (read-only, always first)

```
bash ~/.claude/skills/flex-unbrick/scripts/unbrick.sh check <app> <rg> <storage>
```

Prints subscription, storage PNA state, app state, live HTTPS probe, and a
verdict line: `HEALTHY` / `DEGRADED` (classic PNA outage — fix applies) /
`DOWN-OTHER-CAUSE` (probe failed but PNA already Enabled — fix will NOT help).
The live probe is the truth: PNA=Disabled with a healthy probe is the
private-endpoint deployment shape, NOT an outage. If HEALTHY, stop — do not fix.

## 2 — Fix (mutating; only on a DEGRADED verdict)

```
bash ~/.claude/skills/flex-unbrick/scripts/unbrick.sh fix <app> <rg> <storage>
```

Order matters and is encoded in the script:
1. `SecurityControl=Ignore` tag on the storage account (merge, keeps other tags) — without it the policy re-disables PNA again within hours.
2. `--public-network-access Enabled` on the storage account.
3. FULL `az functionapp stop` then `start` — `restart` does NOT re-bind Flex storage.
4. Bounded health poll (20 × 15 s). HTTP 401/404 counts as recovered — an auth layer may 404 without its client-id env var; the metal being up is what we're testing.

## 3 — Aftercare

- If you have alert rules wired on the app (health check, app-down, storage-config-change), check them: a storage-config-change alert firing timestamps the policy sweep.
- If the app is still down after the poll: the problem is NOT this policy — go read Function App logs instead of re-running fix.

## Don'ts

- Don't run `fix` without a `check` first, and never on a HEALTHY verdict.
- Don't substitute `az functionapp restart` for stop/start.
- Don't remove the `SecurityControl=Ignore` tag "to clean up" — it is the thing keeping the app alive.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "app": {
      "description": "Derived from `<app>` used in the documented command at line 11.",
      "type": "string"
    },
    "rg": {
      "description": "Derived from `<rg>` used in the documented command at line 11.",
      "type": "string"
    },
    "storage": {
      "description": "Derived from `<storage>` used in the documented command at line 11.",
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
az functionapp stop
az functionapp restart
bash ~/.claude/skills/flex-unbrick/scripts/unbrick.sh check <app> <rg> <storage>
bash ~/.claude/skills/flex-unbrick/scripts/unbrick.sh fix <app> <rg> <storage>
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
