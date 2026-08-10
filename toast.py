#!/usr/bin/env python3
"""Run the converter skill vendored as this repository's engine."""

from pathlib import Path
import runpy


runpy.run_path(
    str(
        Path(__file__).resolve().parent
        / "engine"
        / "rapp-agent-converter"
        / "scripts"
        / "toast.py"
    ),
    run_name="__main__",
)
