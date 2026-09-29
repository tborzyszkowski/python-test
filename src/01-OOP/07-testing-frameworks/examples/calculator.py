"""Kod produkcyjny do porównania frameworków ``unittest`` i ``pytest``.

Ten sam kod testują dwa pliki:

* ``test_unittest_calculator.py`` - styl ``unittest.TestCase``,
* ``test_pytest_calculator.py`` - styl ``pytest`` (funkcje + `assert`).

Uruchomienie::

    python src/01-OOP/07-testing-frameworks/examples/calculator.py
"""

from __future__ import annotations

from collections.abc import Sequence


class Calculator:
    """Prosty kalkulator: cztery działania i średnia."""

    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Dzieli ``a`` przez ``b``; dla ``b == 0`` podnosi ``ZeroDivisionError``."""
        if b == 0:
            raise ZeroDivisionError("division by zero is not allowed")
        return a / b

    def average(self, values: Sequence[float]) -> float:
        """Średnia arytmetyczna; pusta sekwencja -> ``ValueError``."""
        if not values:
            raise ValueError("cannot average an empty sequence")
        return sum(values) / len(values)

    def __repr__(self) -> str:
        return "Calculator()"


def parse_number(text: str) -> float:
    """Zamienia napis na liczbę, akceptując przecinek dziesiętny.

    ``"3,5"`` -> ``3.5``; dla napisów nieliczbowych podnosi ``ValueError``.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    try:
        return float(text.replace(",", ".").strip())
    except ValueError as exc:
        raise ValueError(f"cannot parse number: {text!r}") from exc


def main() -> None:
    calc = Calculator()
    print(f"add(2, 3)            -> {calc.add(2, 3)}")
    print(f"divide(1, 3)         -> {calc.divide(1, 3)}")
    print(f"average([1, 2, 3, 4])-> {calc.average([1, 2, 3, 4])}")
    print(f"parse_number('3,5')  -> {parse_number('3,5')}")


if __name__ == "__main__":
    main()
