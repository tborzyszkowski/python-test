"""Przykład 01 - dziedziczenie i polimorfizm: hierarchia narzędzi.

Uruchomienie::

    python src/01-OOP/04-inheritance-polymorphism/examples/01_tools_polymorphism.py

Model: ``Tool`` to klasa abstrakcyjna (interfejs narzędzia), a ``Broom``,
``Driller`` i ``Knife`` to konkretne narzędzia. Każde narzędzie ma **inny**
efekt użycia, ale **ten sam** kontrakt:

    tool.use(target) -> str

Dzięki temu pętla:

    for tool in kit:            # nie wiemy, co to za narzędzie!
        print(tool.use("deska"))

działa poprawnie dla każdego z nich. To jest **polimorfizm**: jedna instrukcja,
wiele zachowań, wybranych dynamicznie na podstawie typu obiektu.

Dodatkowo w klasie bazowej stosujemy **metodę szablonową** (template method):
``use()`` wykonuje stałą procedurę (sprawdź, zużyj, wykonaj efekt), a klasy
pochodne dostarczają tylko zmienny fragment (``effect_on``). Dzięki temu
logika „zużycia narzędzia” istnieje w jednym miejscu.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator


# --------------------------------------------------------------------------- #
# Wyjątki domenowe
# --------------------------------------------------------------------------- #
class ToolError(Exception):
    """Bazowy wyjątek dla problemów z narzędziami."""


class ToolBrokenError(ToolError):
    """Narzędzie jest zużyte i nie można go użyć."""


# --------------------------------------------------------------------------- #
# Klasa abstrakcyjna - kontrakt narzędzia
# --------------------------------------------------------------------------- #
class Tool(ABC):
    """Abstrakcyjne narzędzie: wspólny stan i szablon użycia.

    ``ABC`` + ``@abstractmethod`` oznacza: nie da się utworzyć ``Tool()``,
    a każda konkretna podklasa **musi** dostarczyć ``effect_on``.
    """

    #: Ile punktów wytrzymałości ubywa przy każdym użyciu (podklasy nadpisują).
    wear_per_use: int = 1

    def __init__(self, name: str, durability: int = 100) -> None:
        if not name:
            raise ValueError("tool name must not be empty")
        if durability <= 0:
            raise ValueError(f"durability must be positive, got {durability}")
        self.name = name
        self._durability = durability
        self._uses = 0

    # --- wspólny stan (dziedziczony przez wszystkie narzędzia) ---------- #
    @property
    def durability(self) -> int:
        return self._durability

    @property
    def uses(self) -> int:
        return self._uses

    @property
    def is_broken(self) -> bool:
        return self._durability <= 0

    # --- część zmienna (każde narzędzie robi coś innego) ---------------- #
    @abstractmethod
    def effect_on(self, target: str) -> str:
        """Zwraca opis efektu działania narzędzia na ``target``."""
        raise NotImplementedError

    # --- metoda szablonowa: stała procedura używająca części zmiennej ----- #
    def use(self, target: str) -> str:
        """Użyj narzędzia na celu. Kolejność kroków jest zawsze taka sama."""
        if self.is_broken:
            raise ToolBrokenError(f"{self.name} is broken and cannot be used")
        if not target:
            raise ValueError("target must not be empty")

        self._uses += 1
        self._durability = max(0, self._durability - self.wear_per_use)
        return self.effect_on(target)

    def repair(self, amount: int | None = None) -> int:
        """Napraw narzędzie (domyślnie do pełna) i zwróć nową wytrzymałość."""
        if amount is not None and amount <= 0:
            raise ValueError(f"repair amount must be positive, got {amount}")
        self._durability = 100 if amount is None else min(100, self._durability + amount)
        return self._durability

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(name={self.name!r}, "
                f"durability={self._durability})")


# --------------------------------------------------------------------------- #
# Konkretne narzędzia
# --------------------------------------------------------------------------- #
class Broom(Tool):
    """Miotła: prawie się nie zużywa, ale nie robi dziur."""

    wear_per_use = 1

    def __init__(self, name: str = "miotła", durability: int = 100) -> None:
        super().__init__(name, durability)

    def effect_on(self, target: str) -> str:
        return f"Zamiatam {target}"


class Driller(Tool):
    """Wiertarka: szybko się zużywa, ale wierci otwory o zadanej średnicy."""

    wear_per_use = 5

    def __init__(self, name: str, bit_mm: float, durability: int = 50) -> None:
        super().__init__(name, durability)
        if bit_mm <= 0:
            raise ValueError(f"bit_mm must be positive, got {bit_mm}")
        self.bit_mm = float(bit_mm)

    def effect_on(self, target: str) -> str:
        return f"Wiercę otwór {self.bit_mm:g} mm w {target}"

    def drill_many(self, target: str, count: int) -> list[str]:
        """Użyj wiertarki ``count`` razy - każdy otwór zużywa wiertło."""
        if count <= 0:
            raise ValueError(f"count must be positive, got {count}")
        return [self.use(target) for _ in range(count)]


class Knife(Tool):
    """Nóż: kroi, zużywa się średnio, ma długość ostrza."""

    wear_per_use = 2

    def __init__(self, name: str, blade_cm: float, durability: int = 80) -> None:
        super().__init__(name, durability)
        if blade_cm <= 0:
            raise ValueError(f"blade_cm must be positive, got {blade_cm}")
        self.blade_cm = float(blade_cm)

    def effect_on(self, target: str) -> str:
        return f"Cięcie {target} ostrzem {self.blade_cm:g} cm"

    def is_sharp(self) -> bool:
        """Nóż jest ostry, dopóki ma co najmniej połowę wytrzymałości."""
        return self.durability >= 40


class KitchenKnife(Knife):
    """Podklasa: dodaje kontekst kuchenny, ale zachowuje kontrakt ``Knife``."""

    def __init__(self, name: str = "nóż kuchenny", blade_cm: float = 18) -> None:
        super().__init__(name, blade_cm, durability=80)

    def effect_on(self, target: str) -> str:
        # Rozszerzamy zachowanie, nie łamiemy kontraktu: nadal zwracamy ``str``.
        return f"{super().effect_on(target)} (deska kuchenna)"


# --------------------------------------------------------------------------- #
# Klient polimorficzny - nie zna konkretnych typów narzędzi
# --------------------------------------------------------------------------- #
class ToolKit:
    """Zestaw narzędzi. Iteruje po nich **nie znając** ich typów."""

    def __init__(self, tools: Iterable[Tool] | None = None) -> None:
        self._tools: list[Tool] = list(tools) if tools is not None else []

    def add(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise TypeError(f"expected Tool, got {type(tool).__name__}")
        self._tools.append(tool)

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self) -> Iterator[Tool]:
        return iter(self._tools)

    @property
    def total_uses(self) -> int:
        return sum(tool.uses for tool in self._tools)

    @property
    def total_durability(self) -> int:
        return sum(tool.durability for tool in self._tools)

    @property
    def broken_tools(self) -> list[str]:
        return [tool.name for tool in self._tools if tool.is_broken]

    def use_all(self, target: str) -> dict[str, str]:
        """Użyj wszystkich sprawnych narzędzi na ``target``.

        To jest **polimorficzne wywołanie**: ten sam kod, różne efekty.
        Zepsute narzędzia są pomijane (ich nazwy trafiają do ``broken_tools``).
        """
        results: dict[str, str] = {}
        for tool in self._tools:
            if tool.is_broken:
                continue
            results[tool.name] = tool.use(target)
        return results

    def most_durable(self) -> Tool | None:
        return max(self._tools, key=lambda t: t.durability, default=None)

    def __repr__(self) -> str:
        return f"ToolKit(tools={[tool.name for tool in self._tools]!r})"


# --------------------------------------------------------------------------- #
# Demonstracje
# --------------------------------------------------------------------------- #


def demo_abstract_base() -> None:
    print("== 1. Klasy abstrakcyjnej nie da się utworzyć ==")
    try:
        Tool("narzędzie")  # type: ignore[abstract]
    except TypeError as exc:
        print(f"Tool(...)            -> TypeError: {exc}")
    try:

        class IncompleteTool(Tool):
            """Podklasa bez implementacji effect_on."""

        IncompleteTool("x")  # type: ignore[abstract]
    except TypeError as exc:
        print(f"IncompleteTool(...)  -> TypeError: {exc}")
    print()


def demo_polymorphism() -> None:
    print("== 2. Jedna pętla, różne zachowania ==")
    kit = ToolKit([
        Broom(),
        Driller("wiertarka Bosch", bit_mm=8),
        Knife("nóż survivalowy", blade_cm=12),
        KitchenKnife(),
    ])
    for tool in kit:  # nie interesuje nas, co to za klasa
        print(f"{type(tool).__name__:<12} use -> {tool.use('deska')}")
    print()


def demo_kit_aggregation() -> None:
    print("== 3. Agregacja w kliencie polimorficznym ==")
    driller = Driller("wiertarka", bit_mm=6, durability=10)
    kit = ToolKit([Broom(), driller, Knife("nóż", blade_cm=9, durability=6)])

    print(f"total_durability     -> {kit.total_durability}")
    print(f"total_uses           -> {kit.total_uses}")
    print(f"broken_tools         -> {kit.broken_tools}")

    effects = kit.use_all("płyta")
    for name, effect in effects.items():
        print(f"  {name:<16} -> {effect}")

    print(f"po użyciu: total_durability -> {kit.total_durability}")
    print(f"most_durable         -> {kit.most_durable()}")
    print()


def demo_broken_tool() -> None:
    print("== 4. Narzędzie zużyte i naprawa ==")
    driller = Driller("wiertarka", bit_mm=5, durability=10)  # wear 5 -> 2 użycia
    driller.drill_many("ściana", count=2)
    print(f"po 2 użyciach        -> durability={driller.durability}, "
          f"is_broken={driller.is_broken}")
    try:
        driller.use("ściana")
    except ToolBrokenError as exc:
        print(f"use() na zepsutym    -> ToolBrokenError: {exc}")
    print(f"repair()             -> durability={driller.repair()}")
    print(f"repair(1000)         -> durability={driller.repair(1000)} (limit 100)")
    print()


def demo_subclass_extension() -> None:
    print("== 5. Podklasa rozszerza, ale nie łamie kontraktu ==")
    knife = Knife("nóż", blade_cm=20)
    kitchen = KitchenKnife()
    for tool in (knife, kitchen):
        print(f"{type(tool).__name__:<12} -> {tool.effect_on('pomidor')}")
    print("Oba zwracają str, więc pętla polimorficzna działa dla obu.")
    print()


def main() -> None:
    demo_abstract_base()
    demo_polymorphism()
    demo_kit_aggregation()
    demo_broken_tool()
    demo_subclass_extension()


if __name__ == "__main__":
    main()
