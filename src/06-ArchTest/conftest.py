"""Wspolne sciezki importow dla materialow testowania architektury."""

from __future__ import annotations

import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent

for topic in sorted(path for path in MODULE_ROOT.iterdir() if path.is_dir() and path.name[:1].isdigit()):
    for subdirectory in ("examples", "exercises", "src"):
        candidate = topic / subdirectory
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
