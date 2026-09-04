#!/usr/bin/env python3
"""Launcher. The converter lives in skills/rapp-skills/scripts/rapp_skills.py so a
copied skill folder is self-sufficient; this file only forwards to it."""
import runpy, sys
from pathlib import Path
sys.argv[0] = "rapp-skills"
runpy.run_path(str(Path(__file__).resolve().parent / "skills" / "rapp-skills" / "scripts" / "rapp_skills.py"), run_name="__main__")
