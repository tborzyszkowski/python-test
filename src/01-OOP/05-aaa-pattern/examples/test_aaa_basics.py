"""Przykład - struktura AAA na klasach z tematu 02.

    python -m pytest src/01-OOP/05-aaa-pattern/examples/test_aaa_basics.py -v

Testujemy klasę ``Rectangle`` i ``Temperature`` z tematu 02 (``solutions_02.py``).
Kod produkcyjny się nie zmienia - zmienia się tylko **sposób** jego testowania.

Ten plik pokazuje **to samo** oczekiwanie napisane trzy razy:

1. ``test_bez_aaa`` - wersja „strumieniowa”: przygotowanie, akcje i weryfikacje
   pomieszane w jednej linii,
2. ``test_z_aaa`` - wersja z jawnymi sekcjami AAA,
3. ``test_z_aaa_i_kontekstem`` - wersja z AAA i opisem intencji, czyli test,
   który ktoś przeczyta ze zrozumieniem za pół roku.
"""

from __future__ import annotations

import pytest

from solutions_02 import Rectangle, Temperature

# --------------------------------------------------------------------------- #
# ❌ Wersja bez AAA
# --------------------------------------------------------------------------- #


def test_bez_aaa():
    r = Rectangle(2, 3)
    assert r.area == 6 and r.perimeter == 10 and r.is_square is False
    r.width = 4
    assert r.area == 12


# Co jest nie tak?
#  * przygotowanie (`r = Rectangle(2, 3)`), akcje i 3 asercje w jednym miejscu,
#  * asercje połączone `and` - przy porażce nie wiemy, która część padła,
#  * dwie niezależne akcje (konstrukcja i zmiana szerokości) w jednym teście,
#  * nie wiadomo, która wartość jest „danymi”, a która „oczekiwaniem”.


# --------------------------------------------------------------------------- #
# ✅ Wersja z AAA
# --------------------------------------------------------------------------- #


def test_z_aaa():
    # Arrange
    rectangle = Rectangle(width=2, height=3)

    # Act
    area = rectangle.area

    # Assert
    assert area == pytest.approx(6.0)


def test_z_aaa_i_kontekstem():
    """Pole prostokąta 2 x 3 to 6 (jednostek kwadratowych)."""

    # Arrange
    rectangle = Rectangle(width=2, height=3)

    # Act
    area = rectangle.area

    # Assert
    assert area == pytest.approx(6.0)


# Dlaczego wersja z AAA jest lepsza?
#  * trzy sekcje = trzy pytania: co mam na wejściu? co robię? czego oczekuję?
#  * wynik akcji zapisujemy w zmiennej o nazwie mówiącej CO to jest
#    (`area`, nie `result`),
#  * jedna asercja na jedną własność -> komunikat porażki wskazuje przyczynę,
#  * `pytest.approx` zamiast `==` dla `float`.


# --------------------------------------------------------------------------- #
# Zmiana stanu to osobny test (osobny Act)
# --------------------------------------------------------------------------- #


def test_area_tracks_width_change():
    # Arrange
    rectangle = Rectangle(width=2, height=3)

    # Act
    rectangle.width = 4
    area = rectangle.area

    # Assert
    assert area == pytest.approx(12.0)


# --------------------------------------------------------------------------- #
# AAA dla ścieżki błędu - "Act" to wywołanie, które MA zawieść
# --------------------------------------------------------------------------- #


def test_aaa_dla_sciezki_bledu():
    # Arrange
    rectangle = Rectangle(width=2, height=3)

    # Act + Assert
    with pytest.raises(ValueError, match="positive"):
        rectangle.width = 0

    # Assert (stan po nieudanej operacji)
    assert rectangle.width == pytest.approx(2.0)


def test_aaa_dla_odebrania_niepoprawnej_temperatury():
    # Arrange
    temperature = Temperature(25)

    # Act + Assert
    with pytest.raises(ValueError, match="absolute zero"):
        temperature.celsius = -300

    # Assert - poprzednia wartość zachowana
    assert temperature.celsius == pytest.approx(25.0)


# --------------------------------------------------------------------------- #
# AAA z parametrami - jedna własność, wiele przypadków
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("sides", "expected_area"),
    [
        ((1, 1), 1.0),
        ((2, 3), 6.0),
        ((2.5, 4), 10.0),
    ],
)
def test_area_of_rectangle(sides, expected_area):
    # Arrange
    width, height = sides
    rectangle = Rectangle(width=width, height=height)

    # Act
    area = rectangle.area

    # Assert
    assert area == pytest.approx(expected_area)


# Uwaga na `parametrize`: **dane są już częścią Arrange**, więc ciało testu
# zaczyna się od utworzenia obiektu. To nadal AAA - Arrange przyjmuje postać
# parametrów testu. W raporcie zobaczysz osobny wynik dla każdego zestawu:
# test_area_of_rectangle[2.5-4-10.0].


# --------------------------------------------------------------------------- #
# Trudniejszy przypadek: arytmetyka zmiennoprzecinkowa
# --------------------------------------------------------------------------- #


def test_float_comparison_requires_approx():
    """0.1 * 0.3 != 0.3 - dlatego porównania `float` robimy przez `approx`."""
    # Arrange
    rectangle = Rectangle(width=0.1, height=3.0)

    # Act
    area = rectangle.area

    # Assert
    assert area != 0.3                 # dowód, że `==` tu nie zadziała
    assert area == pytest.approx(0.3)  # a to jest porównanie poprawne
