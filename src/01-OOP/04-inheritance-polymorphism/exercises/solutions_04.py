"""Wzorcowe rozwiązania - temat 04 (dziedziczenie i polimorfizm).

Demonstracja::

    python src/01-OOP/04-inheritance-polymorphism/exercises/solutions_04.py

Trzy wnioski, które wyprowadzamy z tych rozwiązań:

1. **Klasa abstrakcyjna trzyma wspólną logikę**, a podklasy dostarczają tylko
   zmienny fragment (``effect_on``) - mniej duplikacji, mniej testów.
2. **Klient polimorficzny (``ToolKit``) nie zna typów** - dodanie nowego
   narzędzia nie wymaga zmiany ani jednej linii w ``ToolKit``.
3. **Kontrakt obowiązuje też podklasy** - jeżeli ``effect_on`` ma zwracać
   ``str``, to zwracanie ``None`` psuje klienta, a nie „jest czyimś wyborem”.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Protocol, runtime_checkable


# --------------------------------------------------------------------------- #
# Wyjątki domenowe i klasa bazowa
# --------------------------------------------------------------------------- #
class ToolError(Exception):
    """Bazowy wyjątek dla problemów z narzędziami."""


class ToolBrokenError(ToolError):
    """Narzędzie jest zużyte i nie można go użyć."""


class Tool(ABC):
    """Abstrakcyjne narzędzie: wspólny stan + metoda szablonowa ``use``."""

    wear_per_use: int = 1

    def __init__(self, name: str, durability: int = 100) -> None:
        if not name:
            raise ValueError("tool name must not be empty")
        if durability <= 0:
            raise ValueError(f"durability must be positive, got {durability}")
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
        """Zwraca efekt działania narzędzia (kontrakt: niepusty ``str``)."""

    def use(self, target: str) -> str:
        if self.is_broken:
            raise ToolBrokenError(f"{self.name} is broken and cannot be used")
        if not target:
            raise ValueError("target must not be empty")
        self._uses += 1
        self._durability = max(0, self._durability - self.wear_per_use)
        return self.effect_on(target)

    def repair(self, amount: int | None = None) -> int:
        if amount is not None and amount <= 0:
            raise ValueError(f"repair amount must be positive, got {amount}")
        self._durability = 100 if amount is None else min(100, self._durability + amount)
        return self._durability

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(name={self.name!r}, "
                f"durability={self._durability})")


# --------------------------------------------------------------------------- #
# Rozwiązanie 1 - Hammer
# --------------------------------------------------------------------------- #
class Hammer(Tool):
    """Młotek o zadanej masie - nowa podklasa, zero zmian w klasie bazowej."""

    wear_per_use = 3

    def __init__(self, name: str, weight_kg: float, durability: int = 60) -> None:
        super().__init__(name, durability)
        if weight_kg <= 0:
            raise ValueError(f"weight_kg must be positive, got {weight_kg}")
        self.weight_kg = float(weight_kg)

    def effect_on(self, target: str) -> str:
        return f"Uderzam w {target} młotkiem {self.weight_kg:g} kg"

    def nail(self, target: str, count: int) -> list[str]:
        if count <= 0:
            raise ValueError(f"count must be positive, got {count}")
        return [self.use(target) for _ in range(count)]


# --------------------------------------------------------------------------- #
# Rozwiązanie 2 - ToolKit (klient polimorficzny)
# --------------------------------------------------------------------------- #
class ToolKit:
    """Zestaw narzędzi; działa na każdym ``Tool`` bez znajomości jego typu."""

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

    def working_tools(self) -> list[Tool]:
        return [tool for tool in self._tools if not tool.is_broken]

    def use_all(self, target: str) -> dict[str, str]:
        working = self.working_tools()
        if not working:
            raise ToolError("no working tools available")
        return {tool.name: tool.use(target) for tool in working}

    def most_durable(self) -> Tool | None:
        return max(self._tools, key=lambda tool: tool.durability, default=None)

    def __repr__(self) -> str:
        return f"ToolKit(tools={[tool.name for tool in self._tools]!r})"


# --------------------------------------------------------------------------- #
# Rozwiązanie 3 - FancySaw bez naruszenia LSP
# --------------------------------------------------------------------------- #
class FancySaw(Tool):
    """Piła: zawsze zwraca ``str``; nieobsługiwany materiał zgłasza ``ToolError``."""

    wear_per_use = 2
    _UNSUPPORTED_MATERIALS = ("metal",)

    def __init__(self, name: str = "piła", durability: int = 100) -> None:
        super().__init__(name, durability)

    def effect_on(self, target: str) -> str:
        # LSP: podklasa może zmienić *sposób* działania, ale nie typ zwracany.
        # Zwrócenie None tam, gdzie klient oczekuje str, przenosi błąd daleko
        # od miejsca powstania - dlatego zamiast None zgłaszamy wyjątek.
        if target in self._UNSUPPORTED_MATERIALS:
            raise ToolError(f"unsupported material: {target!r}")
        return f"Piłuję {target}"


# --------------------------------------------------------------------------- #
# Rozwiązanie 4 (dla chętnych) - Protocol, duck typing i MultiTool
# --------------------------------------------------------------------------- #
@runtime_checkable
class ToolLike(Protocol):
    """Kontrakt strukturalny: ``name`` + ``use(target)``."""

    name: str

    def use(self, target: str) -> str:
        ...


def use_anything(thing: object, target: str) -> str:
    """Używa dowolnego obiektu zgodnego z ``ToolLike`` (bez dziedziczenia)."""
    if not isinstance(thing, ToolLike):  # runtime_checkable: sprawdza kształt
        raise TypeError(
            f"{type(thing).__name__} does not implement ToolLike (missing use())"
        )
    return thing.use(target)


class MultiTool:
    """Narzędzie 'magiczne': nie dziedziczy po ``Tool``, ale spełnia protokół."""

    def __init__(self, name: str = "multitool") -> None:
        self.name = name
        self._uses = 0

    @property
    def uses(self) -> int:
        return self._uses

    @property
    def is_broken(self) -> bool:
        return False

    def use(self, target: str) -> str:
        self._uses += 1
        return f"Multitool rozwiązuje problem: {target}"


# --------------------------------------------------------------------------- #
# Demonstracja
# --------------------------------------------------------------------------- #


def main() -> None:
    print("== 1. Nowa podklasa nie wymaga zmian w klasie bazowej ==")
    hammer = Hammer("młotek", weight_kg=1.5, durability=10)
    print(f"use('gwóźdź')        -> {hammer.use('gwóźdź')}")
    print(f"durability           -> {hammer.durability} (wear_per_use=3)")
    print(f"nail(..., 3)         -> {hammer.nail('gwóźdź', 3)}")
    print(f"is_broken            -> {hammer.is_broken} (10 - 4*3 < 0 -> 0)")
    print()

    print("== 2. Klient polimorficzny ==")
    kit = ToolKit([Hammer("młotek", 1.0, durability=60), FancySaw("piła")])
    print(f"use_all('deska')     -> {kit.use_all('deska')}")
    print(f"total_uses           -> {kit.total_uses}")
    print(f"broken_tools         -> {kit.broken_tools}")
    print(f"most_durable         -> {kit.most_durable()}")
    try:
        ToolKit([Hammer("zepsuty", 1.0, durability=1)]).use_all("x")
    except ToolError as exc:
        print(f"zepsuty zestaw       -> ToolError: {exc}")
    print()

    print("== 3. Piła nie łamie kontraktu ==")
    saw = FancySaw()
    print(f"effect_on('a')       -> {saw.effect_on('a')}")
    try:
        saw.use("metal")
    except ToolError as exc:
        print(f"effect_on('metal')   -> ToolError: {exc}")
    print()

    print("== 4. Duck typing: obiekt spoza hierarchii też jest OK ==")
    print(f"use_anything(Hammer('m', 1), 'gwóźdź') -> "
          f"{use_anything(Hammer('m', 1), 'gwóźdź')}")
    multi = MultiTool()
    print(f"use_anything(multi, 'problem')         -> {use_anything(multi, 'problem')}")
    try:
        use_anything("zwykły napis", "x")
    except TypeError as exc:
        print(f"use_anything('napis', 'x')            -> TypeError: {exc}")
    print()

    print("== 5. Polimorfizm przez protokół ==")
    for thing in (Hammer("młotek", 1.0), MultiTool()):
        print(f"  {use_anything(thing, 'zadanie')}")


if __name__ == "__main__":
    main()
