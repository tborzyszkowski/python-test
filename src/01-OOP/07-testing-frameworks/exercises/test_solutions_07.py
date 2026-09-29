"""Wzorcowe rozwiązanie tematu 07 - **ten sam zestaw testów w dwóch frameworkach**.

Uruchomienie obu wersji naraz::

    python -m pytest src/01-OOP/07-testing-frameworks/exercises/test_solutions_07.py -v

Tylko klasy ``unittest``::

    python -m unittest discover -s src/01-OOP/07-testing-frameworks/exercises -p "test_solutions_07.py" -v

Plik jest celowo podzielony na dwie części:

* **Część A** - ``unittest.TestCase`` (klasy i metody, ``assertXxx``, ``subTest``),
* **Część B** - ``pytest`` (funkcje, ``assert``, ``parametrize``, fixture'y).

Obie części testują dokładnie to samo, dzięki czemu różnice widać „na żywo”
w jednym raporcie. To również dowód interoperacyjności: ``pytest`` uruchamia
część A bez żadnych zmian.
"""

from __future__ import annotations

import unittest

import pytest
from string_utils import normalize, slugify, truncate, word_count

# =========================================================================== #
# CZĘŚĆ A - WERSJA unittest
# =========================================================================== #


class TestNormalizeUnittest(unittest.TestCase):
    """``normalize`` - spacje, tabulatory, przypadki brzegowe."""

    def test_collapses_multiple_spaces(self) -> None:
        self.assertEqual(normalize("Ala    ma   kota"), "Ala ma kota")

    def test_collapses_tabs_and_newlines(self) -> None:
        self.assertEqual(normalize("Ala\tma\nkota"), "Ala ma kota")

    def test_strips_leading_and_trailing_whitespace(self) -> None:
        self.assertEqual(normalize("   Ala ma kota   "), "Ala ma kota")

    def test_empty_string_stays_empty(self) -> None:
        self.assertEqual(normalize(""), "")

    def test_whitespace_only_string_becomes_empty(self) -> None:
        self.assertEqual(normalize(" \t\n "), "")

    def test_non_string_input_raises_type_error(self) -> None:
        with self.assertRaisesRegex(TypeError, "expected str"):
            normalize(None)  # type: ignore[arg-type]


class TestWordCountUnittest(unittest.TestCase):
    """``word_count`` - liczba słów po normalizacji."""

    def test_empty_string_has_zero_words(self) -> None:
        self.assertEqual(word_count(""), 0)

    def test_whitespace_only_has_zero_words(self) -> None:
        self.assertEqual(word_count("   \t  "), 0)

    def test_single_word(self) -> None:
        self.assertEqual(word_count("Ala"), 1)

    def test_sentence_with_repeated_spaces(self) -> None:
        self.assertEqual(word_count("Ala   ma \t kota"), 3)


class TestSlugifyUnittest(unittest.TestCase):
    """``slugify`` - diakrytyki, interpunkcja, ``subTest`` jako parametryzacja."""

    def test_transliterates_polish_diacritics(self) -> None:
        self.assertEqual(slugify("Zażółć gęślą jaźń"), "zazolc-gesla-jazn")

    def test_replaces_punctuation_with_single_dash(self) -> None:
        self.assertEqual(slugify("Hello,   World!!!"), "hello-world")

    def test_removes_leading_and_trailing_dashes(self) -> None:
        self.assertEqual(slugify("  --Hello--  "), "hello")

    def test_empty_string_stays_empty(self) -> None:
        self.assertEqual(slugify(""), "")

    def test_multiple_cases_with_subtest(self) -> None:
        cases = {
            "Wielki Test": "wielki-test",
            "Łódź": "lodz",
            "Kraków 2026": "krakow-2026",
            "a---b": "a-b",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(slugify(text), expected)


class TestTruncateUnittest(unittest.TestCase):
    """``truncate`` - przycinanie i walidacja limitu."""

    def test_shorter_text_is_returned_unchanged(self) -> None:
        self.assertEqual(truncate("abc", 10), "abc")

    def test_text_of_exactly_limit_length_is_unchanged(self) -> None:
        self.assertEqual(truncate("abcd", 4), "abcd")

    def test_longer_text_is_truncated_with_ellipsis(self) -> None:
        result = truncate("abcdefgh", 5)
        self.assertEqual(result, "ab...")
        self.assertEqual(len(result), 5)

    def test_limit_below_four_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 4"):
            truncate("abcdefgh", 3)

    def test_limit_of_four_is_allowed(self) -> None:
        self.assertEqual(truncate("abcdefgh", 4), "a...")


# =========================================================================== #
# CZĘŚĆ B - WERSJA pytest
# =========================================================================== #


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Ala    ma   kota", "Ala ma kota"),
        ("Ala\tma\nkota", "Ala ma kota"),
        ("   Ala ma kota   ", "Ala ma kota"),
        ("", ""),
        (" \t\n ", ""),
    ],
)
def test_normalize_collapses_and_strips(text, expected):
    assert normalize(text) == expected


