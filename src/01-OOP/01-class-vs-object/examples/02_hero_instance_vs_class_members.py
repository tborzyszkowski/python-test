"""Przykład 02 - pola i metody: instancyjne, klasowe (``@classmethod``),
statyczne (``@staticmethod``).

Uruchomienie::

    python src/01-OOP/01-class-vs-object/examples/02_hero_instance_vs_class_members.py

Trzy rodzaje metod i ich znaczenie dla testowalności:

==================  ==========================================  ==========================
Rodzaj              Pierwszy argument                            Kiedy używać / testowalność
==================  ==========================================  ==========================
metoda instancyjna  ``self`` (obiekt)                            Gdy potrzebny stan obiektu
``@classmethod``    ``cls`` (klasa; działa na podklasach)          Alternatywne konstruktory
``@staticmethod``   *brak* (zwykła funkcja w przestrzeni klasy)    Funkcje czyste - najłatwiejsze
==================  ==========================================  ==========================

Metoda statyczna jest szczególnie wdzięczna w testach: nie wymaga tworzenia
obiektu, nie zależy od stanu - to *funkcja czysta* zorganizowana tematycznie
wewnątrz klasy. Metoda klasowa (fabryka) wymaga klasy, ale pozwala testować
warianty konstrukcji (np. „bohater ranny startuje z 25 HP”).
"""

from __future__ import annotations


class Hero:
    """Bohater z licznikiem populacji, fabryką i walidacją nazwy."""

    # --- atrybuty klasowe ---
    MAX_HP: int = 200
    _population: int = 0  # konwencja: ``_`` = szczegół implementacyjny

    def __init__(self, name: str, hp: int = 100) -> None:
        if not self.is_valid_name(name):
            raise ValueError(f"invalid hero name: {name!r}")
        if not 0 <= hp <= self.MAX_HP:
            raise ValueError(f"hp must be in range 0..{self.MAX_HP}, got {hp}")

        self.name = name
        self._hp = hp
        # Licznik aktualizujemy przez klasę, nie przez instancję!
        Hero._population += 1

    # ------------------------------------------------------------------ #
    # Metody instancyjne                                                  #
    # ------------------------------------------------------------------ #
    def take_damage(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._hp = max(0, self._hp - amount)
        return self._hp

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def is_alive(self) -> bool:
        return self._hp > 0

    # ------------------------------------------------------------------ #
    # Metody klasowe - działają na klasie, nie na instancji               #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_wounded(cls, name: str) -> Hero:
        """Alternatywny konstruktor: bohater zaczyna z 25 HP.

        ``cls`` (a nie ``Hero``) sprawia, że metoda działa poprawnie także
        dla podklas - i właśnie to można sprawdzić testem dziedziczenia.
        """
        return cls(name, hp=25)

    @classmethod
    def population(cls) -> int:
        """Zwraca liczbę utworzonych bohaterów (stan klasy)."""
        return cls._population

    @classmethod
    def reset_population(cls) -> None:
        """Zerowanie licznika - w testach to nasza *izolacja stanu*.

        Bez takiej metody testy sprawdzające licznik byłyby zależne od
        kolejności uruchomienia (klasyczny ``flaky test``).
        """
        cls._population = 0

    # ------------------------------------------------------------------ #
    # Metoda statyczna - nie potrzebuje ani ``self``, ani ``cls``         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Reguła biznesowa: nazwa niepusta, zaczyna się wielką literą."""
        return bool(name) and name[0].isupper()

    def __repr__(self) -> str:
        return f"Hero(name={self.name!r}, hp={self._hp})"


def demo_class_vs_instance_state() -> None:
    print("== 1. Stan klasy vs stan instancji ==")
    Hero.reset_population()
    aragorn = Hero("Aragorn")
    legolas = Hero("Legolas", hp=80)

    print(f"Hero.population()   -> {Hero.population()}   # stan KLASY")
    print(f"aragorn.hp          -> {aragorn.hp}          # stan INSTANCJI")
    print(f"legolas.hp          -> {legolas.hp}           # druga instancja")
    print(f"aragorn.is_alive    -> {aragorn.is_alive}")
    print("'hp' w aragorn.__dict__ ->", "hp" in aragorn.__dict__)
    print("'_hp' w aragorn.__dict__ ->", "_hp" in aragorn.__dict__)
    print()


def demo_classmethod_factory() -> None:
    print("== 2. @classmethod jako alternatywny konstruktor ==")
    wounded = Hero.from_wounded("Boromir")
    print(f"Hero.from_wounded('Boromir') -> {wounded}")
    print(f"wounded.is_alive             -> {wounded.is_alive}")
    print()


def demo_staticmethod_rule() -> None:
    print("== 3. @staticmethod jako funkcja czysta ==")
    for name in ("Aragorn", "aragorn", "", "123"):
        print(f"Hero.is_valid_name({name!r:>10}) -> {Hero.is_valid_name(name)}")
    print()
    print("Metodę statyczną można też wywołać z instancji (ta sama funkcja):")
    print(f"Hero('Aragorn').is_valid_name('Legolas') -> "
          f"{Hero('Aragorn').is_valid_name('Legolas')}")
    print()


def demo_validation_errors() -> None:
    print("== 4. Walidacja w konstruktorze ==")
    for name, hp in (("aragorn", 100), ("Aragorn", 999)):
        try:
            Hero(name, hp)
        except ValueError as exc:
            print(f"Hero({name!r}, hp={hp}) -> ValueError: {exc}")
    print()
    print("Kod, który potrafi głośno zawieść, jest znacznie łatwiejszy w testach")
    print("niż kod, który po cichu przyjmuje niepoprawny stan.")


def main() -> None:
    demo_class_vs_instance_state()
    demo_classmethod_factory()
    demo_staticmethod_rule()
    demo_validation_errors()


if __name__ == "__main__":
    main()
