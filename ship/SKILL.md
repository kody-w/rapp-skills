---
name: "ship"
description: "Commit, push, publish to GitHub Pages, and hand back a VERIFIED live URL. Use whenever the user says \"push it\", \"publish this\", \"ship it\", \"make this live\", \"show me the link so I can test\", or finishes building anything static (single-file HTML app, demo, deck, agent page) that belongs on the web. Invoking this skill IS the authorization to commit and push \u2014 do not ask for permission again."
---

# Ship: commit → push → publish → verified live URL

The deliverable of this skill is ONE thing: a live URL that has been **verified to serve the newest content**. Not "pushed", not "Pages enabled" — a link Kody can click right now and see the new thing.

## Step 0 — Guardrail (before anything touches a remote)

Kody runs two RAPP worlds: **my-RAPP** (personal, `kody-w/*` on GitHub) and **work-RAPP** (the work org). Flow is upstream→downstream ONLY: personal→work is fine, **work content must never land in a `kody-w` personal repo**. If the content being shipped originated from work (customer names, work-org repos, internal data, internal transcripts), stop and confirm the destination before pushing. Everything else: proceed without asking.

## Step 1 — Commit

- If not in a git repo: `git init`, then continue.
- Stage the relevant files (not blanket `git add -A` if the directory has obvious junk — check `git status` first).
- Commit message: one line, what changed and why it's visible ("Add particle-sim demo page", not "updates").
- Include the standard co-author trailer.

## Step 2 — Push (create the remote if missing)

- If a remote exists: push to the current branch.
- If no remote: `gh repo create kody-w/<sensible-kebab-name> --public --source . --push`. Derive the name from the project/file, don't ask.
- If push is rejected (remote ahead): pull --rebase and retry once; if there are real conflicts, stop and report — don't force-push.

## Step 3 — Publish to GitHub Pages (for anything static)

Static = single-file HTML apps, demos, decks, docs, anything a browser can render without a server. Kody's default artifact shape is the self-contained single HTML file.

