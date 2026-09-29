"""Kod produkcyjny do zadania z tematu 07 (porównanie ``unittest`` i ``pytest``).

Ten sam kod testujemy **dwa razy**: raz w stylu ``unittest``, raz w stylu
``pytest`` (patrz ``test_solutions_07.py``). Celem zadania jest napisanie obu
wersji i porównanie ich czytelności.

Uruchomienie demonstracji::

    python src/01-OOP/07-testing-frameworks/exercises/string_utils.py
"""

from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")
_NON_SLUG = re.compile(r"[^a-z0-9]+")

_TRANSLITERATION = str.maketrans(
    {"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
     "ó": "o", "ś": "s", "ź": "z", "ż": "z"}
)

_MIN_TRUNCATE_LIMIT = 4


def normalize(text: str) -> str:
    """Zamienia wszystkie ciągi białych znaków na pojedyncze spacje i przycina.

    ``"  Ala   ma\\tkota  "`` -> ``"Ala ma kota"``; pusty napis zostaje pusty.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    return _WHITESPACE.sub(" ", text).strip()


def word_count(text: str) -> int:
    """Liczba słów po normalizacji (pusty napis -> 0)."""
    normalized = normalize(text)
    return len(normalized.split()) if normalized else 0


def slugify(text: str) -> str:
    """Zamienia tekst na „slug” nadający się do adresu URL.

    ``"Zażółć gęślą jaźń"`` -> ``"zazolc-gesla-jazn"``.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    lowered = text.lower().translate(_TRANSLITERATION)
    return _NON_SLUG.sub("-", lowered).strip("-")


def truncate(text: str, limit: int) -> str:
    """Skraca tekst do ``limit`` znaków, dodając ``"..."`` na końcu.

    Dla ``limit < 4`` podnosi ``ValueError`` (nie da się zmieścić treści
    i wielokropka w mniej niż 4 znakach).
    """
    if limit < _MIN_TRUNCATE_LIMIT:
        raise ValueError(f"limit must be at least {_MIN_TRUNCATE_LIMIT}, got {limit}")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def main() -> None:
    sample = "  Zażółć   gęślą   jaźń  "
    print(f"normalize({sample!r}) -> {normalize(sample)!r}")
    print(f"word_count({sample!r}) -> {word_count(sample)}")
    print(f"slugify({sample!r}) -> {slugify(sample)!r}")
    print(f"truncate('abcdefgh', 5) -> {truncate('abcdefgh', 5)!r}")


if __name__ == "__main__":
    main()
