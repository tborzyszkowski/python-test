from string_calculator import NegativeNumberError, add


def calculator_total(expression: str) -> int:
    return add(expression)


__all__ = ["NegativeNumberError", "add", "calculator_total"]
