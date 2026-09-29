from __future__ import annotations

import pytest
from string_calculator import NegativeNumberError, add


def test_empty_string_returns_zero():
    assert add("") == 0


def test_single_number_returns_value():
    assert add("7") == 7


def test_two_numbers_are_summed():
    assert add("1,2") == 3


def test_any_number_of_values_is_supported():
    assert add("1,2,3,4") == 10


def test_newline_is_a_separator():
    assert add("1,2\n3") == 6


def test_whitespace_around_numbers_is_ignored():
    assert add(" 1, 2 \n 3 ") == 6


def test_all_negative_numbers_are_reported():
    with pytest.raises(NegativeNumberError, match="-2.*-3") as error:
        add("1,-2,-3")

    assert error.value.numbers == [-2, -3]
