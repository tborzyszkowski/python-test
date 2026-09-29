"""Wzorcowe rozwiązania - temat 02 (hermetyzacja i ``@property``).

Demonstracja::

    python src/01-OOP/02-encapsulation-property/exercises/solutions_02.py

Wzorce, które warto zapamiętać:

1. **Jedna ścieżka walidacji** - konstruktor ustawia pola przez setter, dzięki
   czemu nie da się „obejść” walidacji.
2. **Walidacja wspólna wydzielona** - jeżeli dwie właściwości walidują tak samo,
   wydziel statyczną metodę pomocniczą (mniej duplikacji = mniej testów).
3. **Właściwości wyliczane bez settera** - nie ma stanu do zsynchronizowania,
   więc nie ma klasy błędów „rozjechanych pól”.
4. **Niemutowalność upraszcza testy** - obiekt, którego nie da się zmienić,
   nie wymaga testów odporności na zmiany w trakcie użycia.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Number = int | float

_MIN_CELSIUS = -273.15


def _require_number(value: Number, name: str, owner: str) -> float:
    """Wspólna walidacja: liczba rzeczywista, bez ``bool`` i bez NaN/inf."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{owner}.{name} must be a number, got {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{owner}.{name} must be finite, got {value!r}")
    return float(value)


# --------------------------------------------------------------------------- #
# Rozwiązanie 1 - Temperature
# --------------------------------------------------------------------------- #


class Temperature:
    """Temperatura z walidacją i właściwościami wyliczanymi."""

    def __init__(self, celsius: Number) -> None:
        self.celsius = celsius  # przez setter -> walidacja obowiązuje też tutaj

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: Number) -> None:
        celsius = _require_number(value, "celsius", "Temperature")
        if celsius < _MIN_CELSIUS:
            raise ValueError(f"celsius below absolute zero: {celsius}")
        self._celsius = celsius

    @property
    def kelvin(self) -> float:
        return self._celsius - _MIN_CELSIUS  # +273.15

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    def __repr__(self) -> str:
        return f"Temperature(celsius={self._celsius!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return math.isclose(self._celsius, other._celsius, abs_tol=1e-9)


# --------------------------------------------------------------------------- #
# Rozwiązanie 2 - Rectangle
# --------------------------------------------------------------------------- #


class Rectangle:
    """Prostokąt, w którym nie da się uzyskać niepoprawnych wymiarów."""

    def __init__(self, width: Number, height: Number) -> None:
        self.width = width
        self.height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: Number) -> None:
        self._width = self._positive(value, "width")

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: Number) -> None:
        self._height = self._positive(value, "height")

    @staticmethod
    def _positive(value: Number, name: str) -> float:
        number = _require_number(value, name, "Rectangle")
        if number <= 0:
            raise ValueError(f"Rectangle.{name} must be positive, got {number}")
        return number

    @property
    def area(self) -> float:
        return self._width * self._height

    @property
    def perimeter(self) -> float:
        return 2 * (self._width + self._height)

    @property
    def is_square(self) -> bool:
        return math.isclose(self._width, self._height)

    def scale(self, factor: Number) -> Rectangle:
        factor_value = _require_number(factor, "factor", "Rectangle")
        if factor_value <= 0:
            raise ValueError(f"scale factor must be positive, got {factor_value}")
        return Rectangle(self._width * factor_value, self._height * factor_value)

    def __repr__(self) -> str:
        return f"Rectangle(width={self._width!r}, height={self._height!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rectangle):
            return NotImplemented
        return (self._width, self._height) == (other._width, other._height)


# --------------------------------------------------------------------------- #
# Rozwiązanie 3 - Player z niezmiennikiem 0 <= hp <= MAX_HP
# --------------------------------------------------------------------------- #


