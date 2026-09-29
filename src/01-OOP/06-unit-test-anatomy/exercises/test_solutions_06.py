"""Wzorcowe rozwiązanie tematu 06 - anatomia testu jednostkowego.

    python -m pytest src/01-OOP/06-unit-test-anatomy/exercises/test_solutions_06.py -v

Cztery wzorce, które warto wynieść z tego pliku:

1. **Jedna własność na test** - każdy test pada z jednego powodu.
2. **Nazwa = specyfikacja** - ``pytest -v`` czyta się jak lista wymagań.
3. **Izolacja stanu klasowego** - fixture ``autouse=True``.
4. **Determinizm** - losowość i czas podstawiamy przez ``monkeypatch``.
"""

from __future__ import annotations

import random

import pytest

from config_reader import new_session_id
from solutions_01 import Ammo
from solutions_03 import Car, Engine
from solutions_04 import Hammer, ToolBrokenError

# --------------------------------------------------------------------------- #
# Fixture'y
# --------------------------------------------------------------------------- #


@pytest.fixture
def car() -> Car:
    """Samochód z pełnym bakiem (50 l) i silnikiem 5.5 l/100 km."""
    return Car("Skoda", Engine(power_kw=110, consumption_l_per_100km=5.5), tank_l=50)


@pytest.fixture(autouse=True)
def reset_ammo_counter():
    """Izolacja stanu klasowego.

    # WYBÓR: fixture ``autouse=True`` zamiast ręcznego ``Ammo.reset_counter()``
    # w każdym teście - nie da się zapomnieć, a intencja jest widoczna
    # w jednym miejscu (mniej powtórzeń, mniej okazji do błędu).
    """
    Ammo.reset_counter()
    yield
    Ammo.reset_counter()


# --------------------------------------------------------------------------- #
# Zadanie 1 - Car.drive: jedna własność na test
# --------------------------------------------------------------------------- #


def test_drive_100_km_consumes_5_5_liters(car):
    # Arrange + Act
    car.drive(100)

    # Assert
    assert car.fuel_l == pytest.approx(44.5)


def test_drive_returns_fuel_level(car):
    # Arrange + Act
    returned = car.drive(200)

    # Assert
    assert returned == pytest.approx(39.0)
    assert returned == car.fuel_l


def test_drive_beyond_range_raises_and_keeps_fuel(car):
    # Arrange
    fuel_before = car.fuel_l

    # Act + Assert
    with pytest.raises(ValueError, match="not enough fuel"):
        car.drive(10_000)

    # Assert
    assert car.fuel_l == pytest.approx(fuel_before)


@pytest.mark.parametrize("distance", [0, -1, -100])
def test_drive_rejects_non_positive_distance(car, distance):
    # Arrange + Act + Assert
    with pytest.raises(ValueError, match="positive"):
        car.drive(distance)


def test_range_is_recalculated_after_drive(car):
    # Arrange
    car.drive(100)                       # zostaje 44.5 l

    # Act
    fuel_range = car.range_km

    # Assert
    assert fuel_range == pytest.approx(44.5 / 5.5 * 100)


def test_drive_consumption_scales_linearly_with_distance(car):
    """Własność: dwukrotny dystans = dwukrotne zużycie paliwa."""
    # Arrange
    reference = Car("Skoda", Engine(110, 5.5), tank_l=50)
    doubled = Car("Skoda", Engine(110, 5.5), tank_l=50)

    # Act
    reference.drive(50)
    doubled.drive(100)

    # Assert
    used_once = 50 - reference.fuel_l
    used_twice = 50 - doubled.fuel_l
    assert used_twice == pytest.approx(2 * used_once)


# --------------------------------------------------------------------------- #
# Zadanie 2 - izolacja licznika klasowego
# --------------------------------------------------------------------------- #


def test_ammo_counter_starts_at_zero():
    # Arrange + Act
    count = Ammo.created_count()

    # Assert
    assert count == 0


