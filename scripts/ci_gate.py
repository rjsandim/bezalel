#!/usr/bin/env python3
"""Atalho nesta árvore para skills/issue-bot/scripts/ci_gate.py (a skill é autocontida)."""
from pathlib import Path
import runpy
import sys

TARGET = Path(__file__).resolve().parents[1] / 'skills/issue-bot/scripts/ci_gate.py'
sys.argv[0] = str(TARGET)
runpy.run_path(str(TARGET), run_name='__main__')
