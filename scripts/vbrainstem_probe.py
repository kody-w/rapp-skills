#!/usr/bin/env python3
"""Execute an agent or build one from SKILL.md inside the live vbrainstem."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONVERTER = (
    ROOT / "engine" / "rapp-agent-converter" / "scripts" / "toast.py"
)
VBRAINSTEM = "https://kody-w.github.io/vbrainstem/"

RUN_AGENT = """
import base64, json, brainstem_web
_src = base64.b64decode(AGENT_B64).decode("utf-8")
_out = brainstem_web.rapp_run(_src, AGENT_NAME, REQUEST, ARGS_OBJ)
print(json.dumps(_out))
"""

BUILD_AND_RUN = """
import base64, hashlib, importlib.util, json, os, sys, brainstem_web

os.makedirs("/tmp/converter", exist_ok=True)
converter_path = "/tmp/converter/toast.py"
skill_path = "/tmp/converter/SKILL.md"
open(converter_path, "w").write(base64.b64decode(CONVERTER_B64).decode())
skill_bytes = base64.b64decode(SKILL_B64)
open(skill_path, "wb").write(skill_bytes)

spec = importlib.util.spec_from_file_location("rapp_agent_converter", converter_path)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

rci = converter.read_skill(skill_bytes, "SKILL.md")
agent_src = converter.write_agent(rci).decode()
out = brainstem_web.rapp_run(agent_src, rci["name"], REQUEST, ARGS_OBJ)
print(json.dumps({
    "runtime": sys.version.split()[0],
    "agent_sha256": hashlib.sha256(agent_src.encode()).hexdigest()[:16],
    "agent_bytes": len(agent_src),
    "executed": out.get("executed"),
    "ran_class": out.get("ran_class"),
    "output": out.get("output") or out.get("error") or "",
}))
"""

EVAL_JS = """
async ({code, consts}) => {
  let head = '';
  for (const [k, v] of Object.entries(consts)) {
    head += (typeof v === 'string' && k.endsWith('_B64'))
      ? `${k} = ${JSON.stringify(v)}\\n`
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
    parser.add_argument("--agent", help="an existing *_agent.py to hot-load")
    parser.add_argument("--skill", help="a SKILL.md to convert and execute")
    parser.add_argument(
        "--converter",
        default=str(DEFAULT_CONVERTER),
        help="the submitted rapp-agent-converter scripts/toast.py",
    )
    parser.add_argument("--args", default="{}", help="JSON args for perform()")
    parser.add_argument("--request", default="run it")
    parser.add_argument("--name", default="Agent", help="display name with --agent")
    opts = parser.parse_args()

    if opts.skill and not Path(opts.converter).is_file():
        print(f"converter not found: {opts.converter}", file=sys.stderr)
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
            print(
                f"   booted CPython {health['runtime'].split()[-1]} "
                f"| registry {health['registry']} | agents {health['agents']}"
            )

            if not opts.agent and not opts.skill:
                print("boot probe only — pass --agent or --skill to execute one")
                return 0

            if opts.agent:
                print(f"-> hot-loading {opts.agent}")
                consts = {
                    "AGENT_B64": base64.b64encode(
                        Path(opts.agent).read_bytes()
                    ).decode(),
                    "AGENT_NAME": opts.name,
                    "REQUEST": opts.request,
                    "ARGS_OBJ": args_obj,
                }
                raw = await page.evaluate(
                    EVAL_JS, {"code": RUN_AGENT, "consts": consts}
                )
            else:
                print(f"-> converting {opts.skill} in-browser")
                consts = {
                    "CONVERTER_B64": base64.b64encode(
                        Path(opts.converter).read_bytes()
                    ).decode(),
                    "SKILL_B64": base64.b64encode(
                        Path(opts.skill).read_bytes()
                    ).decode(),
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
