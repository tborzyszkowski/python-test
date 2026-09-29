"""Przykład 02 - ``Segment``: właściwości wyliczane na podstawie innych obiektów.

Uruchomienie::

    python src/01-OOP/02-encapsulation-property/examples/02_segment_derived_properties.py

Ten przykład pokazuje *naturalną* drogę do kompozycji (temat 03):
``Segment`` nie dziedziczy po ``Point``, tylko **zawiera dwa** punkty.

Dlaczego to ma znaczenie dla testów?

* ``Segment`` nie ma własnego stanu poza dwoma punktami - cała logika
  (długość, środek, degeneracja) jest **funkcją stanu**, czyli łatwa do
  przetestowania bez żadnej infrastruktury.
* ``midpoint`` zwraca **nowy** ``Point``, więc nie ma ryzyka, że ktoś zmieni
  środek segmentu przez modyfikację zwróconego obiektu (brak aliasingu).
* Właściwości wyliczane nie wymagają synchronizacji - nie istnieje stan
  „długość” osobny od stanu „końce”.

Uwaga o ``@cached_property``: skoro ``length`` zależy od ``start``/``end``,
a te mogą się zmienić (są mutowalne), pamiętanie wyniku byłoby **źródłem
błędu**. Cachujemy tylko to, co naprawdę jest niezmienne w cyklu życia
obiektu (np. pole ``immutable`` w dataclass zamrożonym).
"""

from __future__ import annotations

import math
from importlib import import_module

# Importujemy ``Point`` z przykładu 01 (moduł leży w tym samym katalogu).
# Dzięki conftest.py katalog examples/ jest na sys.path, więc działa też
# uruchomienie z innego katalogu roboczego.
Point = import_module("01_point_property").Point


class Segment:
    """Odcinek zdefiniowany przez dwa punkty końcowe."""

    def __init__(self, start: Point, end: Point) -> None:
        if not isinstance(start, Point) or not isinstance(end, Point):
            raise TypeError("start and end must be Point instances")
        self._start = start
        self._end = end

    # ------------------------------------------------------------------ #
    # Dostęp do końców (właściwości z walidacją w setterze)                #
    # ------------------------------------------------------------------ #
    @property
    def start(self) -> Point:
        return self._start

    @start.setter
    def start(self, value: Point) -> None:
        if not isinstance(value, Point):
            raise TypeError(f"start must be a Point, got {type(value).__name__}")
        self._start = value

    @property
    def end(self) -> Point:
        return self._end

    @end.setter
    def end(self, value: Point) -> None:
        if not isinstance(value, Point):
            raise TypeError(f"end must be a Point, got {type(value).__name__}")
        self._end = value

    # ------------------------------------------------------------------ #
    # Właściwości wyliczane - brak setterów                                #
    # ------------------------------------------------------------------ #
    @property
    def length(self) -> float:
        """Długość odcinka - zawsze wyliczana z aktualnych końców."""
        return self._start.distance_to(self._end)

    @property
    def midpoint(self) -> Point:
        """Środek odcinka jako **nowy** obiekt ``Point`` (brak aliasingu)."""
        return Point((self._start.x + self._end.x) / 2, (self._start.y + self._end.y) / 2)

    @property
    def is_degenerate(self) -> bool:
        """Odcinek zdegenerowany: oba końce są identyczne."""
        return self._start == self._end

    @property
    def slope(self) -> float | None:
        """Współczynnik kierunkowy lub ``None`` dla odcinka pionowego."""
        dx = self._end.x - self._start.x
        if dx == 0:
            return None
        return (self._end.y - self._start.y) / dx

    def contains(self, point: Point, eps: float = 1e-9) -> bool:
        """Czy ``point`` leży na odcinku (z tolerancją ``eps``)?"""
        if not isinstance(point, Point):
            raise TypeError(f"expected Point, got {type(point).__name__}")
        a, b, p = self._start, self._end, point
        # odległość a-p + p-b musi równać się długości (z tolerancją)
        return math.isclose(a.distance_to(p) + p.distance_to(b), self.length, abs_tol=eps)

    def __repr__(self) -> str:
        return f"Segment(start={self._start!r}, end={self._end!r})"


def demo_derived_properties() -> None:
    print("== 1. Właściwości wyliczane ==")
    seg = Segment(Point(0, 0), Point(3, 4))
    print(f"seg                  -> {seg}")
    print(f"length               -> {seg.length}          # sqrt(3^2 + 4^2)")
    print(f"midpoint             -> {seg.midpoint}")
    print(f"slope                -> {seg.slope}")
    print(f"is_degenerate        -> {seg.is_degenerate}")
    print()

    print("== 2. Brak synchronizacji: zmiana końca natychmiast zmienia długość ==")
    seg.end = Point(6, 8)
    print(f"po seg.end = (6,8)   -> length={seg.length}, midpoint={seg.midpoint}")
    print()


def demo_no_aliasing() -> None:
    print("== 3. midpoint zwraca NOWY obiekt (brak aliasingu) ==")
    seg = Segment(Point(0, 0), Point(4, 0))
    mid = seg.midpoint
    print(f"mid                  -> {mid}")
    mid.x = 100                     # zmiana lokalnego obiektu...
    print(f"po mid.x = 100       -> mid={mid}, ale seg.midpoint={seg.midpoint}")
    print("Oryginalny segment nietknięty - i to jest własność warta testu.")
    print()


def demo_degenerate_and_vertical() -> None:
    print("== 4. Przypadki brzegowe ==")
    degenerate = Segment(Point(1, 1), Point(1, 1))
    print(f"zero-length          -> length={degenerate.length}, "
          f"is_degenerate={degenerate.is_degenerate}, slope={degenerate.slope}")
    vertical = Segment(Point(2, 0), Point(2, 5))
    print(f"vertical             -> length={vertical.length}, slope={vertical.slope}")
    print()


def demo_contains() -> None:
    print("== 5. Metoda contains z tolerancją ==")
    seg = Segment(Point(0, 0), Point(10, 0))
    for point in (Point(5, 0), Point(11, 0), Point(5, 1)):
        print(f"seg.contains({point}) -> {seg.contains(point)}")
    print()


def main() -> None:
    demo_derived_properties()
    demo_no_aliasing()
    demo_degenerate_and_vertical()
    demo_contains()


if __name__ == "__main__":
    main()
