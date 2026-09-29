Feature: Lot ekonomiczny
  Aby zarządzać listą pasażerów
  Jako operator lotu
  Chcę stosować reguły lotu ekonomicznego

  Scenario: Dodanie zwykłego pasażera
    Given istnieje lot ekonomiczny o numerze "EC100"
    And istnieje standardowy pasażer "Alice"
    When dodaję pasażera "Alice" do lotu
    Then pasażer "Alice" jest na locie

  Scenario: Usunięcie zwykłego pasażera
    Given istnieje lot ekonomiczny o numerze "EC101"
    And istnieje standardowy pasażer "Bob"
    And pasażer "Bob" jest na locie
    When usuwam pasażera "Bob" z lotu
    Then pasażer "Bob" nie jest na locie

  Scenario: VIP nie może zostać usunięty z lotu ekonomicznego
    Given istnieje lot ekonomiczny o numerze "EC102"
    And istnieje pasażer VIP "Victor"
    And pasażer "Victor" jest na locie
    When usuwam pasażera "Victor" z lotu
    Then operacja jest odrzucona komunikatem "VIP passengers cannot be removed"

  Scenario: Ten sam pasażer nie może zostać dodany ponownie
    Given istnieje lot ekonomiczny o numerze "EC103"
    And istnieje standardowy pasażer "Alice"
    And pasażer "Alice" jest na locie
    When ponownie dodaję pasażera "Alice" do lotu
    Then operacja jest odrzucona komunikatem "passenger already on flight"
