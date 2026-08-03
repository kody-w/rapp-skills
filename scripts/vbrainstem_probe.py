#!/usr/bin/env python3
"""Prove a toasted skill runs in the browser, with no local Python at all.

`rapp-agent-bridge` splits hosts into two tiers: those that can execute the
`*_agent.py` and those that can only read the markdown. That split is not fixed
hardware — a host with no shell can still reach Tier 1 through a Pyodide
runtime. This script proves that route works against the LIVE vbrainstem rather
than asserting it.

Three probes, each strictly stronger than the last:

    boot    headless Chromium loads https://kody-w.github.io/vbrainstem/ and
            waits for CPython to come up in Pyodide. No install, no UI.
    agent   push an existing *_agent.py SOURCE STRING into that runtime and
            execute it via brainstem_web.rapp_run — the same entry the local
            brainstem uses.
    skill   push toaster.py AND a raw SKILL.md, toast + convert to an agent
            in-browser, then run the result. toaster.py is stdlib-only, so the
            whole SKILL.md -> agent.py -> execute chain runs client-side.

The `skill` probe additionally prints the capability_id, which should match the
value `roundtrip_fidelity.py` reports for the same skill locally — proving the
browser-built agent is the same capability, not merely a similar-looking one.

Usage:
    pip install playwright && playwright install chromium

    python3 scripts/vbrainstem_probe.py
    python3 scripts/vbrainstem_probe.py --agent ship/ship_agent.py \
        --args '{"repo":"demo-site"}'
    python3 scripts/vbrainstem_probe.py --skill ship/SKILL.md \
        --toaster ../rapp-toaster/toaster.py --args '{"repo":"demo-site"}'

Exits non-zero if the runtime never comes up or the agent does not execute.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

VBRAINSTEM = "https://kody-w.github.io/vbrainstem/"

# Toasting appends these; stripping them returns a committed skill to the raw
# bread the browser-side toast expects. Anchored to whole lines so a skill that
# *documents* the markers is not mistaken for a real block.
GENERATED_BLOCK = re.compile(
    r"\n?^<!-- toaster:generated:begin -->$.*?^<!-- toaster:generated:end -->$\n?",
    re.S | re.M,
)
CAPSULE = re.compile(r"\n?^<!-- rci-capsule:v1:[^>]*-->$\n?", re.S | re.M)

# Runs inside Pyodide. rapp.eval() sends multi-line code through exec(), which
# discards a trailing expression -- results must be printed, not returned.
RUN_AGENT = """
import base64, json, brainstem_web
_src = base64.b64decode(AGENT_B64).decode("utf-8")
_out = brainstem_web.rapp_run(_src, AGENT_NAME, REQUEST, ARGS_OBJ)
print(json.dumps(_out)[:4000])
"""

BUILD_AND_RUN = """
import base64, importlib.util, json, os, sys, brainstem_web

os.makedirs("/tmp/tk", exist_ok=True)
open("/tmp/tk/toaster.py", "w").write(base64.b64decode(TOASTER_B64).decode())
open("/tmp/tk/SKILL.md", "w").write(base64.b64decode(SKILL_B64).decode())

spec = importlib.util.spec_from_file_location("toaster", "/tmp/tk/toaster.py")
tk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tk)

rci = tk.load("/tmp/tk/SKILL.md", "skill")
# Drop the vaulted raw copy or render() restores the bytes we are replacing and
# the toast silently no-ops -- same rule `toaster.py toast` follows.
rci.setdefault("preserved", {}).pop("skill", None)
tk.toast_rci(rci)
agent_src = tk.render(rci, "agent").decode()

