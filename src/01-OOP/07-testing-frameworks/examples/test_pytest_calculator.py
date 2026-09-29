"""Testy kalkulatora w stylu **pytest**.

    python -m pytest src/01-OOP/07-testing-frameworks/examples/test_pytest_calculator.py -v

Ten plik testuje **ten sam kod** co ``test_unittest_calculator.py``. Porównaj
oba pliki i zwróć uwagę na różnice:

===============  ===================================  ======================================
Aspekt           ``unittest``                         ``pytest``
===============  ===================================  ======================================
Struktura        klasa ``TestCase`` + metody          zwykłe funkcje ``test_*``
Asercje          ``self.assertEqual(a, b)``           ``assert a == b`` (przepisywany przez pytest)
Przygotowanie    ``setUp`` / ``setUpClass``           fixture'y (``@pytest.fixture``), ``yield``
Parametryzacja   ``subTest``                          ``@pytest.mark.parametrize``
Wyjątki          ``assertRaises`` / ``assertRaisesRegex``  ``pytest.raises(..., match=...)``
Float            ``assertAlmostEqual``                ``pytest.approx``
Uruchamianie     ``python -m unittest``               ``pytest`` (uruchamia też unittest!)
===============  ===================================  ======================================

Dlaczego ``assert`` działa tak dobrze? pytest **przepisuje** bajtkod modułów
testowych, żeby w komunikacie porażki pokazać wartości pośrednie:

    assert calc.add(2, 3) == 5
    E   assert 6 == 5
    E    +  where 6 = calc.add(2, 3)
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from calculator import Calculator, parse_number

# --------------------------------------------------------------------------- #
# Fixture'y - odpowiednik setUp, ale mogą być współdzielone i parametryzowane
# --------------------------------------------------------------------------- #


@pytest.fixture
def calc() -> Calculator:
    """Świeży kalkulator dla każdego testu, który o niego poprosi."""
    return Calculator()


# --------------------------------------------------------------------------- #
# Arytmetyka - jedna asercja, jedna własność
# --------------------------------------------------------------------------- #


def test_add_returns_sum(calc):
    assert calc.add(2, 3) == 5


def test_subtract_returns_difference(calc):
    assert calc.subtract(10, 4) == 6


def test_multiply_returns_product(calc):
    assert calc.multiply(6, 7) == 42


def test_divide_returns_quotient(calc):
    assert calc.divide(10, 4) == 2.5


def test_divide_by_zero_raises_zero_division_error(calc):
    with pytest.raises(ZeroDivisionError):
        calc.divide(1, 0)


def test_divide_by_zero_message_explains_the_reason(calc):
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        calc.divide(1, 0)


def test_division_result_may_be_inexact(calc):
    assert calc.divide(1, 3) == pytest.approx(0.3333333333, rel=1e-6)


# --------------------------------------------------------------------------- #
# Parametryzacja - odpowiednik `subTest`, ale wynik każdego przypadku jest
# osobnym wpisem w raporcie: test_add_returns_sum[2-3-5]
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (2, 3, 5),
        (-1, 1, 0),
        (0.1, 0.2, 0.30000000000000004),   # arytmetyka binarnego float
    ],
)
def test_add_returns_sum_for_multiple_pairs(calc, a, b, expected):
    assert calc.add(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("values", [[5], [1, 2, 3, 4], (3, 3, 3), [0]])
def test_average_of_non_empty_sequence(calc, values: Sequence[float]):
    assert calc.average(values) == pytest.approx(sum(values) / len(values))


def test_average_of_empty_sequence_raises(calc):
    with pytest.raises(ValueError, match="empty"):
        calc.average([])


# --------------------------------------------------------------------------- #
# Testy czystej funkcji
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("42", 42.0),
        ("3,5", 3.5),
        ("  7.25  ", 7.25),
        ("-0,5", -0.5),
    ],
)
def test_parse_number_accepts_supported_formats(text, expected):
    assert parse_number(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["abc", "", ",", "1,2,3"])
def test_parse_number_rejects_non_numeric_text(text):
    with pytest.raises(ValueError, match="cannot parse number"):
        parse_number(text)


def test_parse_number_rejects_non_string_input():
    with pytest.raises(TypeError):
        parse_number(42)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Fixture na poziomie modułu z klasą TestCase (dowód na interoperacyjność)
# --------------------------------------------------------------------------- #


class TestCalculatorAsClass:
    """Ten sam styl co ``unittest``, ale bez dziedziczenia - czysty pytest."""

    def test_class_based_tests_are_collected(self, calc):
        assert calc.add(1, 1) == 2

    def test_class_based_tests_can_use_fixtures(self, calc):
        assert calc.subtract(5, 5) == 0
