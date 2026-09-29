"""Przykład 01 - klasa a obiekt (instancja) w Pythonie.

Uruchomienie::

    python src/01-OOP/01-class-vs-object/examples/01_hero_class_vs_object.py

Kluczowe obserwacje:

1. Klasa jest **obiektem** (instancją typu ``type``) - też ma swoje atrybuty
   i można się do niej odwoływać jak do zwykłej wartości.
2. Instancję tworzymy wywołując klasę: ``Hero("Aragorn")``.
3. Atrybuty przypisane w ``__init__`` przez ``self`` są **instancyjne**
   (każdy obiekt ma własną kopię).
4. Atrybuty zdefiniowane w ciele klasy są **klasowe** (współdzielone przez
   wszystkie instancje, dopóki nie zostaną przesłonięte).
5. ``__repr__`` i ``__eq__`` mają znaczenie nie tylko estetyczne - bez nich
   komunikat porażki testu jest nieczytelny (widzimy adres w pamięci).

Dlaczego to ważne dla testowania?

* Testy *instancji* sprawdzają **stan pojedynczego obiektu** (np. „po ataku HP
  spadło o 30”).
* Testy na poziomie *klasy* sprawdzają **reguły wspólne** (np. „wszyscy
  bohaterowie mają gatunek human”).
* Bez rozróżnienia tych dwóch poziomów łatwo napisać test, który sprawdza
  przypadkiem stan współdzielony i psuje się przy kolejnym teście.
"""

from __future__ import annotations


class Hero:
    """Bohater gry - minimalny model pokazujący klasę i instancję."""

    # Atrybut klasowy: jedna wartość dla całej rodziny obiektów.
    species: str = "human"

    def __init__(self, name: str, hp: int = 100) -> None:
        # Atrybuty instancyjne: własne dla każdego obiektu.
        self.name = name
        self.hp = hp

    def take_damage(self, amount: int) -> int:
        """Zmniejsza HP o ``amount`` (nie poniżej zera) i zwraca nowe HP."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self.hp = max(0, self.hp - amount)
        return self.hp

    def __repr__(self) -> str:
        """Czytelna reprezentacja obiektu - ratuje komunikaty testów."""
        return f"Hero(name={self.name!r}, hp={self.hp})"

    def __eq__(self, other: object) -> bool:
        """Dwa obiekty są równe, gdy mają ten sam stan logiczny.

        Zwrócenie ``NotImplemented`` (a nie ``False``) sprawia, że Python
        spróbuje porównania po stronie prawego operandu. To poprawny wzorzec
        i zarazem świetny materiał na test jednostkowy.
        """
        if not isinstance(other, Hero):
            return NotImplemented
        return (self.name, self.hp) == (other.name, other.hp)


def demo_class_is_an_object() -> None:
    print("== 1. Klasa też jest obiektem ==")
    print(f"type(Hero)          -> {type(Hero)}")
    print(f"Hero.__name__       -> {Hero.__name__}")
    print(f"Hero.species        -> {Hero.species!r}   # dostęp przez klasę")
    print(f"id(Hero)            -> {id(Hero):#x}")
    print()


def demo_instances_are_independent() -> None:
    print("== 2. Instancje są niezależne ==")
    aragorn = Hero("Aragorn", hp=100)
    legolas = Hero("Legolas", hp=80)

    print(f"aragorn             -> {aragorn}")
    print(f"legolas             -> {legolas}")
    print(f"aragorn is legolas  -> {aragorn is legolas}       # różne obiekty")

    aragorn.take_damage(30)
    print(f"po ataku aragorn    -> {aragorn}")
    print(f"legolas bez zmian   -> {legolas}")
    print(f"aragorn == legolas  -> {aragorn == legolas}")

    tmp = Hero("Aragorn", hp=70)
    print(f"aragorn == tmp      -> {aragorn == tmp}     # równość logiczna")
    print()


def demo_shared_class_attribute() -> None:
    print("== 3. Atrybut klasowy jest współdzielony ==")
    a = Hero("A")
    b = Hero("B")

    print(f"a.species           -> {a.species!r}")
    print(f"b.species           -> {b.species!r}")
    print("'a.__dict__' nie zawiera 'species':", "species" in a.__dict__)

    # UWAGA: przypisanie do instancji tworzy atrybut instancyjny (przesłania
    # atrybut klasowy), a nie modyfikuje klasy! To najczęstsza pułapka.
    a.species = "elf"
    a.__class__.species = "human"  # jawne odwołanie do klasy
    print(f"po 'a.species = elf' -> a.species={a.species!r}, b.species={b.species!r}")
    print("a.__dict__          ->", a.__dict__)
    print()


def demo_instance_dict() -> None:
    print("== 4. Podgląd stanu obiektu: __dict__ ==")
    hero = Hero("Gimli")
    hero.take_damage(10)
    print("hero.__dict__       ->", hero.__dict__)
    print("vars(hero)          ->", vars(hero))  # równoważne
    print()


def main() -> None:
    demo_class_is_an_object()
    demo_instances_are_independent()
    demo_shared_class_attribute()
    demo_instance_dict()


if __name__ == "__main__":
    main()