def test_ammo_counter_increments_per_instance():
    # Arrange + Act
    Ammo("9mm", 10)
    Ammo("5.56mm", 30)

    # Assert
    assert Ammo.created_count() == 2


def test_ammo_counter_does_not_leak_between_tests():
    # Arrange + Act + Assert
    assert Ammo.created_count() == 0        # dzięki fixture `autouse`


def test_ammo_counter_increments_for_subclasses():
    # Arrange
    class SteelAmmo(Ammo):
        pass

    # Act
    SteelAmmo("9mm", 5)

    # Assert
    assert Ammo.created_count() == 1


# --------------------------------------------------------------------------- #
# Zadanie 3 - test własności dla Hammer.nail
# --------------------------------------------------------------------------- #


@pytest.fixture
def hammer() -> Hammer:
    """Młotek z dużym zapasem wytrzymałości (wear_per_use = 3)."""
    return Hammer("młotek", weight_kg=1.0, durability=100)


@pytest.mark.parametrize("count", [1, 3, 5])
def test_nail_returns_one_effect_per_nail(hammer, count):
    # Arrange + Act
    effects = hammer.nail("gwóźdź", count)

    # Assert
    assert len(effects) == count


@pytest.mark.parametrize("count", [1, 3, 5])
def test_nail_increments_uses_by_count(hammer, count):
    # Arrange + Act
    hammer.nail("gwóźdź", count)

    # Assert
    assert hammer.uses == count


@pytest.mark.parametrize("count", [1, 3, 5])
def test_nail_consumes_wear_per_use_durability(hammer, count):
    # Arrange
    starting_durability = hammer.durability

    # Act
    hammer.nail("gwóźdź", count)

    # Assert
    assert hammer.durability == starting_durability - count * Hammer.wear_per_use


def test_nail_never_produces_negative_durability():
    """Osobny test na drugą własność: nasycenie wytrzymałości przy zerze."""
    # Arrange
    hammer = Hammer("młotek", weight_kg=1.0, durability=4)

    # Act
    hammer.nail("gwóźdź", 1)             # 4 - 3 = 1
    durability_after_first_use = hammer.durability
    hammer.nail("gwóźdź", 1)             # 1 - 3 -> 0 (nasycenie, bez wartości ujemnej)

    # Assert
    assert durability_after_first_use == 1
    assert hammer.durability == 0
    assert hammer.is_broken is True
    # ...a kolejna próba użycia już musi zawieść (i to konkretnym wyjątkiem!)
    with pytest.raises(ToolBrokenError, match="broken"):
        hammer.nail("gwóźdź", 1)


@pytest.mark.parametrize("count", [0, -1])
def test_nail_rejects_non_positive_count(hammer, count):
    # Arrange + Act + Assert
    with pytest.raises(ValueError, match="count"):
        hammer.nail("gwóźdź", count)


# --------------------------------------------------------------------------- #
# Zadanie 4 - determinizm losowości
# --------------------------------------------------------------------------- #


def test_session_id_has_requested_length():
    # Arrange + Act
    session_id = new_session_id(length=10)

    # Assert
    assert len(session_id) == 10


def test_session_id_contains_only_lowercase_and_digits():
    # Arrange
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789")

    # Act
    session_id = new_session_id(length=64)

    # Assert
    assert set(session_id) <= allowed


def test_session_id_is_deterministic_when_randomness_is_patched(monkeypatch):
    # Arrange
    monkeypatch.setattr(random, "choices", lambda alphabet, k: ["x"] * k)

    # Act
    session_id = new_session_id(length=6)

    # Assert
    assert session_id == "xxxxxx"


def test_session_id_is_deterministic_with_fixed_seed():
    # Arrange
    random.seed(42)
    first = new_session_id(length=12)

    # Act
    random.seed(42)
    second = new_session_id(length=12)

    # Assert
    assert first == second
