---
name: "rapp-copilot-in-chrome"
description: "Drive the user's real, logged-in Chrome browser from GitHub Copilot CLI — navigate, click, type, screenshot, read the accessibility tree or page text, run JavaScript, and inspect console and network traffic. Use when the user asks to open or browse a site, click through a web UI, fill a form, scrape or read a page, debug a web app in the browser, take a screenshot of a page, or automate anything in Chrome. Also use for \"rapp copilot in chrome\", \"browser automation\", \"drive chrome\", \"open a tab\", \"check the console\", or to install, verify, or diagnose the bridge itself."
license: "MIT"
---

# rapp-copilot-in-chrome

Browser automation against the browser you **actually use** — real profile, live cookies,
authenticated sessions. Not a throwaway headless instance.

## Architecture

```
Copilot CLI (MCP client)
  -> ~/.copilot/bin/rapp-copilot-in-chrome        (launcher shim)
  -> claude --claude-in-chrome-mcp                (self-contained stdio MCP server)
  -> native host com.anthropic.claude_code_browser_extension
  -> Chrome extension fcoeoabgfenejglbffodgkkbkcdhcgfn
  -> live tabs
```

The MCP server is self-contained: it does **not** require a Claude Code session to be running. It
needs only the Claude binary (which hosts the bridge) plus the Chrome extension installed and
connected. That is the whole trick — the bridge was always a plain stdio MCP server, so any MCP
client can drive it.

## Run this — do not improvise

Setup and health checks have a **deterministic implementation** shipped next to this file as
`rapp_copilot_in_chrome_agent.py`. It is stdlib-only Python with no install step. When asked to
install, verify, or diagnose the bridge, execute it and use its output verbatim — do not guess at
the state of the system:

```bash
python3 rapp_copilot_in_chrome_agent.py '{"action": "<action>"}'   # doctor | status | install | uninstall
python3 rapp_copilot_in_chrome_agent.py '{"action": "doctor"}'     # full check + live Chrome round trip
python3 rapp_copilot_in_chrome_agent.py '{"action": "status"}'     # fast check, no browser traffic
python3 rapp_copilot_in_chrome_agent.py '{"action": "install"}'    # launcher + MCP registration + skill
python3 rapp_copilot_in_chrome_agent.py --tool                     # emit the JSON tool contract
```

`doctor` verifies all seven links in the chain — Claude binary, native-host manifest, Chrome
extension, launcher, MCP registration, MCP handshake, and a live round trip that reaches a real tab.

## Loading the tools (do this first)

The 22 browser tools arrive **deferred** in Copilot CLI. Load them with a single tool-search call,
batching every tool you expect to need — each extra search costs a round trip:

```
tool_search_tool  pattern: "rapp-copilot-in-chrome"
```

Or target a subset: `"tabs_context_mcp|browser_batch|navigate|read_page|computer"`.

## The two rules that matter

1. **Always call `tabs_context_mcp` with `createIfEmpty: true` first.** Nearly every other tool
   requires a `tabId`, and tabs only exist inside this session's tab group. Skip it and you get
   `No tab available`.
2. **Prefer `browser_batch` over single calls.** It runs a whole sequence in ONE round trip,
   executing sequentially and stopping on the first error. Batch whenever you can predict two or
   more steps ahead.

```jsonc
// 1. get a tabId
tabs_context_mcp { "createIfEmpty": true }
// -> {"availableTabs":[{"tabId":1363872857,...}],"tabGroupId":249531617}

// 2. batch the rest
browser_batch {
  "actions": [
    { "name": "navigate",      "input": { "url": "https://example.com", "tabId": 1363872857 } },
    { "name": "get_page_text", "input": { "tabId": 1363872857 } }
  ]
}
```

## Tools (22)

**Tabs** — `tabs_context_mcp` (list/create group), `tabs_create_mcp`, `tabs_close_mcp`

**Navigation** — `navigate` (url, or back/forward), `resize_window`

**Reading** — `get_page_text` (article text; best for reading), `read_page` (accessibility tree with
`ref_id`s; supports `filter: interactive`, `depth`, `max_chars`), `find` (natural-language element
lookup returning refs)

**Interaction** — `computer` (screenshot, click, type, key, scroll, drag by coordinate),
`form_input` (set a value by `ref`), `file_upload` (by `ref` — never click a file input, it opens a
native dialog you cannot see), `upload_image`

**Scripting** — `javascript_tool` (REPL semantics in page context: top-level `await` works and the
last expression is returned — do not write `return`)

**Debugging** — `read_console_messages` (`pattern` filter), `read_network_requests` (`urlPattern`
filter)

**Orchestration** — `browser_batch`

**Recording** — `gif_creator` (start/stop/export an animated GIF of the session)

**Shortcuts** — `shortcuts_list`, `shortcuts_execute`

**Browser selection** — `list_connected_browsers`, `select_browser` (by deviceId), `switch_browser`
(broadcast a pairing request, wait for the user to click Connect)

> **Network tracking is lazy.** `read_network_requests` only begins recording the first time it is
> called on a tab, so a page that already loaded shows nothing. Call it once *before* navigating or
> triggering the requests you want, then call it again to read them. Requests also clear when the
> tab navigates to a different domain.

## Choosing a reading tool

- Reading an article, docs page, or any prose -> `get_page_text`
- Need to click or fill something -> `find` (natural language) or `read_page` with
  `filter: "interactive"` to get `ref`s
- Need pixel coordinates, or the page is canvas/visual -> `computer` screenshot first
- `read_page` truncates at 50k chars; narrow with `ref_id` or `depth` rather than raising
  `max_chars` blindly

## Safety

This drives the user's **actual** browser with their **real** authenticated sessions. Anything it
clicks, submits, purchases, sends, or deletes happens as the user. Confirm before any destructive or
irreversible action — sending messages, submitting payments, deleting data, changing account
settings. Prefer opening a fresh tab per task rather than reusing tabs the user is actively working
in.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `No tab available` | Call `tabs_context_mcp { createIfEmpty: true }` first, then pass `tabId`. |
| `Cannot access a chrome:// URL` | New tabs start on `chrome://newtab`; navigate somewhere real first. |
| `read_network_requests` empty | Tracking starts on first call — call it, then navigate/act, then read. |
| Tools not listed | They are deferred — run the tool search above. |
| Server missing | `copilot mcp get rapp-copilot-in-chrome` should report `Status: Enabled`. |
| Cannot locate `claude` | Set `RAPP_CHROME_CLAUDE_BIN` to its absolute path. |
| Browser not responding | Extension may be disconnected — `list_connected_browsers`, then `select_browser` or `switch_browser`. |

Run `python3 rapp_copilot_in_chrome_agent.py '{"action": "doctor"}'` before debugging by hand — it
names the exact broken link in the chain.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "description": "Derived from `<action>` used in the documented command at line 30."
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
python3 rapp_copilot_in_chrome_agent.py '{"action": "doctor"}'
python3 rapp_copilot_in_chrome_agent.py '{"action": "<action>"}'   # doctor | status | install | uninstall
python3 rapp_copilot_in_chrome_agent.py '{"action": "doctor"}'     # full check + live Chrome round trip
python3 rapp_copilot_in_chrome_agent.py '{"action": "status"}'     # fast check, no browser traffic
python3 rapp_copilot_in_chrome_agent.py '{"action": "install"}'    # launcher + MCP registration + skill
python3 rapp_copilot_in_chrome_agent.py --tool                     # emit the JSON tool contract
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
