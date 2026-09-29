import pytest
from tdd_solutions_04 import discount_for_total


def test_solution_uses_business_rule():
    assert discount_for_total(9999) == 999


def test_solution_is_self_validating_on_bad_input():
    with pytest.raises(ValueError, match="non-negative"):
        discount_for_total(-1)
