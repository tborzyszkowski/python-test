"""Przykład - nazwa testu i zakres testu (jedna własność jednej metody).

    python -m pytest src/01-OOP/06-unit-test-anatomy/examples/test_naming_and_scope.py -v

Ten plik to zestaw **kontrastów**: najpierw wersja, której nie chcemy, potem
wersja poprawna. Każda para dotyczy tego samego kodu produkcyjnego
(``Car``/``Engine`` z tematu 03 oraz ``Ammo`` z tematu 01).

Trzy zasady, które ilustrujemy:

1. **Nazwa opisuje zachowanie**, nie numer testu ani nazwę metody:
   ``test_drive_reduces_fuel_by_consumption`` zamiast ``test_drive_1``.
2. **Jedna własność na test** - jedna „przyczyna porażki”.
3. **Test dotyczy jednej metody/funkcji** - jeśli test woła trzy metody,
   to prawdopodobnie są to trzy testy (albo test integracyjny).
"""

from __future__ import annotations

import pytest
from solutions_01 import AmmoV1
from solutions_03 import Car, Engine

# --------------------------------------------------------------------------- #
# 1. Nazewnictwo
# --------------------------------------------------------------------------- #


def test_car_1():                     # ❌ nazwa nie mówi nic o zachowaniu
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)
    assert car.fuel_l == 50


def test_drive_reduces_fuel():        # ✅ co testujemy i czego oczekujemy
    # Arrange
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)

    # Act
    car.drive(100)

    # Assert
    assert car.fuel_l == pytest.approx(44.5)   # 100 km * 5.5 l/100 km


def test_negative_amount_is_rejected():   # ✅ warunek + oczekiwanie
    # Arrange
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)

    # Act + Assert
    with pytest.raises(ValueError, match="positive"):
        car.drive(-1)


# Wzorzec nazwy:  test_<jednostka>_<warunek>_<oczekiwany rezultat>
#   test_drive_when_tank_is_empty_raises_value_error
#   test_discount_above_100_percent_is_rejected
#   test_parse_price_of_empty_string_raises_value_error
#
# Dzięki takim nazwom raport `pytest -v` czyta się jak lista wymagań.

# --------------------------------------------------------------------------- #
# 2. Zakres testu - jedna własność, jedna przyczyna porażki
# --------------------------------------------------------------------------- #


def test_car_everything():            # ❌ 4 własności, 4 możliwe przyczyny porażki
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)
    assert car.fuel_l == 50
    car.drive(100)
    assert car.fuel_l == pytest.approx(44.5)
    car.refuel(1000)
    assert car.fuel_l == 50
    car.fuel_l = 10
    assert car.range_km == pytest.approx(181.8181818, rel=1e-6)


def test_car_starts_with_full_tank():          # ✅
    # Arrange + Act
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)

    # Assert
    assert car.fuel_l == pytest.approx(50.0)


def test_refuel_never_exceeds_tank_capacity():  # ✅
    # Arrange
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)
    car.drive(500)

    # Act
    car.refuel(1000)

    # Assert
    assert car.fuel_l == pytest.approx(50.0)


def test_range_is_derived_from_current_fuel():  # ✅
    # Arrange
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)
    car.fuel_l = 11                       # 11 l / 5.5 l/100 km * 100 = 200 km

    # Act
    fuel_range = car.range_km

    # Assert
    assert fuel_range == pytest.approx(200.0)


# --------------------------------------------------------------------------- #
# 3. "Jedna metoda" - test nie powinien być scenariuszem całego przepływu
# --------------------------------------------------------------------------- #


def test_full_purchase_flow():        # ❌ to jest test integracyjny, nie jednostkowy
    """Woła trzy metody i sprawdza sześć rzeczy - trudno wskazać winowajcę."""
    ammo = AmmoV1("9mm", 10)
    remaining = ammo.spend(4)
    assert remaining == 6
    assert ammo.rounds == 6
    assert repr(ammo) == "AmmoV1(caliber='9mm', rounds=6)"
    assert ammo == AmmoV1("9mm", 6)
    assert ammo != AmmoV1("9mm", 5)
    assert ammo.rounds > 0


def test_spend_returns_remaining_rounds():   # ✅ jedna metoda, jedna własność
    # Arrange
    ammo = AmmoV1("9mm", 10)

    # Act
    remaining = ammo.spend(4)

    # Assert
    assert remaining == 6


def test_repr_shows_caliber_and_rounds():    # ✅ kolejna własność = kolejny test
    # Arrange + Act
    text = repr(AmmoV1("9mm", 6))

    # Assert
    assert text == "AmmoV1(caliber='9mm', rounds=6)"


def test_equality_ignores_object_identity():  # ✅
    # Arrange + Act + Assert
    assert AmmoV1("9mm", 6) == AmmoV1("9mm", 6)


# --------------------------------------------------------------------------- #
# 4. Test własności (property-based thinking) - jedna metoda, wiele danych
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("spent", [1, 2, 5, 10])
def test_spend_never_returns_negative_rounds(spent):
    """Własność: liczba naboi po ``spend`` nigdy nie jest ujemna."""
    # Arrange
    ammo = AmmoV1("9mm", 10)

    # Act
    remaining = ammo.spend(spent)

    # Assert
    assert remaining >= 0
    assert remaining == 10 - spent