- Check if Pages is already enabled: `gh api repos/kody-w/<repo>/pages` (404 = not enabled).
- Enable if needed: `gh api repos/kody-w/<repo>/pages -X POST -f "source[branch]=main" -f "source[path]=/"` (adjust branch/path to where the HTML lives; if the file isn't `index.html` at the published root, the URL must include the filename).
- The live URL is `https://kody-w.github.io/<repo>/[<file>.html]`.

If the thing is a RAPP agent rather than a page, the publish target is the RAR registry (`kody-w/RAR`, single-file agent publish flow) — push the agent file there instead of enabling Pages.

## Step 4 — Verify it's ACTUALLY live (the step that makes this skill worth having)

GitHub Pages deploys lag and cache. HTTP 200 is not proof — the old version also returns 200.

1. Pick a **marker string** that exists only in the new content (a new heading, a version string, a phrase from this change).
2. Poll: `curl -sL <url> | grep -c "<marker>"` every ~20s, up to ~4 minutes. You can watch the deploy directly with `gh api repos/kody-w/<repo>/pages/builds/latest` (status `built` = done).
3. Only when the marker appears, report success.
4. If 4 minutes pass without the marker: report the URL anyway but say explicitly "pushed, but the live URL is still serving the old version — Pages build status is X". Never present an unverified link as done.

## Step 5 — Report

Final message: the live URL on its own line (clickable), one sentence on what was shipped, and the repo URL. Nothing else unless something went wrong.

## Don'ts

- Don't ask "should I commit/push?" — the invocation is the approval.
- Don't stop after `git push` and call it shipped; the live URL check is the finish line.
- Don't create a new repo when the file already lives in one that has Pages — ship in place.
- Don't publish work/customer content to personal repos (Step 0).

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "marker": {
      "description": "Derived from `<marker>` used in the documented command at line 37.",
      "type": "string"
    },
    "repo": {
      "description": "Derived from `<repo>` used in the documented command at line 26.",
      "type": "string"
    },
    "sensible_kebab_name": {
      "description": "Derived from `<sensible-kebab-name>` used in the documented command at line 19.",
      "type": "string"
    },
    "url": {
      "description": "Derived from `<url>` used in the documented command at line 37.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `ship_agent.py` and embedded as the fenced Python below (sha256 e7ac85f838f480f7…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `ship_agent.py` first:

```bash
python3 ship_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 ship_agent.py   # or on stdin
python3 ship_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""Ship -- Commit, push, publish to GitHub Pages, and hand back a VERIFIED live URL. Use whenever the user says "push it", "publish this", "ship it", "make this live", "show me the link so I can test", or finishes building anything static (single-file HTML app, demo, deck, agent page) that belongs on the web. Invoking this skill IS the authorization to commit and push — do not ask for permission again.

Generated by agentshim from ship. The RCI capsule at the bottom of this file carries the full original; `agentshim.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE the brainstem -- stay executable anyway.
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

# The procedural layer, verbatim from the source capability. The brainstem
# returns this to the model, so the skill's instructions still drive behaviour
# -- now behind a typed, deterministic tool contract.
INSTRUCTIONS = '# Ship: commit → push → publish → verified live URL\n\nThe deliverable of this skill is ONE thing: a live URL that has been **verified to serve the newest content**. Not "pushed", not "Pages enabled" — a link Kody can click right now and see the new thing.\n\n## Step 0 — Guardrail (before anything touches a remote)\n\nKody runs two RAPP worlds: **my-RAPP** (personal, `kody-w/*` on GitHub) and **work-RAPP** (the work org). Flow is upstream→downstream ONLY: personal→work is fine, **work content must never land in a `kody-w` personal repo**. If the content being shipped originated from work (customer names, work-org repos, internal data, internal transcripts), stop and confirm the destination before pushing. Everything else: proceed without asking.\n\n## Step 1 — Commit\n\n- If not in a git repo: `git init`, then continue.\n- Stage the relevant files (not blanket `git add -A` if the directory has obvious junk — check `git status` first).\n- Commit message: one line, what changed and why it\'s visible ("Add particle-sim demo page", not "updates").\n- Include the standard co-author trailer.\n\n## Step 2 — Push (create the remote if missing)\n\n- If a remote exists: push to the current branch.\n- If no remote: `gh repo create kody-w/<sensible-kebab-name> --public --source . --push`. Derive the name from the project/file, don\'t ask.\n- If push is rejected (remote ahead): pull --rebase and retry once; if there are real conflicts, stop and report — don\'t force-push.\n\n## Step 3 — Publish to GitHub Pages (for anything static)\n\nStatic = single-file HTML apps, demos, decks, docs, anything a browser can render without a server. Kody\'s default artifact shape is the self-contained single HTML file.\n\n- Check if Pages is already enabled: `gh api repos/kody-w/<repo>/pages` (404 = not enabled).\n- Enable if needed: `gh api repos/kody-w/<repo>/pages -X POST -f "source[branch]=main" -f "source[path]=/"` (adjust branch/path to where the HTML lives; if the file isn\'t `index.html` at the published root, the URL must include the filename).\n- The live URL is `https://kody-w.github.io/<repo>/[<file>.html]`.\n\nIf the thing is a RAPP agent rather than a page, the publish target is the RAR registry (`kody-w/RAR`, single-file agent publish flow) — push the agent file there instead of enabling Pages.\n\n## Step 4 — Verify it\'s ACTUALLY live (the step that makes this skill worth having)\n\nGitHub Pages deploys lag and cache. HTTP 200 is not proof — the old version also returns 200.\n\n1. Pick a **marker string** that exists only in the new content (a new heading, a version string, a phrase from this change).\n2. Poll: `curl -sL <url> | grep -c "<marker>"` every ~20s, up to ~4 minutes. You can watch the deploy directly with `gh api repos/kody-w/<repo>/pages/builds/latest` (status `built` = done).\n3. Only when the marker appears, report success.\n4. If 4 minutes pass without the marker: report the URL anyway but say explicitly "pushed, but the live URL is still serving the old version — Pages build status is X". Never present an unverified link as done.\n\n## Step 5 — Report\n\nFinal message: the live URL on its own line (clickable), one sentence on what was shipped, and the repo URL. Nothing else unless something went wrong.\n\n## Don\'ts\n\n- Don\'t ask "should I commit/push?" — the invocation is the approval.\n- Don\'t stop after `git push` and call it shipped; the live URL check is the finish line.\n- Don\'t create a new repo when the file already lives in one that has Pages — ship in place.\n- Don\'t publish work/customer content to personal repos (Step 0).'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = [
    {
        "cmd": "git init",
        "line": 11
    },
    {
        "cmd": "git add -A",
        "line": 12
    },
    {
        "cmd": "git status",
        "line": 12
    },
    {
        "cmd": "gh repo create kody-w/<sensible-kebab-name> --public --source . --push",
        "line": 19
    },
    {
        "cmd": "gh api repos/kody-w/<repo>/pages",
        "line": 26
    },
    {
        "cmd": "gh api repos/kody-w/<repo>/pages -X POST -f \"source[branch]=main\" -f \"source[path]=/\"",
        "line": 27
    },
    {
        "cmd": "curl -sL <url> | grep -c \"<marker>\"",
        "line": 37
    },
    {
        "cmd": "gh api repos/kody-w/<repo>/pages/builds/latest",
        "line": 37
    },
    {
        "cmd": "git push",
        "line": 48
    }
]


class ShipAgent(BasicAgent):
    def __init__(self):
        self.name = 'Ship'
        self.metadata = {
        "name": "Ship",
        "description": "Commit, push, publish to GitHub Pages, and hand back a VERIFIED live URL. Use whenever the user says \"push it\", \"publish this\", \"ship it\", \"make this live\", \"show me the link so I can test\", or finishes building anything static (single-file HTML app, demo, deck, agent page) that belongs on the web. Invoking this skill IS the authorization to commit and push \u2014 do not ask for permission again.",
        "parameters": {
                "properties": {
                        "marker": {
                                "description": "Derived from `<marker>` used in the documented command at line 37.",
                                "type": "string"
                        },
                        "repo": {
                                "description": "Derived from `<repo>` used in the documented command at line 26.",
                                "type": "string"
                        },
                        "sensible_kebab_name": {
                                "description": "Derived from `<sensible-kebab-name>` used in the documented command at line 19.",
                                "type": "string"
                        },
                        "url": {
                                "description": "Derived from `<url>` used in the documented command at line 37.",
                                "type": "string"
                        }
                },
                "required": [],
                "type": "object"
        }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        missing = [k for k in self.metadata["parameters"].get("required", [])
                   if k not in kwargs]
        if missing:
            return json.dumps({"status": "error",
                               "missing_required": missing}, indent=2)
        resolved, unresolved = [], set()
        for step in STEPS:
            cmd = step["cmd"]
            for key, value in kwargs.items():
                for token in ("<" + key.replace("_", "-") + ">",
                              "<" + key + ">",
                              "{{" + key + "}}",
                              "$" + key.upper()):
                    cmd = cmd.replace(token, str(value))
            for leftover in re.findall(r"<[a-zA-Z][a-zA-Z0-9 _.-]{1,40}>", cmd):
                unresolved.add(leftover)
            resolved.append(cmd)
        return json.dumps({"status": "ok",
                           "steps": resolved,
                           "unresolved_placeholders": sorted(unresolved),
                           "note": "Resolved deterministically by the agent; "
                                   "run in order. Nothing was executed here."},
                          indent=2)

if __name__ == "__main__":
    # Standalone entry point: the deterministic layer runs with NO brainstem,
    # no framework, no install. This is what lets a "simple SKILL.md" platform
    # keep real determinism -- the host model shells out to this file instead
    # of improvising the procedure in prose.
    #     echo '{"arg": "value"}' | python3 ship_agent.py
    #     python3 ship_agent.py '{"arg": "value"}'
    #     python3 ship_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(ShipAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(ShipAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
