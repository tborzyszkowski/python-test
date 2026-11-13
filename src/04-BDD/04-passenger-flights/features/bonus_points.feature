Feature: Punkty promocyjne
  Aby nagradzać lojalnych pasażerów
  Jako system lojalnościowy
  Chcę naliczać punkty według statusu pasażera

  Scenario Outline: Punkty zależą od statusu pasażera
    Given pasażer "<name>" ma status "<status>"
    And przebieg lotu wynosi <mileage> kilometrów
    When naliczam punkty dla pasażera "<name>"
    Then pasażer otrzymuje <points> punktów

    Examples:
      | name  | status   | mileage | points |
      | Alice | STANDARD | 1000    | 50     |
      | Victor| VIP      | 1000    | 100    |
      | Eve   | VIP      | 975     | 97     |
      | Sara  | STUDENT  | 1000    | 66     |
