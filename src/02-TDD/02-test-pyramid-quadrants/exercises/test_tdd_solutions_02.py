from __future__ import annotations

import pytest
from tdd_solutions_02 import build_service


def test_solution_exposes_business_rule():
    assert build_service().price_for("book", 2) == 10_000


def test_solution_rejects_non_positive_quantity():
    with pytest.raises(ValueError, match="positive"):
        build_service().price_for("book", 0)
