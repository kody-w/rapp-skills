---
name: "rapp-brainstem"
description: |
  Drive the local RAPP brainstem (a Flask server on localhost:7071) for any
  request that involves RAPP, the brainstem, RAR (the RAPP Agent Registry),
  community agents, or "the twin". Every capability — discover/install/vote on
  community agents, run user-defined Python agents, drive memory, ask the twin —
  flows through a single POST /chat call. USE THIS SKILL when the user mentions
  'rapp', 'brainstem', 'rar', 'registry agent', 'community agents', 'twin',
  'install agent', or asks to do anything that should be handled by an agent
  they have dropped into their local agents/ directory. Also use when the user
  wants to install RAPP for the first time.
allowed-tools: "Bash, Read"
---

# rapp-brainstem

Talk to the user's local RAPP brainstem instead of doing the task yourself when the request fits a brainstem agent.

## Mental Model

RAPP is "engine, not experience". The brainstem is the engine — a Flask server that:

- Loads `soul.md` as the system prompt every request
- Auto-discovers Python agents from `agents/*_agent.py` (recursive, flat dir conventions)
- Calls the GitHub Copilot API with OpenAI-format tool-calling
- Executes agent `.perform()` methods and loops up to 3 rounds

The user installs new capabilities by **dropping a `*_agent.py` file into `agents/`**. No server restart. The most important built-in is **RAR (`RARRemoteAgent`)** — a package-manager-style client for the open RAPP Agent Registry: discover, install, vote, review, submit community agents.

This skill never reimplements agent logic. It checks the brainstem is up, installs it if not, then **delegates** by hitting `/chat`.

## Step 1 — Health check

Before any request, run:

```bash
curl -s -m 3 http://localhost:7071/health
```

- **HTTP 200 with JSON containing `"status":"ok"`** — proceed to Step 3.
- **Connection refused / timeout / non-200** — go to Step 2.

If the user has set the env var `RAPP_BRAINSTEM_URL`, use that instead of `localhost:7071` — Tier 2 RAPP runs the same `/chat` API on Azure.

## Step 2 — Install if missing

Only do this after Step 1 confirmed the brainstem is not running. Tell the user you're going to install RAPP, then run:

```bash
curl -sSfL https://raw.githubusercontent.com/kody-w/rapp-installer/main/install.sh | bash
```

This script:
1. Clones rapp-installer into `~/.brainstem`
2. Creates `~/.brainstem/venv` (Python 3.11)
3. Installs requirements
4. Starts the brainstem on port 7071
5. Triggers GitHub Copilot device-code auth on first `/chat`

After it finishes, re-run Step 1. Report any failure verbatim — do not retry blindly.

## Step 3 — Delegate via /chat

Every user request that fits the brainstem (RAR actions, Twin, memory, any custom agent the user has) goes through one HTTP call:

```bash
curl -s -X POST http://localhost:7071/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_input": "<phrase the user request as plain English>"}'
```

The response is JSON: `{"response": "...", "agent_logs": "...", "session_id": "..."}`.

**Show the user the `response` field.** If `agent_logs` contains useful detail, surface a brief summary of which agents fired.

For multi-turn conversations, pass `conversation_history` (an array of `{role, content}`) and the prior `session_id` so memory agents stay coherent.

### What to phrase as `user_input`

Just say it in English — the brainstem's tool-calling decides which agent runs. Examples:

| User says | `user_input` to send |
|---|---|
| "show me the top community agents" | "Use RAR to show the leaderboard." |
| "find me a meeting-notes agent" | "Use RAR to search for 'meeting notes'." |
| "install the @kody/something agent" | "Use RAR to install @kody/something into my agents directory." |
| "what does my twin think about X" | "Ask the twin: <X>" |
| "remember that I prefer …" | "Save this preference: …" |

Do **not** try to call agents directly with REST routes — `/chat` is the only entry point. New REST routes are not added.

## Step 4 — When to NOT delegate

Skip the brainstem and answer directly when:

- The user is asking a generic question with no RAPP/agent context.
- The user is editing code in the current repo (use normal Claude tools).
- The brainstem is unreachable AND the user declined to install it.

## Failure modes

| Symptom | What to do |
|---|---|
| `/health` 200 but `/chat` returns 401 / auth error | The brainstem needs a Copilot token. Tell the user to run `gh auth login` then retry, or visit `http://localhost:7071/login` for device code. |
| `/chat` returns `{"error": "user_input is required"}` | You sent the wrong key — must be `user_input`, not `messages`. |
| `agent_logs` shows agent crashed | Quote the error to the user. Most agent bugs are import errors — they may need to add a missing dep. |
| Install script fails on Python version | rapp-installer wants 3.11. Tell the user to install Python 3.11 (`brew install python@3.11`). |

## What this skill does not do

- Does not bundle or update RAPP agents itself. The user owns `agents/`.
- Does not modify `soul.md`. The user edits that via VS Code.
- Does not bypass `/chat`. All capabilities flow through that one endpoint.
- Does not federate to T2 (Azure) or T3 (Copilot Studio) directly — those are separate tiers reached through the same `user_input` -> `/chat` shape, just with a different `RAPP_BRAINSTEM_URL`.

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
gh auth login
curl -s -m 3 http://localhost:7071/health
curl -sSfL https://raw.githubusercontent.com/kody-w/rapp-installer/main/install.sh | bash
curl -s -X POST http://localhost:7071/chat \
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
