"""Testy przykładowych rozwiązań zadań BDD."""

from bdd_solutions_01 import (
    BUSINESS_VALUE_STATEMENTS,
    DUPLICATE_PASSENGER_SCENARIO,
    IMPLEMENTATION_STATEMENTS,
    PREMIUM_FLIGHT_CRITERIA,
    PREMIUM_FLIGHT_STORY,
    THREE_AMIGOS,
)


def test_story_describes_actor_goal_and_reason():
    assert PREMIUM_FLIGHT_STORY.startswith("Jako operator")
    assert "aby" in PREMIUM_FLIGHT_STORY


def test_acceptance_criteria_cover_success_and_two_rejections():
    assert len(PREMIUM_FLIGHT_CRITERIA) == 3
    assert PREMIUM_FLIGHT_CRITERIA[0].then == "pasażer zostaje dodany do lotu"
    assert "odrzuca" in PREMIUM_FLIGHT_CRITERIA[1].then
    assert "braku miejsca" in PREMIUM_FLIGHT_CRITERIA[2].then


def test_three_amigos_questions_are_role_specific():
    assert "wartość biznesowa" in THREE_AMIGOS.customer
    assert "reguły" in THREE_AMIGOS.business_analyst
    assert "komunikatem" in THREE_AMIGOS.developer
    assert "duplikatu" in THREE_AMIGOS.tester


def test_business_value_is_separate_from_implementation():
    assert all("klasa" not in statement.lower() for statement in BUSINESS_VALUE_STATEMENTS)
    assert any("klasa" in statement.lower() for statement in IMPLEMENTATION_STATEMENTS)


def test_duplicate_scenario_uses_business_language_and_expected_outcome():
    assert "Scenario:" in DUPLICATE_PASSENGER_SCENARIO
    assert "ponownie" in DUPLICATE_PASSENGER_SCENARIO
    assert "dokładnie jednego" in DUPLICATE_PASSENGER_SCENARIO
