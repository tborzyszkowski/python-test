"""Testy przykładowych rozwiązań zadań Gherkina."""

from bdd_solutions_02 import (
    ECONOMY_FEATURE,
    IMPLEMENTATION_DETAIL_AFTER,
    IMPLEMENTATION_DETAIL_BEFORE,
    NEGATIVE_SCENARIO,
    STATUS_ACCESS_OUTLINE,
)


def test_economy_solution_has_business_feature_and_observable_result():
    assert "Feature:" in ECONOMY_FEATURE
    assert "operator dodaje" in ECONOMY_FEATURE
    assert "widoczny na liście" in ECONOMY_FEATURE
    assert "add_passenger" not in ECONOMY_FEATURE


def test_outline_has_three_examples_for_one_rule():
    assert "Scenario Outline:" in STATUS_ACCESS_OUTLINE
    assert STATUS_ACCESS_OUTLINE.count("|") >= 8
    assert "| VIP" in STATUS_ACCESS_OUTLINE
    assert "| STANDARD" in STATUS_ACCESS_OUTLINE
    assert "| STUDENT" in STATUS_ACCESS_OUTLINE


def test_refactoring_removes_implementation_details():
    assert "add_passenger" in IMPLEMENTATION_DETAIL_BEFORE
    assert "_passengers" in IMPLEMENTATION_DETAIL_BEFORE
    assert "add_passenger" not in IMPLEMENTATION_DETAIL_AFTER
    assert "_passengers" not in IMPLEMENTATION_DETAIL_AFTER
    assert "widoczny na liście" in IMPLEMENTATION_DETAIL_AFTER


def test_negative_scenario_contains_error_contract():
    assert "operacja zostaje odrzucona" in NEGATIVE_SCENARIO
    assert "only VIP passengers" in NEGATIVE_SCENARIO
    assert "nie jest na liście" in NEGATIVE_SCENARIO
