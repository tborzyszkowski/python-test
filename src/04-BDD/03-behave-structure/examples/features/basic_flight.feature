@structure
Feature: Podstawowa struktura scenariusza
  Scenariusz pokazuje przepływ Given, When, Then i dane w context

  Scenario: Operator dodaje pasażera do lotu
    Given istnieje lot "EC-DEMO" z 2 miejscami
    And pasażer "Alice" ma status "STANDARD"
    When operator dodaje pasażera "Alice" do lotu
    Then lot ma 1 pasażera
    And pasażer "Alice" jest na liście

  Scenario: Operator widzi błąd dla pełnego lotu
    Given istnieje lot "EC-FULL" z 1 miejscem
    And pasażer "Alice" ma status "STANDARD"
    And operator dodał pasażera "Alice" do lotu
    And pasażer "Bob" ma status "STANDARD"
    When operator dodaje pasażera "Bob" do lotu
    Then operacja kończy się błędem "flight is full"
