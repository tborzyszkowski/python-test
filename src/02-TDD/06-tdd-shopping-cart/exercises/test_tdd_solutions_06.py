import pytest
from tdd_solutions_06 import build_books_cart, total_with_three_for_two


def test_solution_builds_cart():
    assert build_books_cart(2).subtotal_cents() == 10_000


def test_solution_three_for_two():
    assert total_with_three_for_two(3) == 10_000


def test_solution_rejects_invalid_quantity():
    with pytest.raises(ValueError, match="positive"):
        build_books_cart(0)
