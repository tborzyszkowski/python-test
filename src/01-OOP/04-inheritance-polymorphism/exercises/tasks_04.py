"""Zadania do samodzielnego wykonania - temat 04 (dziedziczenie i polimorfizm).

Rozwiązania: ``solutions_04.py``. Testy: ``test_solutions_04.py``.

    python -m pytest src/01-OOP/04-inheritance-polymorphism/exercises/test_solutions_04.py -v

Zasada, którą ćwiczysz: **podklasa może rozszerzać zachowanie, ale nie może
łamać kontraktu klasy bazowej** (zasada podstawienia Liskov, LSP). Testy
polimorficzne - uruchamiane na całej liście narzędzi - wychwytują takie
naruszenia natychmiast.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# --------------------------------------------------------------------------- #
# Kontrakt narzędzia - dany, nie zmieniaj sygnatur!
# --------------------------------------------------------------------------- #


class Tool(ABC):
    """Narzędzie z wytrzymałością. Uzupełnij metody oznaczone ``NotImplementedError``."""

    wear_per_use: int = 1

    def __init__(self, name: str, durability: int = 100) -> None:
        self.name = name
        self._durability = durability
        self._uses = 0

    @property
    def durability(self) -> int:
        return self._durability

    @property
    def uses(self) -> int:
        return self._uses

    @property
    def is_broken(self) -> bool:
        return self._durability <= 0

    @abstractmethod
    def effect_on(self, target: str) -> str:
        """Zwraca opis efektu. Każde narzędzie robi coś innego - i to jest OK."""

    def use(self, target: str) -> str:
        """Użyj narzędzia: sprawdź stan, zużyj, wykonaj efekt."""
        if self.is_broken:
            raise ToolBrokenError(f"{self.name} is broken and cannot be used")
        if not target:
            raise ValueError("target must not be empty")
        self._uses += 1
        self._durability = max(0, self._durability - self.wear_per_use)
        return self.effect_on(target)

    def repair(self, amount: int | None = None) -> int:
        """Napraw do pełna (``amount is None``) albo o ``amount`` punktów."""
        if amount is not None and amount <= 0:
            raise ValueError(f"repair amount must be positive, got {amount}")
        self._durability = 100 if amount is None else min(100, self._durability + amount)
        return self._durability

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(name={self.name!r}, "
                f"durability={self._durability})")


class ToolError(Exception):
    """Bazowy wyjątek narzędzi."""


class ToolBrokenError(ToolError):
    """Narzędzie jest zużyte."""


# --------------------------------------------------------------------------- #
# Zadanie 1 - nowa podklasa (2 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``Hammer`` - młotek o zadanej masie (kg).
#
# Wymagania:
#  * ``Hammer(name: str, weight_kg: float, durability: int = 60)``,
#  * ``weight_kg`` musi być dodatnia -> ``ValueError``,
#  * ``wear_per_use = 3``,
#  * ``effect_on(target)`` -> ``f"Uderzam w {target} młotkiem {weight_kg:g} kg"``,
#  * metoda ``nail(target: str, count: int) -> list[str]`` używająca narzędzia
#    ``count`` razy (analogicznie do ``Driller.drill_many`` z przykładu);
#    dla ``count <= 0`` podnosi ``ValueError``.
#
# Podpowiedź: ``f"...{self.weight_kg:g}..."`` usuwa końcowe zera (``2.0`` -> ``2``).


# --------------------------------------------------------------------------- #
# Zadanie 2 - klient polimorficzny i agregacja (3 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``ToolKit`` - zestaw narzędzi, który **nie zna** ich typów.
#
# Wymagania:
#  * ``ToolKit(tools: Iterable[Tool] | None = None)``,
#  * ``add(tool)`` odrzuca obiekty niebędące ``Tool`` -> ``TypeError``,
#  * ``__len__`` i ``__iter__``,
#  * ``total_uses`` (suma użyć), ``total_durability`` (suma wytrzymałości),
#  * ``broken_tools`` -> lista **nazw** zepsutych narzędzi,
#  * ``use_all(target) -> dict[str, str]`` używa wszystkich sprawnych narzędzi
#    i mapuje nazwa -> efekt; zepsute pomija,
#  * ``use_all`` dla zestawu bez sprawnych narzędzi podnosi ``ToolError``
#    z komunikatem "no working tools",
#  * ``most_durable() -> Tool | None``.
#
# Podpowiedzi:
#  * ``use_all`` to miejsce, w którym polimorfizm „płaci za siebie” - jedna
#    pętla obsługuje wszystkie typy narzędzi,
#  * agregaty: ``sum(tool.uses for tool in self._tools)``,
#  * ``max(..., key=..., default=None)`` obsługuje pusty zestaw.


# --------------------------------------------------------------------------- #
# Zadanie 3 - naprawa naruszenia LSP (3 pkt)
# --------------------------------------------------------------------------- #
# Poniższa podklasa łamie kontrakt: dla części wejść zwraca ``None`` zamiast
# ``str``, a dodatkowo wymaga, by ``target`` miał co najmniej 3 znaki.
#
#     class FancySaw(Tool):
#         wear_per_use = 2
#
#         def effect_on(self, target: str) -> str:
#             if len(target) < 3:
#                 return None                     # ❌ łamie typ zwracany
#             if target == "metal":
#                 raise RuntimeError("nie lubię metalu")   # ❌ nieoczekiwany wyjątek
#             return f"Piłuję {target}"
#
# Objawy w kodzie klienckim:
#   * ``use_all`` zwraca ``None`` jako efekt (a potem ``.upper()`` wybucha),
#   * ``pytest.raises(ToolError)`` nie łapie ``RuntimeError``,
#   * test „każde narzędzie zwraca niepusty str” pada dla ``target="ab"``.
#
# Zadanie: napisz poprawną wersję ``FancySaw``:
#  * ``effect_on`` **zawsze** zwraca ``str``,
#  * nieograniczony ``target`` (również krótki) - dla ``"a"`` zwraca
#    ``"Piłuję a"``,
#  * nieobsługiwany materiał (np. ``"metal"``) zgłasza ``ToolError``
#    z komunikatem "unsupported material",
#  * ``wear_per_use = 2``.
#
# W komentarzu ``# LSP:`` (1-2 zdania) wyjaśnij, dlaczego łamanie typu
# zwracanego psuje kod kliencki.
#
# Podpowiedzi:
#  * wyjątki „domenowe” dziedziczą po ``ToolError`` - wtedy klient może
#    łapać jedną rodzinę błędów,
#  * rzucenie wyjątku jest OK (to udokumentowana część kontraktu);
#    zwrócenie ``None`` tam, gdzie obiecano ``str`` - nie jest.


# --------------------------------------------------------------------------- #
# Zadanie 4 (dla chętnych) - polimorfizm przez Protocol (2 pkt)
# --------------------------------------------------------------------------- #
# Napisz ``MultiTool`` (bez dziedziczenia po ``Tool``!), który:
#  * ma atrybut ``name`` i metodę ``use(target) -> str``,
#  * ma właściwość ``is_broken`` (zawsze ``False`` - to magiczne narzędzie),
#  * zlicza użycia w ``uses``.
#
# Następnie napisz funkcję ``use_anything(thing, target: str) -> str``, która
# przyjmuje dowolny obiekt zgodny z protokołem ``ToolLike`` i **weryfikuje
# kontrakt w czasie wykonania**: jeżeli obiekt nie ma metody ``use``, podnosi
# ``TypeError`` z komunikatem "does not implement ToolLike".
#
# Podpowiedzi:
#  * ``hasattr(thing, "use")`` wystarczy do sprawdzenia „kształtu”,
#  * nie używaj ``isinstance`` - celem jest duck typing,
#  * dopisz do protokołu ``ToolLike`` deklarację ``name: str`` i
#    ``def use(self, target: str) -> str: ...``.
