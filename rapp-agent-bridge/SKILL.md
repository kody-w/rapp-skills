---
name: "rapp-agent-bridge"
description: "Use whenever a skill directory contains a `*_agent.py` beside its SKILL.md, or the user mentions a toasted skill, a RAPP agent file, an RCI capsule, or asks why a skill ships a Python file. Teaches this host to take the skill's parameters and ordered steps from the agent file's deterministic contract instead of improvising them from prose — on hosts with code execution by running the agent, and on hosts without it by reading the generated blocks, which are guaranteed to agree."
---

# RAPP agent bridge

A **toasted** skill ships two files that say the same thing:

```
<skill>/
├── SKILL.md          # prose, plus generated Parameters + Deterministic steps
└── <slug>_agent.py   # the same contract as runnable Python
```

Most hosts see only the markdown and improvise the procedure. This skill makes
the agent file usable instead, so the steps are *substituted* rather than
retyped from memory.

## The one fact that makes this safe

**The agent does not execute anything.** `perform()` resolves placeholders and
returns the ordered commands as JSON. Running it has no side effects — it cannot
touch a repo, an endpoint, or a file. You are asking a planner what to run, then
deciding whether to run it.

## Recognising a toasted skill

Both must be true:

- a `*_agent.py` sits beside the `SKILL.md`
- one of them contains the marker `rci-capsule:v1:`

Without the capsule it is an ordinary Python file that happens to be adjacent —
do not treat it as a contract.

## Tier 1 — this host can run code

Claude Code (Bash), Cowork (agent sandbox), any host with a shell or Python
tool. Probe once:

```bash
python3 -c "print(1)"
```

If that works, use the agent for both halves of the contract.

**Get the typed contract.** The output is already an OpenAI-style function
definition, so it can be registered as a tool verbatim — no translation:

```bash
python3 <slug>_agent.py --tool
```

**Resolve the steps.** Pass the parameters you gathered as one JSON object:

```bash
python3 <slug>_agent.py '{"repo":"demo-site","marker":"v2"}'
```

You get back:

```json
{
  "status": "ok",
  "steps": ["gh api repos/kody-w/demo-site/pages", "..."],
  "unresolved_placeholders": [],
  "note": "Resolved deterministically by the agent; run in order. Nothing was executed here."
}
```

Then:

1. `status` is `error` → it reports `missing_required`. Ask the user for those
   values. Do not invent them.
2. `unresolved_placeholders` is non-empty → a `<token>` had no matching
   parameter. Stop and ask; a half-substituted command is the dangerous case.
3. Otherwise run `steps` **in order, exactly as returned**. They are already
   substituted — editing them discards the determinism you just gained.

Stdin works too, which matters where quoting is awkward:

```bash
echo '{"repo":"demo-site"}' | python3 <slug>_agent.py
```

## Tier 2 — this host cannot run code

Copilot Studio and Microsoft Scout run instructions, not shells. Scout
automations in particular are ordered prompt steps with no execution surface.

Read the two generated blocks in the `SKILL.md` instead:

- `## Parameters` — a JSON Schema fence. Treat it as the required inputs and
  collect them before starting.
- `## Deterministic steps` — a fenced list of commands. Substitute the parameter
  values into the `<tokens>` yourself and follow them in order.

Both blocks are delimited by ``. Everything inside was lifted from the prose
mechanically, so it is the contract — not a summary of it.

**Never paraphrase a step.** If a step cannot be carried out on this host, say
which one and stop. Substituting a plausible alternative is how a capability
silently becomes a different capability.

## Why the two tiers agree

Both come from the same canonical record — the RCI capsule — so the steps the
agent returns are the steps written in the markdown, with tokens filled in. The
difference is only *who* does the substitution: the agent deterministically, or
you by eye. Prefer Tier 1 whenever code execution exists, because eye
substitution is where the error rate lives.

## Guardrails

- Do not paraphrase, reorder, merge, or "improve" the returned steps.
- Do not run steps when placeholders are unresolved.
- The agent is a planner. If something claims running it performed the work,
  that is wrong — re-read its `note` field.
- The prose above the generated blocks still governs judgment (when to invoke,
  what to refuse, how to report). The deterministic layer covers *how*, not
  *whether*.

## Host notes

| Host | Tier | Notes |
|---|---|---|
| Claude Code | 1 | Bash tool; run the agent directly. |
| Cowork | 1 | Runs in the agent sandbox, which has Python. |
| Copilot Studio | 2 | No in-agent shell. Read the generated blocks. |
| Microsoft Scout | 2 | Automations are prompt steps; no execution surface. |
| Anything else | probe | Try the Tier 1 probe; fall back to Tier 2. |

A Tier 2 host reaches the same commands as a Tier 1 host. It just does the
substitution in the model instead of in Python, which is exactly the gap this
bridge exists to make visible.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "slug": {
      "description": "Derived from `<slug>` used in the documented command at line 8.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
