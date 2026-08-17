#!/usr/bin/env python3
"""Voice-only re-mix: rebuild the narration track from the VO stems alone and
mux it over the finished video, so the presenter can lay their own music underneath.

Built in TWO steps on purpose:
  1. stems  -> narration.wav   (the video is not an input at all)
  2. video + narration.wav -> output   (-map 0:v -map 1:a, video stream copied)

Step 1 having no video input is the whole point. The single-command version
indexed the stems as [0:a], [1:a]... while ffmpeg input 0 was the VIDEO — so
the finished film's own audio (the same narration at its own timing, plus the
music bed) got mixed in as if it were a stem, and the last stem was dropped.
That is what "two tracks talking over each other" was.

    python3 remix_nobed.py customer
    python3 remix_nobed.py training
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE / "work"
DIST = HERE / "dist"
TARGET_DB = -16.0

CUTS = {
    "customer": {"video": DIST / "S4HANA_Knowledge_Companion_Showcase.mp4",
                 "map": WORK / "beatmap_customer.json", "prefix": "vo",
                 "out": DIST / "S4HANA_Knowledge_Companion_Showcase_NOBED.mp4"},
    "training": {"video": DIST / "MCP_Attach_Training.mp4",
                 "map": WORK / "beatmap_training.json", "prefix": "tr",
                 "out": DIST / "MCP_Attach_Training_NOBED.mp4"},
}


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip())


def mean_db(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                        "volumedetect", "-f", "null", "/dev/null"],
                       capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            return float(line.split("mean_volume:")[1].split("dB")[0])
    return None


def slot_starts(mapping, prefix):
    return {seg["vo"]: float(seg.get("t0", 0.0)) + float(seg.get("off", 0.0))
            for seg in mapping.get("segments", [])
            if isinstance(seg.get("vo"), str) and seg["vo"].startswith(prefix)}


def build(kind):
    cfg = CUTS[kind]
    if not cfg["video"].exists():
        print(f"skip {kind}: {cfg['video'].name} not built")
        return
    starts = slot_starts(json.loads(cfg["map"].read_text()), cfg["prefix"])
    stems = [s for s in sorted((WORK / "vo").glob(cfg["prefix"] + "*.wav"))
             if s.stem in starts]
    if not stems:
        print(f"skip {kind}: no stems matched the beatmap")
        return
    total = probe_duration(cfg["video"])

    # ---- step 1: narration.wav from stems ONLY (no video input) -------------
    inputs, filters, labels = [], [], []
    for i, s in enumerate(stems):                    # here input i IS stem i
        gain = TARGET_DB - (mean_db(s) or TARGET_DB)
        delay = int(starts[s.stem] * 1000)
        inputs += ["-i", str(s)]
        filters.append(
            f"[{i}:a]afftdn=nr=24:nf=-48,"                    # cut room tone
            f"agate=threshold=0.0025:ratio=9:attack=5:release=90:knee=2,"
            f"volume={gain:.2f}dB,"
            f"afade=t=in:st=0:d=0.04,"
            f"adelay={delay}|{delay}[a{i}]")
        labels.append(f"[a{i}]")
    fg = (";".join(filters) + ";" + "".join(labels) +
          f"amix=inputs={len(labels)}:normalize=0,alimiter=limit=0.95,"
          f"apad,atrim=0:{total}[out]")
    narr = WORK / f"narration_{kind}.wav"
    run(["ffmpeg", "-y", "-v", "error"] + inputs +
        ["-filter_complex", fg, "-map", "[out]", "-ac", "2", "-ar", "48000",
         str(narr)])

    # ---- step 2: mux video + narration --------------------------------------
    run(["ffmpeg", "-y", "-v", "error", "-i", str(cfg["video"]), "-i", str(narr),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-shortest", str(cfg["out"])])

    streams = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
         "-of", "csv=p=0", str(cfg["out"])], capture_output=True, text=True
    ).stdout.split()
    print(f"{kind}: {cfg['out'].name} — {len(stems)} stems, narration "
          f"{mean_db(narr)} dB, streams {streams}")


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["customer", "training"]):
        build(k)
