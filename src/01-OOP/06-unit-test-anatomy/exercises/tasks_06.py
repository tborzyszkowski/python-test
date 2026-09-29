"""Zadania do samodzielnego wykonania - temat 06 (anatomia testu jednostkowego).

Kod produkcyjny znowu dostajesz gotowy - testujemy klasy z poprzednich tematów:

* ``solutions_03.Car`` / ``solutions_03.Engine`` - zachowanie metody ``drive``,
* ``solutions_01.Ammo`` - walidacja, licznik klasowy (izolacja!),
* ``solutions_04.ToolKit`` / ``Hammer`` - testy kontraktu i agregacji.

Wzorcowe rozwiązanie: ``test_solutions_06.py``::

    python -m pytest src/01-OOP/06-unit-test-anatomy/exercises/test_solutions_06.py -v

Twoje testy napisz w pliku ``exercises/test_moje_06.py``.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# ZAKRES ZADAŃ
# --------------------------------------------------------------------------- #
# Zadanie 1 (3 pkt) - metoda ``Car.drive``: jedna własność na test
#   Napisz testy sprawdzające kolejno:
#     a) ``drive`` zużywa paliwo zgodnie ze zużyciem silnika
#        (100 km przy 5.5 l/100 km -> 5.5 l mniej),
#     b) ``drive`` zwraca aktualny poziom paliwa,
#     c) ``drive`` z dystansem dłuższym niż zasięg podnosi ``ValueError``
#        i **nie zmienia** poziomu paliwa,
#     d) ``drive`` odrzuca dystans 0 i ujemny,
#     e) po ``drive`` zasięg (``range_km``) jest liczony od nowego poziomu.
#   Każdy podpunkt = osobny test z nazwą w formacie
#   ``test_<jednostka>_<warunek>_<oczekiwanie>``.
#
# Zadanie 2 (2 pkt) - izolacja stanu klasowego ``Ammo.total_created``
#   Napisz trzy testy licznika (stan początkowy, zliczanie, brak „przecieku”
#   z poprzedniego testu) i zadbaj o izolację. Wybierz jedno z rozwiązań:
#     * fixture ``autouse=True`` zerująca licznik (zalecane),
#     * ``Ammo.reset_counter()`` wywołane w każdym teście.
#   Uzasadnij wybór w komentarzu ``# WYBÓR:``.
#
# Zadanie 3 (2 pkt) - test własności (property test)
#   Dla ``Hammer.nail(target, count)`` napisz test, który sprawdza **własność**
#   dla wielu danych wejściowych (``parametrize``):
#     * liczba zwróconych efektów == ``count``,
#     * ``hammer.uses`` rośnie dokładnie o ``count``,
#     * wytrzymałość maleje o ``count * wear_per_use``, ale nie poniżej zera.
#   Uwaga: dla dużych ``count`` narzędzie może się zepsuć - zaplanuj dane tak,
#   aby test dotyczył jednej własności (albo dodaj osobny test na zepsucie).
#
# Zadanie 4 (2 pkt) - determinizm
#   Weź funkcję ``config_reader.new_session_id`` z ``examples/config_reader.py``
#   i napisz dla niej testy:
#     * długość identyfikatora,
#     * dozwolony zbiór znaków,
#     * determinizm po ``monkeypatch.setattr(random, "choices", ...)``.
#   Podpowiedź: ``monkeypatch.setattr(random, "choices", lambda alphabet, k: ["a"] * k)``.
#
# --------------------------------------------------------------------------- #
# PRZYKŁADY TESTÓW DO POPRAWY (napisz ich wersje zgodne z zasadami)
# --------------------------------------------------------------------------- #
#
# ❌ 1. Nazwa bez informacji + trzy własności naraz:
#
#     def test_car():
#         car = Car("Skoda", Engine(110, 5.5))
#         car.drive(100)
#         assert car.fuel_l == 44.5
#         assert car.range_km > 0
#         assert car.fuel_l < car.tank_l
#
# ❌ 2. Stan współdzielony między testami:
#
#     car = Car("Skoda", Engine(110, 5.5))        # obiekt na poziomie modułu!
#
#     def test_drive_a():
#         car.drive(100)
#         assert car.fuel_l == 44.5
#
#     def test_drive_b():
#         car.drive(100)                          # zależy od tego, czy był test A
#         assert car.fuel_l == 44.5
#
# ❌ 3. Test zależny od czasu/losowości:
#
#     def test_session_id():
#         assert new_session_id() == new_session_id()   # ❌ losowe != losowe
#
# ❌ 4. Test „przechodzi zawsze”:
#
#     def test_drive():
#         car = Car("Skoda", Engine(110, 5.5))
#         car.drive(100)
#         assert car.fuel_l is not None                 # ❌ asercja bez treści
#
# ❌ 5. Test zaglądający do wnętrza obiektu:
#
#     def test_drive():
#         car = Car("Skoda", Engine(110, 5.5))
#         car.drive(100)
#         assert car._fuel_l == 44.5                    # ❌ pole prywatne
