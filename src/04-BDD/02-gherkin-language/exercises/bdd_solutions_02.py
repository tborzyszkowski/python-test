"""Przykładowe rozwiązania zadań z tematu Język Gherkin."""

from __future__ import annotations


ECONOMY_FEATURE = """\
Feature: Dodawanie pasażerów do lotu ekonomicznego
  Aby sprawnie zarządzać zwykłymi rejsami
  Jako operator lotu
  Chcę dodawać pasażerów do lotu ekonomicznego

  Scenario: Standardowy pasażer zostaje dodany do lotu ekonomicznego
    Given lot ekonomiczny "EC100" ma wolne miejsce
    And pasażer "Alice" ma status "STANDARD"
    When operator dodaje pasażera "Alice" do lotu
    Then pasażer "Alice" jest widoczny na liście lotu
"""

STATUS_ACCESS_OUTLINE = """\
Scenario Outline: Status pasażera określa dostęp do lotu premium
  Given lot premium "PR100" ma wolne miejsce
  And pasażer "Alex" ma status "<status>"
  When operator dodaje pasażera "Alex" do lotu
  Then operacja jest "<result>"

  Examples:
    | status   | result       |
    | VIP      | zaakceptowana |
    | STANDARD | odrzucona     |
    | STUDENT  | odrzucona     |
"""

IMPLEMENTATION_DETAIL_BEFORE = """\
Scenario: Pasażer zostaje dodany
  Given lot ekonomiczny "EC100" istnieje
  When wywołuję metodę add_passenger z obiektem Passenger
  Then pole _passengers ma długość 1
"""

IMPLEMENTATION_DETAIL_AFTER = """\
Scenario: Pasażer zostaje dodany
  Given lot ekonomiczny "EC100" ma wolne miejsce
  And pasażer "Alice" ma status "STANDARD"
  When operator dodaje pasażera "Alice" do lotu
  Then pasażer "Alice" jest widoczny na liście lotu
"""

NEGATIVE_SCENARIO = """\
Scenario: Standardowy pasażer nie zostaje dodany do lotu premium
  Given lot premium "PR200" ma wolne miejsce
  And pasażer "Bob" ma status "STANDARD"
  When operator dodaje pasażera "Bob" do lotu
  Then operacja zostaje odrzucona
  And operator widzi komunikat "only VIP passengers"
  And pasażer "Bob" nie jest na liście lotu
"""


def all_solutions() -> dict[str, str]:
    """Zwraca wszystkie rozwiązania do omówienia albo zapisania do plików."""
    return {
        "economy_feature": ECONOMY_FEATURE,
        "scenario_outline": STATUS_ACCESS_OUTLINE,
        "implementation_detail_before": IMPLEMENTATION_DETAIL_BEFORE,
        "implementation_detail_after": IMPLEMENTATION_DETAIL_AFTER,
        "negative_scenario": NEGATIVE_SCENARIO,
    }


if __name__ == "__main__":
    for name, specification in all_solutions().items():
        print(f"\n### {name}\n{specification}")
