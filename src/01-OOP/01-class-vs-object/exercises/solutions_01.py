"""Wzorcowe rozwiązania - temat 01 (klasa vs obiekt).

Plik demonstruje trzy warianty tej samej klasy ``Ammo`` - od najprostszego do
wersji „produkcyjnej”. Taki „stopniowy refactoring” jest dobrym materiałem na
wykład: pokazuje, że ten sam **kontrakt** można zrealizować coraz lepiej,
a testy pozostają niezmienione (i to jest miara dobrego projektu!).

Uruchomienie demonstracji::

    python src/01-OOP/01-class-vs-object/exercises/solutions_01.py
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------- #
# Rozwiązanie 1 - pola i metody instancyjne
# --------------------------------------------------------------------------- #


class AmmoV1:
    """Wersja 1: tylko stan instancyjny i podstawowe operacje."""

    def __init__(self, caliber: str, rounds: int) -> None:
        if rounds < 0:
            raise ValueError(f"rounds must be non-negative, got {rounds}")
        self.caliber = caliber
        self.rounds = rounds

    def spend(self, n: int) -> int:
        if n < 0:
            raise ValueError(f"cannot spend a negative amount: {n}")
        if n > self.rounds:
            raise ValueError(f"not enough rounds: have {self.rounds}, need {n}")
        self.rounds -= n
        return self.rounds

    def __repr__(self) -> str:
        return f"{type(self).__name__}(caliber={self.caliber!r}, rounds={self.rounds})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AmmoV1):
            return NotImplemented
        return (self.caliber, self.rounds) == (other.caliber, other.rounds)


# --------------------------------------------------------------------------- #
# Rozwiązanie 2 - + walidacja kalibru (@staticmethod) i licznik (@classmethod)
# --------------------------------------------------------------------------- #

_CALIBER_PATTERN = re.compile(r"\d+(?:\.\d+)?(?:mm|cal)?|\.\d+(?:mm|cal)?")


class Ammo(AmmoV1):
    """Wersja 2: dodajemy stan klasowy i regułę walidacji kalibru."""

    total_created: int = 0

    def __init__(self, caliber: str, rounds: int) -> None:
        if not self.is_valid_caliber(caliber):
            raise ValueError(f"invalid caliber: {caliber!r}")
        super().__init__(caliber, rounds)
        Ammo.total_created += 1

    # --- metoda statyczna: czysta funkcja, idealna do testów jednostkowych ---
    @staticmethod
    def is_valid_caliber(value: str) -> bool:
        """Czy ``value`` wygląda jak kaliber, np. ``9mm``, ``5.56mm``, ``.45cal``?"""
        if not isinstance(value, str) or not value:
            return False
        return _CALIBER_PATTERN.fullmatch(value) is not None

    # --- metody klasowe: operują na stanie klasy -------------------------- #
    @classmethod
    def created_count(cls) -> int:
        return cls.total_created

    @classmethod
    def reset_counter(cls) -> None:
        """Izolacja stanu w testach - patrz ``reset_ammo_counter`` w testach."""
        cls.total_created = 0

    @classmethod
    def box_of(cls, caliber: str, boxes: int = 1) -> list["Ammo"]:
        """Alternatywny konstruktor: ``boxes`` magazynków po 30 naboi."""
        return [cls(caliber, 30) for _ in range(boxes)]


# --------------------------------------------------------------------------- #
# Rozwiązanie 3 - naprawa mutowalnego atrybutu klasowego
# --------------------------------------------------------------------------- #


class Inventory:
    """Poprawna wersja: każda instancja ma własną listę przedmiotów.

    # DLACZEGO: ``items`` w ciele klasy tworzy **jeden** obiekt listy
    # współdzielony przez wszystkie instancje (mutowalny atrybut klasowy),
    # więc ``a.add("sword")`` zmieniało też ``b.items``. Przeniesienie
    # ``self.items = []`` do ``__init__`` sprawia, że lista powstaje
    # w momencie tworzenia obiektu - czyli stan jest naprawdę instancyjny.
    """

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def clear(self) -> None:
        self.items.clear()

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return f"Inventory(items={self.items!r})"


class BuggyInventory:
    """Wersja z błędem - zostawiona w celach dydaktycznych (NIE kopiuj)."""

    items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)


# --------------------------------------------------------------------------- #
# Rozwiązanie 4 (dla chętnych) - czysta funkcja korzystająca z @staticmethod
# --------------------------------------------------------------------------- #


def only_valid(*calibers: str) -> tuple[str, ...]:
    """Zwraca kalibry poprawne, bez duplikatów, z zachowaniem kolejności."""
    unique = dict.fromkeys(c for c in calibers if Ammo.is_valid_caliber(c))
    return tuple(unique)


# --------------------------------------------------------------------------- #
# Demonstracja
# --------------------------------------------------------------------------- #


def main() -> None:
    print("== Rozwiązanie 1: stan instancyjny ==")
    mag = AmmoV1("9mm", 10)
    print(f"repr                -> {mag}")
    print(f"spend(4)            -> {mag.spend(4)}")
    print(f"po spend            -> {mag}")
    print(f"== porównanie       -> {mag == AmmoV1('9mm', 6)}")
    try:
        mag.spend(99)
    except ValueError as exc:
        print(f"spend(99)           -> ValueError: {exc}")
    print()

    print("== Rozwiązanie 2: licznik i walidacja ==")
    Ammo.reset_counter()
    for caliber in ("9mm", "5.56mm", ".45cal", "12", "bum", ""):
        print(f"is_valid_caliber({caliber!r:>8}) -> {Ammo.is_valid_caliber(caliber)}")
    Ammo.box_of("9mm", boxes=3)
    print(f"created_count()     -> {Ammo.created_count()}")
    print()

    print("== Rozwiązanie 3: mutowalny atrybut klasowy ==")
    good_a, good_b = Inventory(), Inventory()
    good_a.add("sword")
    print(f"Inventory (poprawnie): good_b.items -> {good_b.items}")

    bug_a, bug_b = BuggyInventory(), BuggyInventory()
    bug_a.add("sword")
    print(f"BuggyInventory (błąd): bug_b.items  -> {bug_b.items}")
    print()

    print("== Rozwiązanie 4: only_valid ==")
    print(only_valid("9mm", "bum!", "9mm", "5.56"))


if __name__ == "__main__":
    main()
