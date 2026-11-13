@premium
Feature: Lot premium
  Aby chronić ofertę premium
  Jako operator lotu
  Chcę wpuszczać wyłącznie pasażerów VIP

  Scenario: Pasażer VIP może zostać dodany do lotu premium
    Given istnieje lot premium o numerze "PR100"
    And istnieje pasażer VIP "Victor"
    When dodaję pasażera "Victor" do lotu
    Then pasażer "Victor" jest na locie

  Scenario: Standardowy pasażer nie może zostać dodany do lotu premium
    Given istnieje lot premium o numerze "PR101"
    And istnieje standardowy pasażer "Alice"
    When dodaję pasażera "Alice" do lotu
    Then operacja jest odrzucona komunikatem "only VIP passengers"

  Scenario: Ten sam VIP nie może zostać dodany ponownie do lotu premium
    Given istnieje lot premium o numerze "PR102"
    And istnieje pasażer VIP "Victor"
    And pasażer "Victor" jest na locie
    When ponownie dodaję pasażera "Victor" do lotu
    Then operacja jest odrzucona komunikatem "passenger already on flight"
