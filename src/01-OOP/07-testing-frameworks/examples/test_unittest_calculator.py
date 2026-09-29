"""Testy kalkulatora w stylu **unittest** (framework z biblioteki standardowej).

Uruchomienie (dwa sposoby)::

    python -m pytest src/01-OOP/07-testing-frameworks/examples/test_unittest_calculator.py -v
    python -m unittest discover -s src/01-OOP/07-testing-frameworks/examples -p "test_unittest_*.py" -v

Cechy charakterystyczne ``unittest``, które zobaczysz w tym pliku:

* testy to **metody klas** dziedziczących po ``unittest.TestCase``,
* przygotowanie stanu robi się w ``setUp`` (przed każdym testem) i
  ``setUpClass`` (raz na klasę),
* asercje to metody: ``assertEqual``, ``assertAlmostEqual``, ``assertTrue``,
  ``assertRaises``, ``assertRaisesRegex``, ``assertIn``,
* ``self.subTest(...)`` daje coś w rodzaju parametryzacji w jednym teście,
* metoda ``tearDown`` sprząta po teście (odpowiednik części po ``yield``).

Klasę ``TestCase`` potrafi uruchomić także ``pytest`` - nie musisz wybierać
jednego frameworka „na zawsze”.
"""

from __future__ import annotations

import unittest

from calculator import Calculator, parse_number


class TestCalculatorArithmetic(unittest.TestCase):
    """Podstawowe działania - jedna asercja na jeden test."""

    def setUp(self) -> None:
        """Świeży kalkulator przed każdym testem (izolacja!)."""
        self.calc = Calculator()

    def test_add_returns_sum(self) -> None:
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_subtract_returns_difference(self) -> None:
        self.assertEqual(self.calc.subtract(10, 4), 6)

    def test_multiply_returns_product(self) -> None:
        self.assertEqual(self.calc.multiply(6, 7), 42)

    def test_divide_returns_quotient(self) -> None:
        self.assertEqual(self.calc.divide(10, 4), 2.5)

    def test_divide_by_zero_raises_zero_division_error(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(1, 0)

    def test_divide_by_zero_message_explains_the_reason(self) -> None:
        with self.assertRaisesRegex(ZeroDivisionError, "division by zero"):
            self.calc.divide(1, 0)

    def test_division_result_may_be_inexact(self) -> None:
        # assertAlmostEqual to odpowiednik `pytest.approx`
        self.assertAlmostEqual(self.calc.divide(1, 3), 0.3333333333, places=6)


class TestCalculatorAverage(unittest.TestCase):
    """Średnia: przypadki poprawne i brzegowe."""

    def setUp(self) -> None:
        self.calc = Calculator()

    def test_average_of_single_value_is_that_value(self) -> None:
        self.assertEqual(self.calc.average([5]), 5)

    def test_average_of_multiple_values(self) -> None:
        self.assertEqual(self.calc.average([1, 2, 3, 4]), 2.5)

    def test_average_of_empty_sequence_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            self.calc.average([])

    def test_average_accepts_tuple_and_list(self) -> None:
        """`subTest` pozwala sprawdzić kilka danych bez kopiowania testu."""
        for values in ([1, 2, 3], (3, 3, 3), [0]):
            with self.subTest(values=values):
                self.assertAlmostEqual(self.calc.average(values), sum(values) / len(values))


class TestParseNumber(unittest.TestCase):
    """Funkcja pomocnicza - testy czystej funkcji."""

    def test_parses_plain_integer(self) -> None:
        self.assertEqual(parse_number("42"), 42.0)

    def test_parses_comma_as_decimal_separator(self) -> None:
        self.assertEqual(parse_number("3,5"), 3.5)

    def test_parses_whitespace_surrounded_value(self) -> None:
        self.assertEqual(parse_number("  7.25  "), 7.25)

    def test_rejects_non_numeric_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot parse number"):
            parse_number("abc")

    def test_rejects_non_string_input(self) -> None:
        with self.assertRaises(TypeError):
            parse_number(42)  # type: ignore[arg-type]


class TestCalculatorLifecycle(unittest.TestCase):
    """Przykład ``setUpClass`` / ``tearDownClass`` - przygotowanie raz na klasę.

    W klasie ``log`` zapisujemy wywołania metod cyklu życia, żeby zobaczyć
    kolejność: ``setUpClass`` -> ``setUp`` -> test -> ``tearDown`` ->
    (kolejny ``setUp`` -> test...) -> ``tearDownClass``.
    """

    log: list[str] = []

    @classmethod
    def setUpClass(cls) -> None:
        # Wykonuje się RAZ, przed wszystkimi testami w klasie.
        cls.shared = Calculator()
        cls.log = ["setUpClass"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.log.append("tearDownClass")

    def setUp(self) -> None:
        # Wykonuje się przed KAŻDYM testem w klasie (także po setUpClass).
        type(self).log.append("setUp")

    def test_shared_instance_works(self) -> None:
        self.assertEqual(self.shared.add(1, 1), 2)

    def test_setup_class_ran_before_every_test(self) -> None:
        self.assertEqual(self.log[0], "setUpClass")

    def test_setup_ran_before_this_test(self) -> None:
        self.assertIn("setUp", self.log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
