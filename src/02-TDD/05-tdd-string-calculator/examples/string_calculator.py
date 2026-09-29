"""String Calculator - finalny kod po iteracjach TDD."""

from __future__ import annotations

import re


class NegativeNumberError(ValueError):
    """Co najmniej jedna liczba ujemna wystapila w wyrazeniu."""

    def __init__(self, numbers: list[int]) -> None:
        self.numbers = numbers
        super().__init__(f"negative numbers are not allowed: {numbers}")


def add(numbers: str) -> int:
    """Sumuje liczby rozdzielone przecinkiem lub nowa linia."""
    if not numbers:
        return 0
    values = [int(value.strip()) for value in re.split(r",|\n", numbers)]
    negatives = [value for value in values if value < 0]
    if negatives:
        raise NegativeNumberError(negatives)
    return sum(values)


def main() -> None:
    for expression in ("", "7", "1,2", "1,2,3\n4"):
        print(f"add({expression!r}) = {add(expression)}")
    try:
        add("1,-2,-3")
    except NegativeNumberError as exc:
        print(f"ujemne: {exc.numbers}")


if __name__ == "__main__":
    main()
