import pytest
from tdd_solutions_05 import NegativeNumberError, calculator_total


def test_solution_calculates_newline_expression():
    assert calculator_total("1,2\n3") == 6


def test_solution_reports_all_negatives():
    with pytest.raises(NegativeNumberError) as error:
        calculator_total("-1,2,-4")
    assert error.value.numbers == [-1, -4]
