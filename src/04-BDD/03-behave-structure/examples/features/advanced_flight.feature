@structure
Feature: Parametry i tabela danych

  Scenario Outline: Punkty zależą od statusu pasażera
    Given istnieje lot "<flight>" z 3 miejscami i przebiegiem <mileage> km
    And pasażer "Alex" ma status "<status>"
    When obliczam punkty dla pasażera "Alex"
    Then pasażer otrzymuje <points> punktów

    Examples:
      | flight | mileage | status   | points |
      | EC-101 | 1000    | STANDARD | 100    |
      | EC-102 | 1000    | VIP      | 200    |

  Scenario: Dane wielu pasażerów trafiają do context table
    Given istnieje lot "EC-TABLE" z 3 miejscami
    And lot ma następujących pasażerów:
      | name  | status   |
      | Alice | STANDARD |
      | Victor| VIP      |
    When operator dodaje pasażera "Alice" do lotu
    Then lot ma 1 pasażera
    And pasażer "Alice" jest na liście