out = brainstem_web.rapp_run(agent_src, rci["name"], REQUEST, ARGS_OBJ)
print(json.dumps({
    "runtime": sys.version.split()[0],
    "capability_id": tk.capability_id(rci)[:12],
    "params": sorted((rci.get("parameters") or {}).get("properties", {})),
    "steps": len((rci.get("impl") or {}).get("steps") or []),
    "agent_bytes": len(agent_src),
    "executed": out.get("executed"),
    "ran_class": out.get("ran_class"),
    "output": out.get("output") or out.get("error") or "",
})[:4000])
"""

# btoa() is latin-1 only, so the source is UTF-8 encoded before base64 and
# decoded as UTF-8 on the Python side -- otherwise any em dash breaks the round
# trip, and these skills are full of them.
EVAL_JS = """
async ({code, consts}) => {
  const enc = (s) => btoa(String.fromCharCode(...new TextEncoder().encode(s)));
  let head = '';
  for (const [k, v] of Object.entries(consts)) {
    head += (typeof v === 'string' && k.endsWith('_B64'))
      ? `${k} = "${enc(v)}"\\n`
      : `${k} = json.loads(${JSON.stringify(JSON.stringify(v))})\\n`;
  }
  return await window.rapp.eval('import json\\n' + head + code);
}
"""


async def boot(page, timeout_s: int = 300) -> dict | None:
    await page.goto(VBRAINSTEM, wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_function("() => !!window.rapp", timeout=120_000)
    return await page.evaluate(
        """async (tries) => {
             for (let i = 0; i < tries; i++) {
               try {
                 const h = await window.rapp.health();
                 if (h && h.status === 'ok') return h;
               } catch (e) {}
               await new Promise(r => setTimeout(r, 2000));
             }
             return null;
           }""",
        timeout_s // 2,
    )


def show(payload: dict) -> None:
    for key, value in payload.items():
        if key == "output":
            print("  output:")
            for line in str(value).splitlines()[:24]:
                print("    " + line)
        else:
            print(f"  {key}: {value}")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", help="an existing *_agent.py to hotload")
    parser.add_argument("--skill", help="a SKILL.md to toast + convert in-browser")
    parser.add_argument("--toaster", help="toaster.py, required with --skill")
    parser.add_argument("--args", default="{}", help="JSON args for perform()")
    parser.add_argument("--request", default="run it")
    parser.add_argument("--name", default="Agent", help="display name with --agent")
    opts = parser.parse_args()

    if opts.skill and not opts.toaster:
        print("--skill needs --toaster (see kody-w/rapp-toaster)", file=sys.stderr)
        return 2

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print(
            "playwright missing:\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    args_obj = json.loads(opts.args)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"-> {VBRAINSTEM}")
            health = await boot(page)
            if not health:
                print("FAIL: Pyodide never reported healthy")
                return 1
            print(f"   booted CPython {health['runtime'].split()[-1]} "
                  f"| registry {health['registry']} | agents {health['agents']}")

            if not opts.agent and not opts.skill:
                print("boot probe only — pass --agent or --skill to execute one")
                return 0

            if opts.agent:
                print(f"-> hotloading {opts.agent}")
                consts = {
                    "AGENT_B64": Path(opts.agent).read_text(encoding="utf-8"),
                    "AGENT_NAME": opts.name,
                    "REQUEST": opts.request,
                    "ARGS_OBJ": args_obj,
                }
                raw = await page.evaluate(
                    EVAL_JS, {"code": RUN_AGENT, "consts": consts}
                )
            else:
                print(f"-> building {opts.skill} into an agent in-browser")
                text = Path(opts.skill).read_text(encoding="utf-8")
                consts = {
                    "TOASTER_B64": Path(opts.toaster).read_text(encoding="utf-8"),
                    "SKILL_B64": CAPSULE.sub("", GENERATED_BLOCK.sub("", text)),
                    "REQUEST": opts.request,
                    "ARGS_OBJ": args_obj,
                }
                raw = await page.evaluate(
                    EVAL_JS, {"code": BUILD_AND_RUN, "consts": consts}
                )

            out = (raw or {}).get("output", "").strip()
            if not out:
                print("FAIL: runtime returned nothing")
                return 1
            try:
                payload = json.loads(out)
            except json.JSONDecodeError:
                print("FAIL: non-JSON from runtime:\n" + out[:1500])
                return 1

            show(payload)
            if not payload.get("executed"):
                print("FAIL: agent did not execute")
                return 1
            print("PASS: executed in the browser, no local Python")
            return 0
        finally:
            await browser.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
