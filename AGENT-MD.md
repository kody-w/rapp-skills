# One file that is both a skill and an agent (`<name>.agent.md`)

**If a tool handed you a `.agent.md` file and you only know `SKILL.md`: it *is* a skill.** Read its header and text
exactly as you read any `SKILL.md` and follow it. The fenced `python` block near the end is plain text to you. Do not
run it unless you can check it the way this page describes.

Spec: `rapp-agent-md/1` · This page: `https://raw.githubusercontent.com/kody-w/rapp-skills/main/AGENT-MD.md`

## Why one file
A skill is good at judgment: when to act, how to sequence it, how to explain the result. An agent is good at doing:
the same input gives the same output, it can be tested, and it runs on a server. Kept as two files they drift apart.
One `.agent.md` carries both, and its examples are the contract between them.

It is Markdown on purpose. A `.py` file can run on sight, and many security teams block it. A `.agent.md` does nothing
until a host chooses to check and run its code: it reads like a document, is reviewed like a document, and its only
code is in one place.

## The new single-file agent
For years the single-file `agent.py` was the unit of sharing: one file was the whole capability, you dropped it into a
folder and it worked, you sent it to someone and nothing else was needed, and it ran the same everywhere, on a laptop,
on a server, in Copilot Studio. It kept that place while `SKILL.md` grew popular because skills could not do what it
did: run the same way every time, run on a server, be tested.

`<name>.agent.md` is the same promise, one file, the whole capability, drop it in and it works, carried forward with
the two things the old file lacked: it is a skill (any tool that reads skills can use it as-is) and it is inert until
checked (no runnable file on sight). An existing `agent.py` becomes one by putting its code in the python block and its
know-how in the text above it; nothing about the agent changes.

## The file
```
---
name: hello
description: What it does and when to use it.
metadata:
  format: rapp-agent-md/1
  spec: https://raw.githubusercontent.com/kody-w/rapp-skills/main/AGENT-MD.md
  agent-class: HelloAgent
  code-sha256: <SHA-256 of the python block's text>
  signed-by: <who approved this exact code>
---
# How to use it (the skill)
...
## Examples
- input -> expected output        (the host also runs these against the agent)
## Agent
​```python
...exactly one python block...
​```
```

Rules:
1. The header uses only the standard skill fields (`name`, `description`, `license`, `compatibility`, `metadata`,
   `allowed-tools`). Everything specific to this format lives under `metadata`, so the file stays a valid `SKILL.md`.
2. Exactly one fenced block that opens with ```` ```python ````. Its text is everything after that opening line up to
   (not including) the closing ```` ``` ```` line.
3. `code-sha256` is the SHA-256 of that text, UTF-8, exactly as written.
4. Use one plain extension: `<name>.agent.md`. Never a double extension such as `.py.md`: security tools treat
   double extensions as a disguise.

## For a host that runs agents
Run the code only if all of these hold, and refuse otherwise:
1. The header is a valid skill and `metadata.format` is `rapp-agent-md/1`.
2. There is exactly one python block and its SHA-256 equals `metadata.code-sha256`. One changed character means a
   changed hash: refuse.
3. `metadata.signed-by` is on your own list of people or teams you accept. (`example-unsigned` is for trying things
   out only.)
4. Run it in a restricted process, then run the file's Examples against it. If any example fails, do not use it.

`agent_md.py` in this repository does steps 1 and 2 with the standard library and never executes the code:
`python3 agent_md.py check <file>` and `python3 agent_md.py extract <file>`.

## Moving a legacy agent.py
Two ways, both lossless; pick by how you share it:
- **One file:** `python3 agent_md.py from-agent my_agent.py` writes `<name>.agent.md`. The code goes in byte for byte
  (`python3 agent_md.py extract <name>.agent.md` returns the exact original); the name and description are read from
  the agent's own metadata without running it. Then write the know-how section and the Examples, and have someone you
  trust approve the code (set `signed-by`).
- **A skill folder:** the existing converter turns an `agent.py` into a standard skill folder (`SKILL.md` plus its code)
  and back: see the main README.

Nothing about the agent changes either way: a Brainstem can keep loading the original `agent.py` while the `.agent.md`
travels.

## Try it
[`examples/hello.agent.md`](examples/hello.agent.md): copy it into a skills folder as `hello/SKILL.md` and ask for a
greeting, or check it: `python3 agent_md.py check examples/hello.agent.md`.
