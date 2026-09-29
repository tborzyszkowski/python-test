"""Mały moduł produkcyjny do demonstracji **izolacji testów**.

Uruchomienie::

    python src/01-OOP/06-unit-test-anatomy/examples/config_reader.py

Ten moduł celowo dotyka „trudnych” zasobów, od których testy muszą się
odizolować:

* **zmiennych środowiskowych** (``os.environ``),
* **systemu plików** (``pathlib.Path``),
* **czasu** (``datetime``),
* **losowości** (``random``).

Każdy z tych zasobów jest źródłem niedeterminizmu: ten sam test może przechodzić
lokalnie, a padać na serwerze CI (inna strefa czasowa, brak katalogu, już
ustawiona zmienna środowiskowa). W ``test_isolation.py`` zobaczysz, jak
izolować każdy z nich **bez** zmiany kodu produkcyjnego.
"""

from __future__ import annotations

import json
import os
import random
import string
from datetime import UTC, datetime
from pathlib import Path


def read_timeout(default: float = 5.0) -> float:
    """Timeout z ``APP_TIMEOUT`` (sekundy) albo wartość domyślna."""
    raw = os.environ.get("APP_TIMEOUT")
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"APP_TIMEOUT must be a number, got {raw!r}") from exc


def save_config(path: Path, data: dict[str, object]) -> None:
    """Zapisuje konfigurację do pliku JSON (UTF-8, klucze posortowane)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def load_config(path: Path) -> dict[str, object]:
    """Wczytuje konfigurację; brak pliku -> ``FileNotFoundError``."""
    return json.loads(path.read_text(encoding="utf-8"))


def new_session_id(length: int = 8) -> str:
    """Losowy identyfikator sesji (małe litery i cyfry)."""
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def utc_timestamp() -> str:
    """Znacznik czasu w ISO 8601 (UTC), np. ``2026-09-29T10:15:30+00:00``."""
    return datetime.now(tz=UTC).isoformat(timespec="seconds")


def main() -> None:
    print(f"read_timeout()   -> {read_timeout()}")
    print(f"new_session_id() -> {new_session_id()}")
    print(f"utc_timestamp()  -> {utc_timestamp()}")


if __name__ == "__main__":
    main()
