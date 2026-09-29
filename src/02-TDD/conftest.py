"""Wspolne sciezki importow i fixture'y dla modulu 02-TDD."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

MODULE_ROOT = Path(__file__).resolve().parent


def _topic_directories() -> list[Path]:
    return sorted(
        directory
        for directory in MODULE_ROOT.iterdir()
        if directory.is_dir() and directory.name[:1].isdigit()
    )


for topic in _topic_directories():
    for subdirectory in ("examples", "exercises", "src"):
        candidate = topic / subdirectory
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


@pytest.fixture
def tolerance() -> float:
    """Wspolna tolerancja porownan float."""
    return 1e-9
