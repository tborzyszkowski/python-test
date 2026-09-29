"""Przykład - Arrange jako fixture: przygotowanie przeniesione poza test.

    python -m pytest src/01-OOP/05-aaa-pattern/examples/test_aaa_with_fixtures.py -v

Gdy to samo przygotowanie powtarza się w kilku testach, przenosimy je do
**fixture**. Zysk:

* test czyta się jak specyfikacja zachowania (zostaje Act + Assert),
* przygotowanie jest w jednym miejscu - zmiana modelu danych nie wymaga
  edycji dwudziestu testów,
* fixture może być *parametryzowana*, więc jeden test obsługuje wiele wariantów
  przygotowania (patrz ``any_rectangle``).

Uwaga dydaktyczna: **fixture nie ukrywa Arrange, tylko je nazywa.** Nazwa
fixture (``small_rectangle``) mówi, jaki stan przygotowuje - i to jest cała
różnica między dobrą a złą abstrakcją.
"""

from __future__ import annotations

import pytest
from solutions_02 import Rectangle, Temperature

# --------------------------------------------------------------------------- #
# Fixture'y - nazwane sekcje Arrange
# --------------------------------------------------------------------------- #


@pytest.fixture
def small_rectangle() -> Rectangle:
    """Prostokąt 2 x 3 (pole 6, obwód 10, nie jest kwadratem)."""
    return Rectangle(width=2, height=3)


@pytest.fixture
def square() -> Rectangle:
    """Kwadrat 4 x 4."""
    return Rectangle(width=4, height=4)


@pytest.fixture
def temperature_25() -> Temperature:
    """Temperatura pokojowa: 25 C = 298.15 K = 77 F."""
    return Temperature(25)


# --------------------------------------------------------------------------- #
# Testy korzystające z fixture jako gotowego Arrange
# --------------------------------------------------------------------------- #


def test_area_of_small_rectangle(small_rectangle):
    # Arrange - wykonane przez fixture `small_rectangle`
    # Act
    area = small_rectangle.area

    # Assert
    assert area == pytest.approx(6.0)


def test_square_is_recognised(square):
    # Arrange - fixture `square`
    # Act
    is_square = square.is_square

    # Assert
    assert is_square is True


def test_derived_units_of_room_temperature(temperature_25):
    # Arrange - fixture `temperature_25`
    # Act
    kelvin = temperature_25.kelvin
    fahrenheit = temperature_25.fahrenheit

    # Assert
    assert kelvin == pytest.approx(298.15)
    assert fahrenheit == pytest.approx(77.0)


# --------------------------------------------------------------------------- #
# Fixture parametryzowana: jeden test, trzy różne Arrange
# --------------------------------------------------------------------------- #


@pytest.fixture(params=[(1, 1), (2, 3), (2.5, 4)])
def any_rectangle(request) -> Rectangle:
    """Parametryzowana fixture - jeden test uruchomi się trzy razy."""
    width, height = request.param
    return Rectangle(width=width, height=height)


def test_every_rectangle_has_positive_area(any_rectangle):
    """Własność (niezmiennik): pole prostokąta jest zawsze dodatnie."""
    # Arrange - fixture `any_rectangle`
    # Act
    area = any_rectangle.area

    # Assert
    assert area > 0


def test_invariant_holds_after_scaling(small_rectangle):
    """Niezmiennik po operacji: skalowanie nie psuje relacji boków."""
    # Arrange
    original_ratio = small_rectangle.height / small_rectangle.width

    # Act
    scaled = small_rectangle.scale(3)

    # Assert
    assert scaled.height / scaled.width == pytest.approx(original_ratio)
    assert scaled.area == pytest.approx(small_rectangle.area * 9)


# --------------------------------------------------------------------------- #
# Fixture vs tworzenie obiektu w teście - kiedy co?
# --------------------------------------------------------------------------- #
# * 1-2 testy używają stanu      -> twórz obiekt w teście (Arrange inline),
# * 3+ testy używają tego stanu  -> fixture,
# * stan wymaga "sprzątania"     -> fixture z `yield` (setup/teardown),
# * stan ma warianty             -> fixture parametryzowana lub `parametrize`,
# * stan jest zależnością (np. fake bramki płatności) -> fixture w `conftest.py`.
