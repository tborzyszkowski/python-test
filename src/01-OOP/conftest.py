"""Wspólna konfiguracja pytest oraz helpery dla modułu ``01-OOP``.

Pytest, przy domyślnym trybie importu (``prepend``), dodaje do ``sys.path``
katalog *zawierający* plik testowy. W tym module testy leżą w podkatalogach
``examples/`` i ``exercises/`` każdego tematu, więc importy typu
``from solutions_02 import Point`` działają "od razu" dla pliku testowego.

Ten plik robi to samo jawnie i deterministycznie dla **wszystkich** tematów,
dzięki czemu:

* w jednym przebiegu ``pytest`` można importować moduły z każdego tematu,
* można uruchamiać kod przykładowy z dowolnego miejsca (np. z notebooka
  albo z REPL-a) bez ręcznego manipulowania ``sys.path``.

Nazwy plików w katalogach ``examples/`` i ``exercises/`` są **unikalne w całym
module** (np. ``solutions_02.py``, ``tools_polymorphism.py``), dlatego
wszystkie katalogi mogą współistnieć w ``sys.path`` bez kolizji nazw modułów.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

MODULE_ROOT = Path(__file__).resolve().parent


def _topic_directories() -> list[Path]:
    """Zwraca katalogi tematów, np. ``01-class-vs-object`` (posortowane)."""
    return sorted(
        d
        for d in MODULE_ROOT.iterdir()
        if d.is_dir() and d.name[:1].isdigit() and not d.name.startswith("__")
    )


def _extend_import_path() -> list[str]:
    """Dodaje katalogi ``examples/``, ``exercises/`` i ``src/`` każdego tematu."""
    added: list[str] = []
    for topic in _topic_directories():
        for sub in ("examples", "exercises", "src"):
            candidate = topic / sub
            if not candidate.is_dir():
                continue
            entry = str(candidate)
            if entry not in sys.path:
                sys.path.insert(0, entry)
                added.append(entry)
    if str(MODULE_ROOT) not in sys.path:
        sys.path.insert(0, str(MODULE_ROOT))
        added.append(str(MODULE_ROOT))
    return added


ADDED_IMPORT_PATHS = _extend_import_path()


# --------------------------------------------------------------------------- #
# Wspólne fixture'y                                                        #
# --------------------------------------------------------------------------- #


@pytest.fixture
def tolerance() -> float:
    """Domyślna tolerancja porównań liczb zmiennoprzecinkowych (1e-9)."""
    return 1e-9


@pytest.fixture
def tmp_json_file(tmp_path: Path):
    """Fabryka plików JSON w katalogu tymczasowym ``tmp_path``.

    Użycie w teście::

        def test_loads_config(tmp_json_file):
            path = tmp_json_file({"level": 3})
            assert load_config(path)["level"] == 3

    Fixture jest przykładem *setup/teardown* zarządzanym przez pytest —
    pliki tworzone są w ``tmp_path``, który pytest sprząta automatycznie.
    """

    def _make(payload: Any, name: str = "data.json") -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    return _make