class Player:
    """Gracz, którego HP zawsze mieści się w zakresie 0..MAX_HP."""

    MAX_HP: int = 100

    def __init__(self, name: str, hp: int = 100) -> None:
        self.name = name
        self.hp = hp

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        # DECYZJA: setter reprezentuje "ustawienie stanu z zewnątrz" - wartość
        # spoza zakresu jest błędem wołającego, więc zgłaszamy wyjątek
        # (a nie po cichu nasycamy), aby błąd nie przeszedł niezauważony.
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"hp must be an int, got {type(value).__name__}")
        if not 0 <= value <= self.MAX_HP:
            raise ValueError(f"hp out of range 0..{self.MAX_HP}: {value}")
        self._hp = value

    @property
    def is_alive(self) -> bool:
        return self._hp > 0

    def take_damage(self, amount: int) -> int:
        if amount < 0:
            raise ValueError(f"amount must be non-negative, got {amount}")
        self._hp = max(0, self._hp - amount)
        return self._hp

    def heal(self, amount: int) -> int:
        if amount < 0:
            raise ValueError(f"amount must be non-negative, got {amount}")
        self._hp = min(self.MAX_HP, self._hp + amount)
        return self._hp

    def __repr__(self) -> str:
        return f"Player(name={self.name!r}, hp={self._hp})"


# --------------------------------------------------------------------------- #
# Rozwiązanie 4 (dla chętnych) - FrozenPoint
# --------------------------------------------------------------------------- #
# WNIOSEK: przy obiekcie niemutowalnym nie trzeba pisać testów typu
# "po zmianie pola X właściwość Y nadal się zgadza", nie ma wyścigów i nie ma
# defensorów (tzw. copy defensywny) w API. Testy ograniczają się do wartości
# zwracanych przez metody - czyli do czystych funkcji stanu.


class FrozenPoint:
    """Niemutowalny punkt 2D - sami implementujemy to, co daje ``frozen=True``."""

    __slots__ = ("_x", "_y")

    def __init__(self, x: Number, y: Number) -> None:
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def shift(self, dx: Number, dy: Number) -> FrozenPoint:
        return FrozenPoint(self._x + dx, self._y + dy)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrozenPoint):
            return NotImplemented
        return (self._x, self._y) == (other._x, other._y)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f"FrozenPoint(x={self._x!r}, y={self._y!r})"


@dataclass(frozen=True, slots=True)
class FrozenPointDataclass:
    """To samo co ``FrozenPoint``, ale w dwóch liniach - idiomatyczne w nowym kodzie."""

    x: float
    y: float

    def shift(self, dx: Number, dy: Number) -> FrozenPointDataclass:
        return FrozenPointDataclass(self.x + dx, self.y + dy)


# --------------------------------------------------------------------------- #
# Demonstracja
# --------------------------------------------------------------------------- #


def main() -> None:
    print("== Temperature ==")
    t = Temperature(25)
    print(f"{t} -> kelvin={t.kelvin}, fahrenheit={t.fahrenheit}")
    t.celsius = -273.15
    print(f"zero absolutne       -> {t}, kelvin={t.kelvin}")
    for bad in (-274, "25", True):
        try:
            Temperature(bad)
        except (TypeError, ValueError) as exc:
            print(f"Temperature({bad!r:>7}) -> {type(exc).__name__}: {exc}")
    print()

    print("== Rectangle ==")
    rect = Rectangle(3, 4)
    print(f"{rect} -> area={rect.area}, perimeter={rect.perimeter}, "
          f"is_square={rect.is_square}")
    bigger = rect.scale(2)
    print(f"po scale(2)          -> {bigger} (oryginał: {rect})")
    try:
        rect.area = 100
    except AttributeError as exc:
        print(f"rect.area = 100      -> AttributeError: {exc}")
    print()

    print("== Player ==")
    player = Player("Aragorn")
    print(f"{player} is_alive={player.is_alive}")
    player.take_damage(30)
    print(f"take_damage(30)      -> {player}")
    player.heal(1000)  # clamp do MAX_HP
    print(f"heal(1000)           -> {player} (clamp)")
    player.take_damage(1000)
    print(f"take_damage(1000)    -> {player}, is_alive={player.is_alive}")
    try:
        player.hp = 150
    except ValueError as exc:
        print(f"player.hp = 150      -> ValueError: {exc}")
    print()

    print("== FrozenPoint ==")
    p = FrozenPoint(1, 2)
    print(f"{p} -> shift(1, 1) = {p.shift(1, 1)}")
    try:
        p.x = 10
    except AttributeError as exc:
        print(f"p.x = 10             -> AttributeError: {exc}")
    print(f"FrozenPointDataclass(1, 2) == FrozenPoint(1, 2)? "
          f"{FrozenPointDataclass(1, 2) == FrozenPoint(1, 2)} (różne typy!)")


if __name__ == "__main__":
    main()
