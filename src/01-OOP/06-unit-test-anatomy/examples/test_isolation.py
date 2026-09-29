"""Przykład - izolacja testów: środowisko, pliki, losowość, czas, stan klasowy.

    python -m pytest src/01-OOP/06-unit-test-anatomy/examples/test_isolation.py -v

Test jednostkowy ma być **deterministyczny**: te same dane wejściowe, ten sam
wynik, niezależnie od tego, co dzieje się wokół (kolejność testów, katalog
roboczy, zmienne środowiskowe, strefa czasowa, losowość).

Pięć typowych źródeł niedeterminizmu i narzędzia, które je neutralizują:

| Źródło | Narzędzie pytest | Co robi |
|---|---|---|
| zmienne środowiskowe | ``monkeypatch.setenv`` / ``delenv`` | ustawia/usuwa na czas testu i przywraca po |
| system plików | ``tmp_path`` | świeży, unikalny katalog, sprzątany automatycznie |
| losowość | ``monkeypatch.setattr`` / ``random.seed`` | ustala wynik losowania |
| czas / strefa czasowa | ``monkeypatch.setattr`` na ``datetime`` | „zamraża” zegar |
| stan klasowy współdzielony | fixture ``autouse=True`` | zeruje stan przed i po każdym teście |

Wszystkie te narzędzia działają **bez zmiany kodu produkcyjnego** - i o to
chodzi: izolacja to zadanie testu, nie produkcji.
"""

from __future__ import annotations

import json
import random
import string
from datetime import datetime

import config_reader
import pytest
from config_reader import load_config, new_session_id, read_timeout, save_config, utc_timestamp
from solutions_01 import Ammo

# --------------------------------------------------------------------------- #
# 1. Zmienne środowiskowe (monkeypatch)
# --------------------------------------------------------------------------- #


def test_read_timeout_uses_default_when_variable_is_missing(monkeypatch):
    # Arrange
    monkeypatch.delenv("APP_TIMEOUT", raising=False)

    # Act
    timeout = read_timeout(default=5.0)

    # Assert
    assert timeout == 5.0


def test_read_timeout_reads_environment_variable(monkeypatch):
    # Arrange
    monkeypatch.setenv("APP_TIMEOUT", "12.5")

    # Act
    timeout = read_timeout()

    # Assert
    assert timeout == 12.5


def test_read_timeout_rejects_garbage(monkeypatch):
    # Arrange
    monkeypatch.setenv("APP_TIMEOUT", "wkrótce")

    # Act + Assert
    with pytest.raises(ValueError, match="APP_TIMEOUT"):
        read_timeout()


# monkeypatch automatycznie przywraca poprzednią wartość zmiennej, dlatego
# dwa powyższe testy nie kolidują ze sobą, mimo że dotykają tego samego
# zasobu globalnego.

# --------------------------------------------------------------------------- #
# 2. System plików (tmp_path)
# --------------------------------------------------------------------------- #


def test_save_and_load_config_roundtrip(tmp_path):
    # Arrange
    path = tmp_path / "nested" / "config.json"
    data = {"level": 3, "name": "Aragorn"}

    # Act
    save_config(path, data)
    loaded = load_config(path)

    # Assert
    assert loaded == data
    assert path.exists()                      # katalog `nested` powstał sam
    assert json.loads(path.read_text(encoding="utf-8"))["level"] == 3


def test_load_config_of_missing_file_raises(tmp_path):
    # Arrange
    missing = tmp_path / "nie-ma-mnie.json"

    # Act + Assert
    with pytest.raises(FileNotFoundError):
        load_config(missing)


def test_save_config_sorts_keys(tmp_path):
    # Arrange
    path = tmp_path / "config.json"

    # Act
    save_config(path, {"zeta": 1, "alpha": 2})

    # Assert
    assert path.read_text(encoding="utf-8").startswith('{"alpha"')


# `tmp_path` daje **inny** katalog w każdym teście, więc testy nie widzą
# nawzajem swoich plików. Nic nie zostaje na dysku po zakończeniu przebiegu.

# --------------------------------------------------------------------------- #
# 3. Losowość (monkeypatch / seed)
# --------------------------------------------------------------------------- #


def test_session_id_has_requested_length():
    # Arrange + Act
    session_id = new_session_id(length=12)

    # Assert
    assert len(session_id) == 12


def test_session_id_uses_only_allowed_characters():
    # Arrange
    allowed = set(string.ascii_lowercase + string.digits)

    # Act
    session_id = new_session_id(length=50)

    # Assert
    assert set(session_id) <= allowed


def test_session_id_is_deterministic_under_monkeypatch(monkeypatch):
    """Zamiast zgadywać losową wartość, podstawiamy własne losowanie."""
    # Arrange
    monkeypatch.setattr(random, "choices", lambda alphabet, k: ["a"] * k)

    # Act
    session_id = new_session_id(length=5)

    # Assert
    assert session_id == "aaaaa"


def test_session_id_is_deterministic_under_seed():
    # Arrange
    random.seed(1234)
    expected = new_session_id(length=8)

    # Act
    random.seed(1234)
    repeated = new_session_id(length=8)

    # Assert
    assert repeated == expected


@pytest.mark.parametrize("bad_length", [0, -3])
def test_session_id_rejects_non_positive_length(bad_length):
    # Arrange + Act + Assert
    with pytest.raises(ValueError, match="length"):
        new_session_id(bad_length)


# --------------------------------------------------------------------------- #
# 4. Czas (monkeypatch na module produkcyjnym)
# --------------------------------------------------------------------------- #


class _FrozenDatetime(datetime):
    """Podklasa ``datetime`` z zamrożonym ``now()`` (klasyczny sposób w testach)."""

    @classmethod
    def now(cls, tz=None):  # noqa: D102 - sygnatura musi zgadzać się z datetime
        return cls(2026, 1, 2, 3, 4, 5, tzinfo=tz)


def test_utc_timestamp_is_frozen(monkeypatch):
    # Arrange
    monkeypatch.setattr(config_reader, "datetime", _FrozenDatetime)

    # Act
    timestamp = utc_timestamp()

    # Assert
    assert timestamp == "2026-01-02T03:04:05+00:00"


def test_utc_timestamp_ends_with_utc_offset():
    """Test bez zamrażania zegara sprawdza tylko format, nie konkretną datę."""
    # Arrange + Act
    timestamp = utc_timestamp()

    # Assert
    assert timestamp.endswith("+00:00")
    assert "T" in timestamp


# Zasada: nie testuj „jaka jest godzina”, testuj **co kod robi z czasem**
# (np. format, strefę). Dokładną wartość wstawiamy przez monkeypatch.

# --------------------------------------------------------------------------- #
# 5. Stan klasowy współdzielony (fixture autouse)
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def reset_ammo_counter():
    """Zeruje licznik klasowy przed i po każdym teście w tym module."""
    Ammo.reset_counter()
    yield
    Ammo.reset_counter()


def test_counter_starts_from_zero():
    assert Ammo.created_count() == 0


def test_counter_counts_created_instances():
    Ammo("9mm", 10)
    assert Ammo.created_count() == 1


def test_counter_is_not_polluted_by_previous_test():
    """Gdyby nie fixture `autouse`, ten test zależałby od kolejności wykonania."""
    assert Ammo.created_count() == 0


# Dlaczego to działa bez `autouse`? Nie działałoby! Stan klasowy żyje tak długo,
# jak proces Pythona - czyli przez cały przebieg pytest. Fixture rozwiązuje
# problem w jednym miejscu i dla wszystkich testów.
