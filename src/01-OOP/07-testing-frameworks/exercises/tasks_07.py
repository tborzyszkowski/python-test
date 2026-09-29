"""Zadania do samodzielnego wykonania - temat 07 (porównanie frameworków).

Testowany kod: ``string_utils.py`` (``normalize``, ``word_count``, ``slugify``,
``truncate``).

Wzorcowe rozwiązanie - **obie wersje w jednym pliku**:
``test_solutions_07.py``::

    python -m pytest src/01-OOP/07-testing-frameworks/exercises/test_solutions_07.py -v
    python -m unittest discover -s src/01-OOP/07-testing-frameworks/exercises -p "test_string_*" -v

Twoje testy napisz w plikach ``exercises/test_moje_unittest_07.py`` oraz
``exercises/test_moje_pytest_07.py``.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# ZAKRES ZADAŃ
# --------------------------------------------------------------------------- #
# Zadanie 1 (3 pkt) - wersja ``unittest``
#   Napisz klasę ``TestStringUtils(unittest.TestCase)`` pokrywającą:
#     * ``normalize``: wielokrotne spacje, tabulatory i spacje na końcach,
#       pusty napis, ``TypeError`` dla ``None``;
#     * ``word_count``: pusty napis -> 0, napis z samych spacji -> 0,
#       zwykłe zdanie -> liczba słów;
#     * ``slugify``: polskie znaki diakrytyczne, interpunkcja, spacje;
#     * ``truncate``: tekst krótszy niż limit bez zmian, dłuższy przycięty
#       z ``...``, ``ValueError`` dla ``limit < 4``.
#   Wymagania techniczne:
#     * przygotowanie w ``setUp``, jeśli potrzebne,
#     * użyj ``assertEqual``, ``assertRaisesRegex`` i ``subTest`` (dla slugify),
#     * każdy test ma jedną asercję sprawdzającą jedną własność.
#
# Zadanie 2 (3 pkt) - wersja ``pytest``
#   Napisz testy funkcyjne dla tego samego kodu:
#     * dane w ``@pytest.mark.parametrize`` (jeden test = jedna własność),
#     * ``pytest.raises(..., match=...)`` dla błędów,
#     * ``assert is True`` / ``is False`` tam, gdzie to sensowne,
#     * dopisz test na ``slugify("") == ""`` (przypadek brzegowy!).
#
# Zadanie 3 (2 pkt) - porównanie
#   W komentarzu ``# WNIOSKI:`` (4-6 punktów) porównaj obie wersje pod kątem:
#     * liczby linii kodu,
#     * czytelności komunikatu porażki (uruchom celowo zepsuty test!),
#     * łatwości dodania nowego przypadku,
#     * wsparcia edytora (podpowiedzi, breakpointy, *Test Explorer*),
#     * kosztu migracji istniejącego zestawu testów.
#
# Zadanie 4 (2 pkt, dla chętnych) - interakcja frameworków
#   Sprawdź eksperymentalnie i opisz (2-3 zdania) w komentarzu
#   ``# EKSPERYMENT:``:
#     * czy ``python -m unittest`` uruchomi twoje testy w stylu pytest?
#     * czy ``pytest`` uruchomi twoje testy ``unittest.TestCase``?
#     * która konwencja nazw plików (``test*.py`` vs ``test_*.py``) pasuje obu?
#
# --------------------------------------------------------------------------- #
# ŚCIĄGAWKA
# --------------------------------------------------------------------------- #
# | Zadanie                     | unittest                          | pytest                         |
# |-----------------------------|-----------------------------------|--------------------------------|
# | równość                     | self.assertEqual(a, b)            | assert a == b                  |
# | porównanie float            | self.assertAlmostEqual(a, b, 6)   | pytest.approx                  |
# | prawda / fałsz              | assertTrue / assertFalse          | assert x is True               |
# | wyjątek                     | assertRaises(T)                   | pytest.raises(T)               |
# | wyjątek + komunikat         | assertRaisesRegex(T, "text")      | pytest.raises(T, match="text") |
# | kilka danych                | with self.subTest(...)            | @pytest.mark.parametrize       |
# | przygotowanie               | setUp / setUpClass                | @pytest.fixture                |
# | sprzątanie                  | tearDown / tearDownClass          | fixture z yield                |
# | pominięcie testu            | @unittest.skip("powód")           | @pytest.mark.skip("powód")     |
# | test oczekiwany jako porażka| @unittest.expectedFailure         | @pytest.mark.xfail             |
# | uruchomienie                | python -m unittest discover       | python -m pytest               |
