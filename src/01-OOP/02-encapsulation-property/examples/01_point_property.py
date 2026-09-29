"""Przykład 01 - od publicznych atrybutów do ``@property``.

Uruchomienie::

    python src/01-OOP/02-encapsulation-property/examples/01_point_property.py

Porównujemy dwie wersje tej samej klasy ``Point``:

* ``NaivePoint`` - publiczne atrybuty ``x``/``y``: można wpisać cokolwiek,
  obiekt bywa w stanie, który „nie ma sensu” (np. ``x = "abc"``).
* ``Point`` - pola prywatne ``_x``/``_y`` za właściwościami ``x``/``y``:
  * walidacja typu i konwersja na ``float`` w *jednym* miejscu (setter),
  * konstruktor ustawia pola **przez setter**, więc nie ma drugiej ścieżki
    walidacji, której można zapomnieć,
  * ``magnitude`` jest właściwością **wyliczaną i tylko do odczytu** - zawsze
    zgodna ze stanem, bo nie da się jej „rozjechać”.

Wniosek dla testów: obiekt, który nie potrafi wejść w niepoprawny stan,
nie wymaga testów na niepoprawny stan. Testujemy wtedy:

1. że setter odrzuca to, co ma odrzucać,
2. że getter zwraca to, co zostało ustawione,
3. że właściwość wyliczana liczy właściwie i jest tylko do odczytu.
"""

from __future__ import annotations

import math

Number = int | float


class NaivePoint:
    """Wersja „naiwna”: publiczne atrybuty, brak walidacji."""

    def __init__(self, x: Number, y: Number) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"NaivePoint({self.x!r}, {self.y!r})"


class Point:
    """Wersja hermetyzowana: ``_x``/``_y`` + właściwości ``x``/``y``.

    Uwaga: podwójne podkreślenie (``__x``) uruchamia *name mangling* na nazwie
    ``_Point__x`` - to narzędzie ochrony przed przesłonięciem w podklasach,
    a nie „private” w rozumieniu Javy. Konwencja ``_x`` (jedno podkreślenie)
    oznacza „szczegół implementacyjny, nie dotykaj z zewnątrz”.
    """

    def __init__(self, x: Number, y: Number) -> None:
        # ŚWIADOMIE przez setter: walidacja istnieje tylko w jednym miejscu.
        self.x = x
        self.y = y

    # ------------------------------------------------------------------ #
    # x - właściwość z walidacją                                          #
    # ------------------------------------------------------------------ #
    @property
    def x(self) -> float:
        """Współrzędna x (tylko do odczytu przez getter, zmiana przez setter)."""
        return self._x

    @x.setter
    def x(self, value: Number) -> None:
        self._x = self._as_number(value, "x")

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: Number) -> None:
        self._y = self._as_number(value, "y")

    @staticmethod
    def _as_number(value: Number, name: str) -> float:
        """Walidacja wspólna dla obu współrzędnych (usuwa duplikację kodu)."""
        # bool jest podklasą int - wykluczamy jawnie, bo Point(True, False)
        # byłby cichym źródłem (1.0, 0.0). To świetny przypadek brzegowy do testu.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a real number, got {type(value).__name__}")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite, got {value!r}")
        return float(value)

    # ------------------------------------------------------------------ #
    # Właściwości wyliczane (brak settera = tylko do odczytu)             #
    # ------------------------------------------------------------------ #
    @property
    def magnitude(self) -> float:
        """Odległość od początku układu współrzędnych (zawsze aktualna)."""
        return math.hypot(self._x, self._y)

    def distance_to(self, other: "Point") -> float:
        if not isinstance(other, Point):
            raise TypeError(f"expected Point, got {type(other).__name__}")
        return math.hypot(self._x - other._x, self._y - other._y)

    def __repr__(self) -> str:
        return f"Point(x={self._x!r}, y={self._y!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self._x, self._y) == (other._x, other._y)


def demo_naive_pitfalls() -> None:
    print("== 1. Co potrafi zepsuć klasa bez hermetyzacji ==")
    naive = NaivePoint(1, 2)
    print(f"naive                -> {naive}")
    naive.x = "nie liczba"          # nikt nie protestuje...
    naive.y = [1, 2, 3]
    print(f"po 'chamskiej' zmianie -> {naive}")
    print("Klasa 'udaje', że jest poprawna - błąd ujawni się później i daleko od miejsca.")
    print()

    good = Point(1, 2)
    try:
        good.x = "nie liczba"
    except TypeError as exc:
        print(f"Point.x = 'nie liczba' -> TypeError: {exc}")
    print(f"stan obiektu bez zmian -> {good}")
    print()


def demo_property_basics() -> None:
    print("== 2. Getter, setter i konwersja typu ==")
    p = Point(3, 4)
    print(f"p                    -> {p}")
    print(f"p.x, p.y             -> {p.x!r}, {p.y!r}   (oba float, mimo int na wejściu)")
    p.x = 6                              # wywołuje setter
    print(f"po p.x = 6           -> {p}, magnitude={p.magnitude}")
    print("'p._x' istnieje (konwencja: nie używać z zewnątrz):", p._x)
    print()


def demo_read_only_derived_property() -> None:
    print("== 3. Właściwość wyliczana jest tylko do odczytu ==")
    p = Point(3, 4)
    print(f"magnitude            -> {p.magnitude}     # 3-4-5 - trójka pitagorejska")
    try:
        p.magnitude = 10
    except AttributeError as exc:
        print(f"p.magnitude = 10     -> AttributeError: {exc}")
    print("Nie da się rozjechać stanu z wyliczeniem - i to jest cała korzyść.")
    print()


def demo_edge_cases() -> None:
    print("== 4. Przypadki brzegowe (materiał na testy) ==")
    for value in (True, "5", float("nan"), float("inf"), 2 + 3j):
        try:
            Point(value, 0)
        except (TypeError, ValueError) as exc:
            print(f"Point({value!r:>10}, 0) -> {type(exc).__name__}: {exc}")
    print()
    zero = Point(0, 0)
    print(f"Point(0, 0)          -> {zero}, magnitude={zero.magnitude}")
    print()


def main() -> None:
    demo_naive_pitfalls()
    demo_property_basics()
    demo_read_only_derived_property()
    demo_edge_cases()


if __name__ == "__main__":
    main()
