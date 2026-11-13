"""Przykładowe rozwiązania zadań do tematu BDD i Outside-In."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptanceCriterion:
    """Jedno kryterium akceptacji zapisane językiem zachowania."""

    given: str
    when: str
    then: str


PREMIUM_FLIGHT_STORY = (
    "Jako operator chcę dopuścić do lotu premium wyłącznie pasażerów VIP, "
    "aby oferta premium była dostępna tylko dla uprawnionych osób."
)

PREMIUM_FLIGHT_CRITERIA = (
    AcceptanceCriterion(
        given="lot premium ma wolne miejsce",
        when="operator dodaje pasażera VIP",
        then="pasażer zostaje dodany do lotu",
    ),
    AcceptanceCriterion(
        given="lot premium ma wolne miejsce",
        when="operator dodaje pasażera standardowego",
        then="system odrzuca operację i nie zmienia listy pasażerów",
    ),
    AcceptanceCriterion(
        given="lot premium jest pełny",
        when="operator dodaje pasażera VIP",
        then="system odrzuca operację z powodu braku miejsca",
    ),
)


@dataclass(frozen=True)
class ThreeAmigosQuestions:
    """Pytania, które każda rola wnosi do rozmowy o przykładzie."""

    customer: str
    business_analyst: str
    developer: str
    tester: str


THREE_AMIGOS = ThreeAmigosQuestions(
    customer="Jaka wartość biznesowa uzasadnia ograniczenie lotu premium do VIP?",
    business_analyst=(
        "Czy VIP oznacza wyłącznie status pasażera i jakie są reguły braku miejsc?"
    ),
    developer="Czy odrzucenie ma być komunikatem dla operatora, a lista pasażerów ma pozostać bez zmian?",
    tester="Co powinno się stać dla standardowego pasażera, duplikatu i pełnego lotu?",
)

BUSINESS_VALUE_STATEMENTS = (
    "Pasażerowie mogą bezpiecznie i przejrzyście zarządzać podróżą.",
    "Oferta premium jest dostępna tylko dla uprawnionych pasażerów VIP.",
)

IMPLEMENTATION_STATEMENTS = (
    "Klasa PremiumFlight wywołuje metodę add_passenger.",
    "Status VIP jest przechowywany w polu vip obiektu Passenger.",
)

DUPLICATE_PASSENGER_SCENARIO = """\
Feature: Ochrona listy pasażerów przed duplikatami

  Scenario: Operator nie dodaje tego samego pasażera dwa razy do lotu premium
    Given lot premium "PR-100" ma pasażera VIP "Alice"
    When operator próbuje dodać pasażera VIP "Alice" ponownie
    Then system odrzuca operację jako duplikat
    And lot nadal ma dokładnie jednego pasażera "Alice"
"""


def all_solutions() -> dict[str, object]:
    """Zwraca rozwiązania w formie wygodnej do omówienia albo inspekcji."""
    return {
        "story": PREMIUM_FLIGHT_STORY,
        "acceptance_criteria": PREMIUM_FLIGHT_CRITERIA,
        "three_amigos": THREE_AMIGOS,
        "business_value": BUSINESS_VALUE_STATEMENTS,
        "implementation_details": IMPLEMENTATION_STATEMENTS,
        "duplicate_passenger_scenario": DUPLICATE_PASSENGER_SCENARIO,
    }


if __name__ == "__main__":
    for key, value in all_solutions().items():
        print(f"\n{key}:\n{value}")
