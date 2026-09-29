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
