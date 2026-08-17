#!/usr/bin/env python3
"""Capture the customer demo slot: drive the published agent in Preview and
record TAB-ONLY via CDP screencast. Never closes the browser (new tabs only).

    python3 capture_demo.py            # full 5-question take
    python3 capture_demo.py --one      # single question (rehearsal)
"""
import base64, json, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
CAPS = HERE / "captures"; FRAMES = CAPS / "frames"
QUESTIONS = [
    "Who is responsible for the Finance workstream, and who covers if they're out?",
    "Who owns the Procure-to-Pay process?",
    "Which resources are available for the change management and training stream?",
    "I have a data migration blocker that's been open for a week - who do I escalate to, and who is their backup?",
    "Which plants and company codes are in Wave 1 scope?",
]


SPINNERS = ("Working on it", "Thinking", "Generating", "Let me ")


def settle(pg, timeout=300):
    """Answer is done when: no spinner text, a Citations block landed, and the
    body has stopped growing. A length-plateau alone is NOT enough — the page
    sits still while the spinner spins, which once let a take type the next
    question over an unfinished answer."""
    last, stable, t0 = 0, 0, time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        body = pg.inner_text("body")
        cur = len(body)
        busy = any(s in body[-1500:] for s in SPINNERS)
        if cur == last and not busy:
            stable += 1
            if stable >= 4:
                return True
        else:
            last, stable = cur, 0
    return False


def main():
    qs = QUESTIONS[1:2] if "--one" in sys.argv else QUESTIONS
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        pg = next(p for c in b.contexts for p in c.pages if "copilotstudio" in p.url)
        pg.bring_to_front()
        try:
            pg.get_by_role("button", name="New chat").first.click(); time.sleep(4)
        except Exception:
            pass

        sess = pg.context.new_cdp_session(pg)
        meta, n = [], {"i": 0}

        def on_frame(params):
            n["i"] += 1
            (FRAMES / f"f{n['i']:05d}.png").write_bytes(base64.b64decode(params["data"]))
            meta.append({"file": f"f{n['i']:05d}.png", "ts": params["metadata"]["timestamp"]})
            sess.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})

        sess.on("Page.screencastFrame", on_frame)
        sess.send("Page.startScreencast", {"format": "png", "everyNthFrame": 2,
                                           "maxWidth": 1440, "maxHeight": 900})
        time.sleep(2)
        for i, q in enumerate(qs, 1):
            box = pg.locator("textarea").first
            box.click(); box.fill(q)
            pg.keyboard.press("Enter")
            ok = settle(pg)
            print(f"[{i}/{len(qs)}] {'ok' if ok else 'TIMEOUT'} — {q[:50]}")
            time.sleep(4)  # reading hold
        time.sleep(2)
        sess.send("Page.stopScreencast")
        (CAPS / "frames.json").write_text(json.dumps(meta))
        print("frames captured:", len(meta))
        assemble(meta)


def assemble(meta):
    if len(meta) < 2:
        print("too few frames"); return
    lines = []
    for i, m in enumerate(meta):
        dur = (meta[i + 1]["ts"] - m["ts"]) if i + 1 < len(meta) else 0.5
        lines.append(f"file 'frames/{m['file']}'\nduration {min(max(dur, 0.02), 4.0):.3f}")
    lines.append(f"file 'frames/{meta[-1]['file']}'")
    (CAPS / "concat.txt").write_text("\n".join(lines))
    out = CAPS / "demo-slot.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(CAPS / "concat.txt"),
                    "-vf", "scale=1440:-2,fps=30", "-pix_fmt", "yuv420p",
                    "-c:v", "libx264", "-crf", "18", str(out)], check=True, capture_output=True)
    print("assembled:", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