def test_normalize_rejects_non_string():
    with pytest.raises(TypeError, match="expected str"):
        normalize(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("", 0), ("   \t  ", 0), ("Ala", 1), ("Ala   ma \t kota", 3)],
)
def test_word_count(text, expected):
    assert word_count(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Zażółć gęślą jaźń", "zazolc-gesla-jazn"),
        ("Hello,   World!!!", "hello-world"),
        ("  --Hello--  ", "hello"),
        ("Wielki Test", "wielki-test"),
        ("Łódź", "lodz"),
        ("Kraków 2026", "krakow-2026"),
        ("a---b", "a-b"),
        ("", ""),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


def test_slugify_output_never_contains_spaces():
    """Własność: slug nigdy nie zawiera spacji ani wiodących myślników."""
    for text in ["  Ala ma kota  ", "Zażółć gęślą jaźń", "!!!", "a b c"]:
        result = slugify(text)
        assert " " not in result
        assert not result.startswith("-")
        assert not result.endswith("-")


def test_truncate_keeps_short_text_intact():
    assert truncate("abc", 10) == "abc"


def test_truncate_respects_limit_for_long_text():
    result = truncate("abcdefgh", 5)
    assert result == "ab..."
    assert len(result) == 5


@pytest.mark.parametrize("limit", [0, 1, 3, -5])
def test_truncate_rejects_too_small_limit(limit):
    with pytest.raises(ValueError, match="at least 4"):
        truncate("abcdefgh", limit)


# =========================================================================== #
# WNIOSKI (Zadanie 3)
# =========================================================================== #
# 1. LINIE KODU: część B jest o ~35% krótsza - brak `self.`, brak `unittest.`,
#    brak dekoratora klasy. Mniej „szumu” wokół właściwej treści testu.
#
# 2. KOMUNIKAT PORAŻKI: `unittest` domyślnie pokazuje `5 != 6`; pytest dorzuca
#    *wartości pośrednie* (`where 6 = calc.add(2, 3)`), więc od razu widać,
#    co zwróciło testowane wywołanie. To największa praktyczna różnica.
#
# 3. DODANIE NOWEGO PRZYPADKU: w pytest to jedna linia w `parametrize`, a wynik
#    każdego przypadku jest osobnym wpisem w raporcie (`test_slugify[Łódź-lodz]`).
#    W unittest `subTest` daje podobny efekt, ale raport jest mniej wygodny.
#
# 4. NARZĘDZIA: obie wersje obsługuje VS Code (Testing panel, breakpointy).
#    pytest daje dodatkowo `-k`, `--pdb`, `--ff`, wtyczki (coverage, xdist).
#
# 5. KOSZT MIGRACJI: żaden - pytest uruchamia klasy `unittest.TestCase`.
#    Można więc migrować plik po pliku, bez „wielkiego przełączenia”.
#
# 6. KIEDY unittest: gdy zależy nam na zerowych zależnościach (tylko standardowa
#    biblioteka), na środowisku bez prawa do instalacji pakietów, albo gdy
#    projekt już ma duży zestaw `TestCase`.
#
# =========================================================================== #
# EKSPERYMENT (Zadanie 4)
# =========================================================================== #
# * `python -m unittest` uruchomi TYLKO część A (klasy TestCase). Funkcje
#   w stylu pytest nie są w ogóle widziane - unittest ich nie zbiera.
# * `pytest` uruchomi OBIE części, w tym klasy `unittest.TestCase`.
# * Wzorzec `test_*.py` pasuje obu frameworkom (unittest domyślnie szuka
#   `test*.py`, pytest `test_*.py`), dlatego jest najbezpieczniejszą konwencją.
