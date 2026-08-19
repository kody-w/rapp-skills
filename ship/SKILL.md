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

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `ship_agent.py` and embedded as the fenced Python below (sha256 3b7a9c8cce079f22…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `ship_agent.py` first:

```bash
python3 ship_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 ship_agent.py   # or on stdin
python3 ship_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""Ship -- Commit, push, publish to GitHub Pages, and hand back a VERIFIED live URL. Use whenever the user says "push it", "publish this", "ship it", "make this live", "show me the link so I can test", or finishes building anything static (single-file HTML app, demo, deck, agent page) that belongs on the web. Invoking this skill IS the authorization to commit and push — do not ask for permission again.

Generated by the rapp skill from ship. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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

# rci-capsule:v1:H4sIAAAAAAAC/616a7ejyHLlX9E6/uDupqoEiGfZ17MkQIBAQgIhIbnvcvF+v994rn/7JOicqmqvtn3XzNSHU0JJZkZG7NixA/Tvb2bbBHn19jVrk+TTm+NWYWc2YZ69ff3Xf3+Lw8x5+/pmZn7ivn16S8LMffuK0J/eCrMyUzBSu1kdWon7b7Frmda/ZWY639fksQsWePvnj+HPy/Dnefhf3v726b9YGCV+LFy5Rf7zSvP1fzN1Q/6Y2lbJzzPB5d85MTWr2K1+nvv6Bkz/6+ya2q7C4uWbNyZP07D5tCraOpj/WklYB6smX/FhI7TW6mz6bv1pZWbOKpj/WKYdr8zVjVPFvcixqyTs3JWuyl9Weu2u+sDN3M6tVk3grtoafKjNsV79/jYvvwqb398+LRfvuwRh/fqmDsLi+3Bqxu4ytiz+cUPer1J3WRccOF7V+Upc2Wa2atx6mZdXKy/MwLJuvbLaMHHCzAdmj2Ah8KFuABjs1S91OHvtsxcm7kq4HuWVWRSfVo6b5vNfOwYn9d2sWRXgv1/Bbmazstwkz/x6lWfL7r1rfVmJWZfH87qLmXUcJslK1JbxFw7DaQHf7Eh78fDiwcULv7cojGArJ19lOfi6jlcesL1wqzSs63mO6Zth9gWEzx3MtEjcGkAYxC3IU3c26wPiIRh7+/rvbwkAAghkAU4KIvrprW7col5Qb6czTnywOXBM8wP3yIyiH4Om46w+b38Mo38cnl3X1n8+HKxmPK/syjUbdxXnzvi5X/9ptqw+f17CboMPdd5Wtrv6snxXBz8l5B+WNotwWb5efyy8JM96dkL9U7L9/ZNWn43VWdGuq8/ejKnFjH+1KjOzg7/+JQVe//3tD0OF2YCB9e9vP3Yjf+xmg4xcfa7l1ZKaq/+98sFWq882mP+RcD/N3JB/v53rBcD1OjFndP/5EiAyf3AeRv3tr38DqMjqpmrtGXwABG//sNJAan39ACHAHkKj33H4+vxKxvdLkLyhF7rO98T+Pfs9uwJcO+78TWWCuK5y72fggw/KiVstifYVcMPHzFf6BCbIR9fNVr/99n1tkBWAG7pXOmduDw4JLMwakHm//fZldQJ58aIM15lTO1uuFyZaudlsAfj6I4/MFx9IwIsLH9gAY/GqCv2gARP7Je9q9/tWLzO/zKf6B+AckCsr+GMpvjUrpzLDZPWL5YKkdH/wR5O39swsJghamjfur/MCy55Vm9Wrps9X6vZ8XvV5BQL3FRw2HT/P3/z22+oXkNt1npnJp9W392D/9m2mkxfF/rqY+NtvYGr8fcrCNOALQGv+r19W+wScBPi5LUB0XTN9BcvJ++x1DQIgP76uPjZ6DS/zwSRAi+6n9w0+3LxKW+DzF1cn8/4h4J0P8759X2iB6BwS0Vsc+DHbchdSBdAqQDgB3flhBrDqrLwqT1+G/2KDHQBlVas5/0EJWc4HjvOC/SewY+NW8x6O2Zg/XTYgH18Vqv71E2CfvFgcBLb2wipdzAAlrJk3nNnyPVIzWubArjhwpPeguUntAqdUue0C0/oQEGS7MO5/RgDygYBXNZyHPs9HnoG3OGbOttnsr6tvH3T67dNsSra4JMxa98s8R2sASBcTKzdxOxO4ai419eqXeSkLeDp2m9caL9b9tgpfnnXCyrWbvBqXhMmtLszbehW1ANrvtgH8AWB/+0HJ38DaVd38uuz8shyUyLoGJnwF8FoKJQh8P2ehDYq3D5wwe7IPRlBr/7FedeFC06tffn/bAmuAfAA1EtB2HaZLSVyq4I8EbAtn5qPf3147ipmdtM7rtMCgzAHJA7zx+VUA5zCCk1d/8DP6cZbzTEC/vJeNl7vmrJqdsVTBzP/1exA+Um7lDmHdgNxa2AtQyALItqoWQC4k/uV73N7nzPH6/1Kjvn1ZsbOkfOcRcPcL6vMVAFgEYreeIw1URJ794wKyD2Ne0qcGVsx3gRj88n4eM3BN59f5PIBEP3+ugCG1u0SochsAhDyz3X96x8fMRdXsJpAgcyYAI5v6p+yYj1g1P7TFbAPIC9tdrP9DEDY/gvCnYm/1y6xH/pNyWsKhvUTUX1Z/pqLql4yqXzpq/i+3F+H4vo4JYpT3syScWRoEDUj0Hzn5qgfVl4XHATQd1zPbBAwASHqmDSAfmIU7u3GBm5t4n+fEAyUbOPRlzsuS2aYvL+wwS8IA/72OBeaaCXAg4Oz3IvJCx39bib+tfsFgDBx5ToH3aS/4c8vFvHwG2OXvWuz/Wn4AK0wnmhn7dfd6Hpnj1i/ImF2yHH6uvPUHZBZXgFPPUPgGWgZ3+BI0afJtBehgge0r/MB/VZ43C5stVXupDOFPyT2vMyP+de7rosDfKzzw6begaYr66/r9wF8APwWt9SXMP47+r/88L/Avy+Z//bbE5r2avIAxx+VVPF/SuzJnvM/iYWbe2XGffrZ31ZiVD0j0HQrqVgUO9wEzgIz55aO+gm8BP/8M03dZ/76GB+rprx958OKT4OOe5fZXys1iCgBm1jtL7GdzFzD9IaGwj4Vus75559Ytc9W3svx4+eqXF0mCmxdNNHc49c8SCtRGENDA7D6Y7w8J6bhFkoM2KjH9Vyk0QS34AkJ+Pa9QGJ5dMcMT8BAw9N2WecM8cWY992oqknomxaatgFwBk5YTIF9W53Dp54BeWRQrMLICNgAJshj6olzARMk4F8IPDfUhA34xl8uZx8AkkOzft3stM39TBNVMa+9sCUx9laIZTCjYPk8SkDl/l5T+tprlyrj6DxQGxNIWcwL8BwYKRtaCsvRl9cjbhVt6s7GDd50wO+69toIjzHTzP6fpH9U3yL1XuV19m78H13+Z+XU5wObLSpldM7e9y4bvTgR06JoVMPKdluvWtkFhBjOwRUp9NxrAu66/s+CPFb5+zPxISkCjvTmCxraZO2oQlwJUgHA+04dQ/rQMNv8pO4FOAvCayfXVrf4RFB+FYEHZcup3aTFPNX5/A1J8UYhF5dZzvIFz2+ynDgGIEyBWZm/8ISHwj4XV5RDz0D6cpd13dfIHM4Eh4QyyPlsUC9AFs4Sf2RXov1nHzHu7oBjOdy5qpge7vovP16OJl4QAVX55EgH6h+/6DxgM9Be4HUjR17f9fJK+yn9oQHYul/WraLAf5fv10KEFLhHfu6f17Oj/9aPzmDcNsy63X0L0nZBA7Ku8M5MvP1Z7VWkP6NuXfFsExXsmz/1T83GYf/qjY16K733d18ONxUM/Lf2ual55uHjgOxZftPde8ZbKMKfw7M/vfdkr8O/HeT2DyVZFYto/b/HBmbN+X38X9R8UAHLwD80CkA+vpurXL0tragOd9f2RxfJY7evb3JK+vT+ucoFX6vkxBvAaWKgJ3eXq/REW+PTHx1UvEfbeZ3z74IZv87Mm54OhgPBo0xkyzhK42c/gvAu0NuRsVTMWsxkvjnoDTfPykO5/2mthiL97J5T4053+7Dnj/7Txn0nVv9sOhP5TO+Zni//TvjMV/795dnFt2QL6dV7PsN7Hc2uWwrMdAGwNkJspMGa+mnkG6EBntm2pjPMHi8DAHAGrxe3rH7Mmbw/UkCtUuNE4YvtjfkJkguL8cLfTFbLdcyEj9uF2y3vW887x4YF7MJqK4lrsxcfcgOJ2ZGGmdCxAzFGj0MwuULqufrgogtCCPMJ1pQtTxBqNZDEOAaQon9c3JWGLYHtc87lLkcTVrsdAtNa3B30g+eF0VNNrVJ1v3KDLzBkPwnQXNVmeEEUul0/fRZ7mdefVu7Nib447FPSpEqmKrIT20VEQoyGRrV4WOTmQkqvMeudRmNLDGVq3ieUZZ28wTA33s5FUFKQiA35tYui6832ZZb1SQYhruwu1h98cOfhQn1SRyG5BdEiULW+edvvjNNCK02+ljTZtuT2cloVI8GfN6bEh7or2+ESFkcSjbRJWeNC2vEDIXnoptTtnqo+dAEE9j0thmfL7/nn389uuM5qglNYPsQ7YPZ02G32wh7XSB7dxfSNlnU2VTE8YRtckRKlPyK6t67VieOu+u17GXsRuWfgIH5gQpAM5Xg73cvcIA4U6Vzc358fGo56xdpysnlK9dXtck6NVhqN5IHb5SBahkhu0ntOG6Yct4bt4pD5u/mWtTNVmG1DMcMehx2nskgcCq7WE75i+D/sKodYyd/T1I0GV+s7fH3aIzTSieEu8jsTDM6de93R2ydVH3pS2qTx9NVc2SDEVdQHQLjVXuc1ME+8Z81G7o44EV4RNpEikaL6jXfECXcKTJtYc3jyfj6JWsSrKbbrszXhah/jEpw/z4m+Z4Mlqt3OkEc3NGp7Z5SEl6iM4REwQqmpAup3IY16WMJtqpLUOZdmb2Mfs0KVCJ4cDLnlMRxJRelVpqjQ2JBTc721Ay2YUbbcU49Kufks3+WWbXtAQF+FTcPGkUhFUh7UvMoHDQ4eiW8NFtC6wYaahXKSFir02HSm/g+HKvQfZDmcHW5novi84/qHn60s7TU0SNfdKT7dere63xEU6JzsulxL0YUP5Rp6GqubOhS/gHOsIvsNfVA3FVHIHT3tzSzva83Zu0LTebdHdYQ9Blxu015+wiZ4K+FHR6HbwU1Wtw/OJqgKJ2Zl5OnAnib6LprFlmr1t+k9sXwWXEx07Ok0ZGy2Us4rVic2dwfIbZnZKuL05vjfQPU2qB09dQx12glRWbw2GmYRwfzBE6S4NTthvzuPuJnJ3absTGj5JrmLNt3F0SfYIyRl4gExpPpXXdMhNNTScm8KZLcHdHwfnGG8Hyq+2O59p96PEj88DSOk+I1QXNqHjWO9NrT8/u61kginsY+fmI+tFul/vVNovyd25Iq8PObm2ku9kCPSoGVUT013zYDqudjvNrNJCd9mnyutDHLpEDd9995m4wTFud3IOM8rFx10+SgAwFBbTkZJ0LtswL04ZqzLmOZA4yDf3xnTSHgKK4+tJ1YtgsHFRb0snFUtmz2fBUzh52+1ml9NtG2mdnZRsgRqaV3eAEvsNLkYSo9CUjty4G325sRRjNHhpJScfq+OJl0/9nqyeWEavwcb+YevKW9U7YQHvYEzE4BdJxfS97EPshlYfbddp04HiMm7rXRzTI2kO5JiQG8gWvoh1J08CFqsBcr2LUWBJgn+3KDrH+IG9DFrAw1tbJKGDn2abfKuqoJ/FDgLUn+GTeUbX+3M4Gl24hsp4eJLq+RztUVHUxuOGggKBNPtjbWrPB5z3Pc14OlEkdEMctoYtMtf7iWuTbS5oGJi+CWgvRIr0vs154qG11o4B+VTew621bw/sQaP4pOWfJOFvcnHY3ZN6w8fU5UrQYqUdCYLYZqwe9Hq194nLjqWh7HI5igBzQOdzns3tNmeIEzF6J04korD9gddlqisxQUEaT3R9BqbMpn5otHDdXWPZe4a+H5aidyd3ZbKGTrygHDAA6VDf78joCjHbPKEu7NX1sNbfS4mjbnshyXPMjGwy9p9bYjdse6kjyO0mhTqnLEgSiWCFQrRDW14gOTxyQ1WUlWDFm81U2nc1e1y6tr00pJG3Op2Piklm5lOlcst7bOA9VHET7egHARHWpO/C69IhyAmiLvCmpQh+tyUK4dj7VqUeK+bU5DRzklQ1I+kmecr7W8hA0cD6zCHW2Os+226dozc9EIvRR9adIIYiiJBk1VOK4bYJbZEGFakzkULWJjv4t+1BivdawWA4VakCXBoJ0TxgWg9vmyG98uiwYUFznF4o6rSmeKN5HnZ6JOOyMPhjzN0s7dalCkoijXIat82uMkoJefTwzo3ovVlSexDkAjtq/nErqtujK0bexSj5TFxnN5O1u8tTM54Rn7M3f+cBxZAqkR4GGRcEEqnt+Ox47xWoFNCa31/zXdqpzLnJjd6N18OzvFOqZnMhoaTnSc0ngkviAQsnMu5FIwLSwGSvgYOwE3a8bx8i78Y1Rm5dDNpm5InqmYLfdnxnwRfofL/2O+zAOhJ5XDtssRP2IV+vyVh4jKz4OJbUo7T7cp1GIPtOXU3jicyS0fa65kyDIu8kZ27uLrbDTCNM4fv1iNeGBwsKvlYV7dAxjne88MlOhUui27TM5cof8cvDk6fJeh4KvgbhQsxuH4ue7Ct6DGksvsFQ6vx8QIoPiceCkVxBjyU5YopLvE2fG51TN5rXNl7hQbmP7PAtE3JCjR4woetvzNUT0UppCPIcs1UUQ36CNsWeuvF+mR/vNspcR9FFtvecfWr8lWY7ZDQTtLvdTbDa0TMD2SIn1nhuOMmU8tPDOgLGn2ITZh75qVQZuLzwLGsAAYZzTFN18uCaNQL7O/4UIfCF1NcPJ9zC9E6xhUzcEVbR61L+iNgALa38lBo5x/WuPgTO+XE8UhGDZcS9v+0B3xhFjsG2st8V0V2iqH7QlQs+DUZH16fz8a6eYFNSMDO+9SSiwkUce6I3odDmAost0jZRHCFZhqPewUmuGn3LPdq3Un6EyKiEngQiPfJQpYXCtCTpIKf8rvFjE/TbVL/WdruDdR5YZ6JN4VTVygSf+XKLk9xWbgQSK3DbAFSz0/LO81k2OG29Etfh/dbHt1U36Adk0B+Bf6M4Q8vOncbVCfRkaZ4iu2DH3LTb0ZngQByT4NrLToW5WiyfmScbZFOSDw/i2N6jMyMcMC1NOIPGTdJwNzTVYbxRGUj9oHMNdYWKzWLxRphpZkH+E9nWswy/FDz1gPzSPV+uroC2Oxq2YTjCXS+Sr/E+aYqMhAiD0glBj6CWFJK1uy6DyoMtyqK37t73WcnbqmNnP6ze9/USxfjH/AqKvB4yvHKyhFXWG94zc5lEdBwubxS2NScqWrfb8owYLbxVvHbPXDBy3e68jetJa1tSEad/SnaN+KUS+GvDWZtn+HBx6bW1vV1qYOFaKu6pMQqWdtFz3sYGWFO2F766cALkoLY0OdupOHc37hRwsiVsoJ7odCepd6mtSWYLvNukIbe3/UGWbic/mBxZMPmAOHZVjpwoaO27nBDp106JB0VYPyrbCZrOmGLrilAjP9EGPaVpRVd65kAZpSIl4uX6zfRwSDTZDd870C7ZB5ORb/WY6qdNJoeWg8v7eALS7lFg5cVVn/dN65nlGCgW6yOC4QZCXHjUwwI4g1uJCo7E1Uvy1FOfSccbbNseVRJVLeGwOwwoWk78MPIOud6K2Lg/G2gUwUe9ydsErR32eXv6urG7NgjZg/Jx6TU/aJAD7Uxy9twIp+6WbFD3ACpwJ132CeSB7kdWVadDZIorZaHaHU1UNyMvJ5BrXJIJI/AUMQEtUGS7vcc2z81+ZE+1E5rPEL0/kFwJ9TOjrftCKGIJF9tgXVHHhtnsYPokNSV1POK4QRVN3rTZlbh0ei2lnUkqa4+NG+g2yaJjKbhOuleLj0fBqCnptt9opZE90uLue8FdLEiv4xo/Inq7JK36DBfBmjxomFtOcm6IjVIlki6ffe7oBDEEiq8TwSgup454AT1T+ExOz5R83mlSKdz2cqyghDX3J8crEtAuYnJggaJRGy5zIDGtEOp1gztCBGUwTsVK28J4PuaUhqu959fHwMAFKqi7NPNi0HL4x7ODwyfOpIs9n7cB17EZZ55HZJOZkhieSXXE3Fbe7WJJiKLwluUFtElzoN2dIdigCdydVeKkHfRTc+skH3RqeOJ0jd7mnbR2hb1ZN/6tisrq5tR9SgqH6QDEm3jaj5iQQYl2FteguMjYY0RsjIUDW4kq9KTkxMHAkSrhsWOS3E/10+Gh6G49oa4wnxtS6aF+KE137/CGzSCKOk3qpr9yDxe+t9hZzx5j1l7TdSX7sMF5N5k5aC122pB2VQ1Kfpko84paJbknSF3aH44PZ4ur1YVQeEKvVfUG8VdNeGL0BulQiESODQ3CUBo9XEPk2SLqou3Q8Z53jO1tZcO9c0BLNlcFMTeGkhkiTvQEa1n5GoYf67q4y+1l0sa7fs3SBwVoTlDgY3Llic2TbeHKylS53rHEZit2Tlp7mipsIYRnqbtsPUzavAqdOTbGwdg/Uc8vzYuR+tJWaK0giECTfjVLFVR0G7ojTMJhpYVZUYyxG61GHdQLdfz0LIe0IlsAEl+HOrTjdhHqNEEo92b1GPEz4hvBZGHtjS+cYmidAEnNzfNuePt1oR1Ct6EmuqavoNtD4sKqCNCnSlcOFoAau+6fTyMcjHZzyu6qSKBbIKtaTRsLPq/JoN4xI10bVhs8d9aoRqciPVqnO5B0E5NNoSDvHnlabMl75mbY1LlMFic3TmMfp7bYZ51FyLlj3bzKFnwIe1peaRPoMUfTdiT3ldzKd91MoHsiqFxxVyzEVgwVplNJmRqANqmADWRo1Lg0S8zJz2vQU2oJD7RkjR/0/Gg7AIo0jFypbiOIY2FbnHV1HPsJU7yNZqjZV4JJJ4RE8c9wsN3A4eHulLR1mjE0fBXuOjxd1nv/LnMnay9fJ+s2kWJzvMaE7+CNjjZ4DaXe04RLth/aRHGLBg/TnOjkOJLwLOil83BHqmDQHq2oR8I5uO83LAtxSXoZp+dVNJXI3cPuGZK3ZHbATkUweU7tcUg9IDAKxIQRoGy6cWA1wWEi4oUj4abEWodIxkif2ZAbkCFOxuEe5wfkomIHglLR01rYswKaOlB74sK4U/pWqE5WZF05j8NS1zpvqM1OqK0qBrrAt2TCs8QdC0/3YEAHmHF1FvQf/C6TMziQ1/WB3ms5oaqHNpXIAqdKt1RT+Hx83uoqS+6uEreRH+Ns1o5nKpV1HPCWHblwSwaGfLSKbleO14zUlMPDta+n7AB5DUwCUK01uD6CFsq5HhBvyJ9pAp/rFLKDseqfxU2jrHo8j9i4ts+CnvUDjYSpF9FlTJ8S5V6eJ9+lj6xxk1Gs6lqtlaPjrThO9cbAyHBnCM9zRnU4Xt+u2NHg1YoZ0EvNKU14jNKdMVppUiI9DNWYa21JGO4DblL89jnEo8HgXLbxQvtKV+leBQqDC5SgBdiRpEbawIEqeIdwl7ByVNFsvRdNB1tb5+jqS7qSZ/BEuMmg35jQDhJvfIpPOlZxNrk8r/twT0eu86jzmMIUr1nzIbp32373CFqoHPow9BuKH1KhijVLGOXsSGlijluGspcJs93Q7UaiYi3C6kLQYHJrNnJbXU8bhYfla23EuB17LGjCNo+BE8s+W0fP/oYbddRLG+NJUfH6VsuheWVoe5ft0VD2D0fcRNYpzgXruupoJtnEVeJLJaY5iZqqylPTBigMqwPhec5GVx/C6ezmBo2c4DFwp8piKBGd+i4kojAE9V2KKbmq96iSNWe02LeoutkzCTmebKSz60q/GNSaA1q5cnZ7jKgCkz5Ydh1B4khajoTE6bWDby7ZOq4W9K0zIdMgTlIU3bJ+/Qiz3c2lESTRMbNiPLxhS/faqYPVifqAahfjCSWK8NCxSomKlLiWWtDoEB46XEydqQ3uCVMwCAQa5sfcRhA04WM3o3eBF5p2ppzIAywgTP7wbffmx/bEkFYxpVQp7a1TdySPtE0e+f0Jn8YDFvAG4d/klKhKFZTAE2OeFNLj27ufCdUVRfLB4MMEacZaEh/qPbHuENt77K7SoXLPn7e7aw9zU5nCKOjw9ijeglip0+nKHavz86kRAzNiSJW6tzwEPe4JOXHj2VYe2iRWVqCdn/ERYowRw6BsAhrrKcH7wtmajiLfLNfctYdmgKGiJjur2Z0qA0PvbsTelcYFrTNURu35sYM5UZZMfU+JeSSZDophR/TY+HVDD4ORpyh9xW+RIKd0vraRfU0NG43u4mvyeI4ZF5I8pCHj0eYahL7GcKg7mHe7KI3oMMwNgxWzdhW0PuGnPUtW2REaMe9UkkR/eYzQpTwivHKWiDTtlS6GkAi/ELmkHTOlaNvoxp7FKD/Ga4YwxiSOcUE4rdHTdB9ksQ6Rjs/Pe06g8IEYq5wyDTGW6JSAh7OY32FnlNKIDdt2j2L6uXmeh/iCpAwAXyaLFQfFDUXQwc1SFKayn8XTks9i4kGYFxQoPuw8Ob5DeiLUJKyfrzfOuxZXE9QMR4eVbN9z5CROEHqoyVzkJrZ3I1GoE6wOqDrpjn7o41SyO1SbNXtgrMY1eqKwtsK+6km4rXuC2jxHsd3AdrI1Bhq/AWHDra9m/mxclx9JOHRc4wqdoAliQQM2wEUWdOcEge0cqpsyLsuDGxXGvcg3gQqx+IENCfVQMxeZSnOTnmqpHskdq8r8jdzcQTddsaVst61WWrRX6JJJ5KQhYOQh0/PmQvEE1BQXVjByN+otxXSqrBm1jIGSWmecXdYcIsGLbjfOvqVEyzLk2FvXB3karjFJbE6tS2ThBpb1bqaYa0I5D0VsnVOQuOVxZ1phP6YYBT9RopZPjA7Ru02B8SV9kKETVzkeMw1+QTvSEKeVVPcDD3qBUrzi6y66GBcxhqK6sJDTreETDcZSI34UtBxz5JZUrmEm1hWb3/RjthlC3DvmG+6aqBycXjCEx5zpJAEl4z7tgxlwJhI9hIB3rn60d6TYbeRHelRO8mmMBpcqIOuaSvndJScriQYa9gkZIxmvpmQkKYSqi3L3yDwmRw3G2w1O72SZK3lTCPTVjl1phPeTF5wyEw2L7NHXIQiM5Fuj1AihJWiO7Jtmlun1Oo+HZ29nTe37ChSJj/YRP0nzuncqtki38VN28gHf3KvGins/A0ygpe35np0HJjJuhYPF7F6XiZE4bPYubt9tEaajzS50MCmaMGyNhG643qqnjttfYtHfzr/X/vhhzvzGLQiL9VqTRFn+kjrzr8ADE8UJMEJQlkkhJOx6NAybGxSnKZTEHIsmYIQyTRSxNy4M2+gGpW2EoDcW6ZjuxnVoB7cIwrKWt3jzK22wVWaDvf71bX6l/HV5Pff1px2bHDQLX533d4jLy936L9jyq5f6L/Tbp/9imp3Pvyhovn7+l9cLv7+CG+0QGI58gd9er2brcP5h5MdL5Dpp/fcTz+ccwQbpvy2vo4fm457G9N9/Nf/+U4fXemDFv/0fEDJYpSoyAAA=
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
