#!/usr/bin/env python3
"""Compress dead time out of the captured demo slot.

The raw capture holds long frozen spans while the agent thinks. Reading holds
are kept (they are the point); spinner holds are compressed. Frames are
compared by hash: any run of identical frames longer than KEEP is collapsed to
KEEP seconds. NEVER motion-interpolates — hard cuts only.
"""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
CAPS = HERE / "captures"
FRAMES = CAPS / "frames"
KEEP = 1.6          # seconds a frozen span is allowed to hold
MAX_HOLD = 3.0      # ceiling for any single frame's duration


def main():
    meta = json.loads((CAPS / "frames.json").read_text())
    rows = []
    for i, m in enumerate(meta):
        dur = (meta[i + 1]["ts"] - m["ts"]) if i + 1 < len(meta) else 0.6
        h = hashlib.md5((FRAMES / m["file"]).read_bytes()).hexdigest()
        rows.append({"file": m["file"], "dur": max(dur, 0.02), "hash": h})

    # collapse runs of identical frames
    out, i, dropped = [], 0, 0.0
    while i < len(rows):
        j = i
        span = 0.0
        while j < len(rows) and rows[j]["hash"] == rows[i]["hash"]:
            span += rows[j]["dur"]
            j += 1
        if span > KEEP:
            dropped += span - KEEP
            out.append({"file": rows[i]["file"], "dur": KEEP})
        else:
            out.append({"file": rows[i]["file"], "dur": min(span, MAX_HOLD)})
        i = j

    total = sum(r["dur"] for r in out)
    lines = []
    for r in out:
        lines.append(f"file 'frames/{r['file']}'\nduration {r['dur']:.3f}")
    lines.append(f"file 'frames/{out[-1]['file']}'")
    (CAPS / "concat-tight.txt").write_text("\n".join(lines))

    dst = CAPS / "demo-slot-tight.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(CAPS / "concat-tight.txt"),
                    "-vf", "scale=1440:-2,fps=30", "-pix_fmt", "yuv420p",
                    "-c:v", "libx264", "-crf", "18", str(dst)], check=True)
    print(f"distinct states: {len(out)} / {len(rows)} frames")
    print(f"compressed {dropped:.0f}s of dead time -> {total:.1f}s")
    print("wrote", dst)


if __name__ == "__main__":
    main()
