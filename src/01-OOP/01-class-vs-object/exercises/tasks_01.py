"""Zadania do samodzielnego wykonania - temat 01 (klasa vs obiekt).

Uzupełnij kod w tym pliku (``tasks_01.py``). Wzorcowe rozwiązanie znajduje się
w ``solutions_01.py``, a gotowe testy sprawdzające - w ``test_solutions_01.py``.

Jak sprawdzić swoje rozwiązanie::

    python -m pytest src/01-OOP/01-class-vs-object/exercises/test_solutions_01.py -v

Rady ogólne:
- nie zmieniaj nazw klas, metod i parametrów - testy korzystają z tego API,
- uruchamiaj przykłady z ``examples/`` zanim zaczniesz pisać,
- pamiętaj o typowaniu (``from __future__ import annotations``).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Zadanie 1 - pola i metody instancyjne (2 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj klasę ``Ammo`` opisującą zapas amunicji danego kalibru.
#
# Wymagania:
#  * konstruktor ``Ammo(caliber: str, rounds: int)`` zapisuje argumenty jako
#    atrybuty instancyjne ``caliber`` i ``rounds``,
#  * konstruktor odrzuca ``rounds < 0`` podnosząc ``ValueError``,
#  * metoda ``spend(n: int) -> int`` zmniejsza zapas o ``n`` i zwraca liczbę
#    pozostałych naboi; dla ``n < 0`` podnosi ``ValueError``; dla ``n``
#    większego niż zapas podnosi ``ValueError`` (nie „schodzimy” poniżej zera),
#  * ``__repr__`` zwraca tekst postaci ``Ammo(caliber='9mm', rounds=10)``,
#  * ``__eq__`` porównuje ``caliber`` i ``rounds``; dla obiektu innego typu
#    zwraca ``NotImplemented`` (nie ``False``!).
#
# Podpowiedź: aby zobaczyć oczekiwany format ``__repr__``, uruchom
# ``examples/01_hero_class_vs_object.py`` i przypatrz się metodzie ``__repr__``
# klasy ``Hero`` - wzorzec ``f"...{self.x!r}..."`` jest identyczny.


class Ammo:
    def __init__(self, caliber: str, rounds: int) -> None:
        raise NotImplementedError("Zadanie 1: zaimplementuj konstruktor")

    def spend(self, n: int) -> int:
        raise NotImplementedError("Zadanie 1: zaimplementuj metodę spend")

    def __repr__(self) -> str:
        raise NotImplementedError("Zadanie 1: zaimplementuj __repr__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Zadanie 1: zaimplementuj __eq__")


# --------------------------------------------------------------------------- #
# Zadanie 2 - atrybut klasowy, @classmethod, @staticmethod (3 pkt)
# --------------------------------------------------------------------------- #
# Rozbuduj klasę ``Ammo`` o stan współdzielony i reguły walidacji.
#
# Wymagania:
#  * atrybut klasowy ``total_created`` zlicza utworzone obiekty ``Ammo``
#    (aktualizowany przez klasę: ``Ammo.total_created += 1``),
#  * ``@classmethod created_count(cls) -> int`` zwraca licznik (użyj ``cls``,
#    nie ``Ammo`` - dzięki temu metoda działa dla podklas),
#  * ``@classmethod reset_counter(cls) -> None`` zeruje licznik
#    (potrzebne do izolacji testów!),
#  * ``@staticmethod is_valid_caliber(value: str) -> bool`` zwraca ``True``
#    dla napisów pasujących do wzorca kalibru: cyfry, opcjonalnie kropka
#    i cyfry, opcjonalnie sufiks ``mm`` lub ``cal`` (np. ``"9mm"``, ``"5.56mm"``,
#    ``".45cal"``, ``"12"``). Puste napisy i napisy z literami spoza sufiksu są
#    niepoprawne.
#  * konstruktor podnosi ``ValueError``, gdy ``caliber`` nie przechodzi
#    walidacji ``is_valid_caliber``.
#
# Podpowiedź: w module ``re`` wystarczy ``re.fullmatch(r"...", value)``.
# Zanim napiszesz wzorzec, przetestuj go w REPL-u na przykładach z treści.


# --------------------------------------------------------------------------- #
# Zadanie 3 - pułapka mutowalnego atrybutu klasowego (2 pkt)
# --------------------------------------------------------------------------- #
# Poniższa klasa ``Inventory`` ma błąd: ``items`` jest przypisany w ciele klasy,
# więc jest **współdzielony** przez wszystkie instancje („aliasing”).
#
#     >>> a, b = Inventory(), Inventory()
#     >>> a.add("sword")
#     >>> b.items
#     ['sword']        # <- błąd!
#
# Twoje zadanie:
#  1. popraw klasę tak, aby każda instancja miała własną listę,
#  2. napisz krótkie uzasadnienie (1-2 zdania) w komentarzu ``# DLACZEGO:``,
#     dlaczego poprzednia wersja była błędna i dlaczego nowa jest poprawna,
#  3. nie zmieniając API dodaj metodę ``clear() -> None``.


class Inventory:
    items: list[str] = []  # <-- tu jest błąd

    def add(self, item: str) -> None:
        self.items.append(item)

    def clear(self) -> None:
        raise NotImplementedError("Zadanie 3: zaimplementuj clear")


# --------------------------------------------------------------------------- #
# Zadanie 4 (dla chętnych) - testowalność metod statycznych (1 pkt)
# --------------------------------------------------------------------------- #
# Metody statyczne to funkcje czyste - dlatego testuje się je najprzyjemniej.
# Zadanie: napisz w ``solutions_01.py`` funkcję ``only_valid(*calibers: str)``,
# która zwraca krotkę tylko tych kalibrów, które przechodzą walidację
# ``Ammo.is_valid_caliber``, zachowując kolejność i usuwając duplikaty.
#
# Przykład:
#     >>> only_valid("9mm", "bum!", "9mm", "5.56")
#     ('9mm', '5.56')
#
# Podpowiedź: ``dict.fromkeys(...)`` zachowuje kolejność i usuwa duplikaty.
