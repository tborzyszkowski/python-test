"""Przykład 02 - ``Protocol``, kacze typowanie i antywzorzec ``isinstance``.

Uruchomienie::

    python src/01-OOP/04-inheritance-polymorphism/examples/02_protocols_and_duck_typing.py

Trzy lekcje:

1. **Kacze typowanie (duck typing)**: funkcja ``use_tool`` nie wymaga żadnej
   wspólnej klasy bazowej - wystarczy, że obiekt ma metodę ``use``.
2. **``Protocol``** opisuje taki kontrakt formalnie i pozwala sprawdzić go
   w typowaniu statycznym (Pylance/mypy) oraz w ``isinstance``
   (z ``@runtime_checkable``).
3. **Antywzorzec ``if isinstance(...)``**: rozgałęzianie po typie wymaga
   edycji przy każdym nowym narzędziu. Polimorfizm wymaga tylko nowej klasy.

Uwaga o klasach abstrakcyjnych: ``ABC`` narzuca kontrakt w momencie tworzenia
obiektu (nie da się utworzyć podklasy bez implementacji), a ``Protocol``
opisuje kontrakt bez wymuszania dziedziczenia. W praktyce stosuje się oba:
``ABC`` dla hierarchii własnych, ``Protocol`` dla kodu, który ma współpracować
z obiektami spoza naszej hierarchii (np. z biblioteki).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# --------------------------------------------------------------------------- #
# Kontrakt opisany protokołem (typing strukturalny)
# --------------------------------------------------------------------------- #
@runtime_checkable
class ToolLike(Protocol):
    """Cokolwiek, co ma ``name`` i umie się "użyć" na celu."""

    name: str

    def use(self, target: str) -> str:
        ...


class LegacyScrewdriver:
    """Klasa "z zewnątrz" (np. z biblioteki) - o naszym protokole nic nie wie."""

    def __init__(self, size: str = "PH2") -> None:
        self.size = size
        self.name = f"śrubokręt {size}"
        self.wear = 0

    def use(self, target: str) -> str:
        self.wear += 1
        return f"Wkręcam śrubę {self.size} w {target}"


class BrokenGadget:
    """Obiekt, który udaje narzędzie, ale nie ma ``use`` - protokół go odrzuci."""

    name = "błyskotka"

    def wiggle(self) -> str:
        return "błyszczę"


# --------------------------------------------------------------------------- #
# Kod kliencki: duck typing + Protocol
# --------------------------------------------------------------------------- #
def use_tool(tool: ToolLike, target: str) -> str:
    """Używa dowolnego obiektu zgodnego z ``ToolLike`` (bez dziedziczenia)."""
    return tool.use(target)


def use_many(tools: list[ToolLike], target: str) -> list[str]:
    return [use_tool(tool, target) for tool in tools]


# --------------------------------------------------------------------------- #
# Antywzorzec: rozgałęzianie po typie
# --------------------------------------------------------------------------- #
def describe_by_isinstance(tool: object) -> str:
    """[ZLE] Antywzorzec: każde nowe narzędzie wymaga zmiany tej funkcji."""
    if isinstance(tool, LegacyScrewdriver):
        return "śrubokręt"
    if isinstance(tool, BrokenGadget):
        return "błyskotka"
    return "nieznane narzędzie"


# --------------------------------------------------------------------------- #
# Rozwiązanie polimorficzne
# --------------------------------------------------------------------------- #
class Describable(ABC):
    """Wersja poprawna: opis dostarcza sama klasa (metoda polimorficzna)."""

    @abstractmethod
    def describe(self) -> str:
        ...


class Screwdriver(Describable):
    """Nowe narzędzie = nowa klasa. Żadna istniejąca funkcja nie wymaga zmian."""

    def __init__(self, size: str = "PH2") -> None:
        self.size = size
        self.name = f"śrubokręt {size}"

    def use(self, target: str) -> str:
        return f"Wkręcam śrubę {self.size} w {target}"

    def describe(self) -> str:
        return f"śrubokręt krzyżowy {self.size}"


def demo_duck_typing() -> None:
    print("== 1. Kacze typowanie: liczy się metoda, nie pochodzenie ==")
    tools: list[ToolLike] = [LegacyScrewdriver(), Screwdriver("T15")]
    for effect in use_many(tools, "szafa"):
        print(f"  {effect}")
    print()


def demo_protocol_isinstance() -> None:
    print("== 2. @runtime_checkable pozwala sprawdzić 'kształt' obiektu ==")
    print(f"isinstance(LegacyScrewdriver(), ToolLike) -> "
          f"{isinstance(LegacyScrewdriver(), ToolLike)}")
    print(f"isinstance(BrokenGadget(), ToolLike)      -> "
          f"{isinstance(BrokenGadget(), ToolLike)}")
    print("(protokół sprawdza tylko obecność metod - nie sprawdza typów argumentów)")
    print()


def demo_antipattern() -> None:
    print("== 3. Antywzorzec isinstance vs polimorfizm ==")
    objects = [LegacyScrewdriver(), BrokenGadget(), Screwdriver()]
    for obj in objects:
        print(f"  describe_by_isinstance -> {describe_by_isinstance(obj)}")
    print("  Dodanie nowego narzędzia wymaga edycji describe_by_isinstance  [ZLE]")
    print()

    print("  Polimorficznie:")
    for tool in (Screwdriver(), Screwdriver("T20")):
        print(f"    {tool.describe()} <- wie o sobie sama klasa  [OK]")
    print()


def demo_abc_enforcement() -> None:
    print("== 4. ABC wymusza kontrakt już przy tworzeniu obiektu ==")

    class HalfDone(Describable):
        """Brak implementacji ``describe``."""

    try:
        HalfDone()  # type: ignore[abstract]
    except TypeError as exc:
        print(f"HalfDone() -> TypeError: {exc}")
    print()


def demo_virtual_subclass() -> None:
    print("== 5. ABC.register(): wirtualna podklasa (obietnica, nie sprawdzenie) ==")

    class ThirdPartyTool:
        """Klasa spoza naszej hierarchii - ma tylko ``use``."""

        def __init__(self) -> None:
            self.name = "narzędzie 3rd party"

        def use(self, target: str) -> str:
            return f"Używam {self.name} na {target}"

    Describable.register(ThirdPartyTool)      # type: ignore[attr-defined]
    instance = ThirdPartyTool()
    print(f"isinstance(ThirdPartyTool(), Describable) -> "
          f"{isinstance(instance, Describable)}")
    print(f"hasattr(instance, 'describe')             -> {hasattr(instance, 'describe')}")
    print("Uwaga: register() to obietnica programisty - ABC jej NIE weryfikuje,")
    print("więc instance.describe() zakończyłoby się AttributeError.")
    print("Dlatego wolimy Protocol (sprawdza kształt) albo jawne dziedziczenie.")


def main() -> None:
    demo_duck_typing()
    demo_protocol_isinstance()
    demo_antipattern()
    demo_abc_enforcement()
    demo_virtual_subclass()


if __name__ == "__main__":
    main()
