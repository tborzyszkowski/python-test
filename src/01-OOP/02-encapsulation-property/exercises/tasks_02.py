"""Zadania do samodzielnego wykonania - temat 02 (hermetyzacja i ``@property``).

Rozwiązania: ``solutions_02.py``. Testy: ``test_solutions_02.py``.

    python -m pytest src/01-OOP/02-encapsulation-property/exercises/test_solutions_02.py -v

Zasada, którą ćwiczysz w każdym zadaniu:

    **Walidacja jest w jednym miejscu, a obiekt nigdy nie wchodzi
    w niepoprawny stan - nawet na chwilę.**
"""

from __future__ import annotations

Number = int | float


# --------------------------------------------------------------------------- #
# Zadanie 1 - właściwość z walidacją i właściwości wyliczane (3 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj klasę ``Temperature``.
#
# Wymagania:
#  * pole prywatne ``_celsius``; dostęp przez właściwość ``celsius``,
#  * setter ``celsius``:
#      - przyjmuje ``int``/``float`` (odrzuca ``bool``!); w przeciwnym
#        razie podnosi ``TypeError`` z komunikatem zawierającym słowo "number",
#      - konwertuje wartość na ``float``,
#      - odrzuca wartości poniżej zera absolutnego (-273.15) podnosząc
#        ``ValueError`` (komunikat ma zawierać "absolute zero"),
#  * konstruktor ``Temperature(celsius: Number)`` ustawia pole **przez setter**
#    (jedna ścieżka walidacji!),
#  * właściwości tylko do odczytu:
#      - ``kelvin`` = ``celsius + 273.15``,
#      - ``fahrenheit`` = ``celsius * 9 / 5 + 32``,
#  * ``__repr__`` -> ``Temperature(celsius=25.0)``,
#  * ``__eq__`` porównuje temperatury z tolerancją ``1e-9`` (użyj
#    ``math.isclose``) i zwraca ``NotImplemented`` dla obcego typu.
#
# Podpowiedź: żeby „ukryć” pole użyj konwencji ``self._celsius``; odwołanie do
# ``self.celsius = value`` w ``__init__`` wywoła setter.


class Temperature:
    def __init__(self, celsius: Number) -> None:
        raise NotImplementedError("Zadanie 1: zaimplementuj konstruktor")

    @property
    def celsius(self) -> float:
        raise NotImplementedError("Zadanie 1: zaimplementuj getter celsius")

    @celsius.setter
    def celsius(self, value: Number) -> None:
        raise NotImplementedError("Zadanie 1: zaimplementuj setter celsius")

    @property
    def kelvin(self) -> float:
        raise NotImplementedError("Zadanie 1: zaimplementuj kelvin")

    @property
    def fahrenheit(self) -> float:
        raise NotImplementedError("Zadanie 1: zaimplementuj fahrenheit")


# --------------------------------------------------------------------------- #
# Zadanie 2 - walidacja w setterze + właściwości wyliczane (3 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj klasę ``Rectangle``.
#
# Wymagania:
#  * właściwości ``width`` i ``height`` z setterami walidującymi:
#      - wartość musi być liczbą (``int``/``float``, bez ``bool``) -> ``TypeError``,
#      - wartość musi być **dodatnia** -> ``ValueError`` (komunikat: "positive"),
#      - konwersja na ``float``,
#  * konstruktor ``Rectangle(width, height)`` ustawia oba pola przez settery,
#  * właściwości tylko do odczytu:
#      - ``area`` = ``width * height``,
#      - ``perimeter`` = ``2 * (width + height)``,
#      - ``is_square`` = ``math.isclose(width, height)``,
#  * ``scale(factor: Number) -> "Rectangle"`` zwraca **nowy** prostokąt
#    (nie modyfikuje bieżącego); dla ``factor <= 0`` podnosi ``ValueError``,
#  * ``__repr__`` -> ``Rectangle(width=3.0, height=4.0)``.
#
# Podpowiedzi:
#  * czy właściwość wyliczana ``area`` może być jednocześnie „zapisywalna”?
#    Nie ustawiaj settera - wtedy ``rect.area = 10`` podniesie ``AttributeError``
#    (i to jest zachowanie, które warto przetestować),
#  * ``scale`` jest metodą instancyjną, bo korzysta ze stanu obiektu.


class Rectangle:
    def __init__(self, width: Number, height: Number) -> None:
        raise NotImplementedError("Zadanie 2: zaimplementuj konstruktor")

    @property
    def width(self) -> float:
        raise NotImplementedError("Zadanie 2: zaimplementuj getter width")

    @width.setter
    def width(self, value: Number) -> None:
        raise NotImplementedError("Zadanie 2: zaimplementuj setter width")

    @property
    def height(self) -> float:
        raise NotImplementedError("Zadanie 2: zaimplementuj getter height")

    @height.setter
    def height(self, value: Number) -> None:
        raise NotImplementedError("Zadanie 2: zaimplementuj setter height")

    @property
    def area(self) -> float:
        raise NotImplementedError("Zadanie 2: zaimplementuj area")

    @property
    def perimeter(self) -> float:
        raise NotImplementedError("Zadanie 2: zaimplementuj perimeter")

    @property
    def is_square(self) -> bool:
        raise NotImplementedError("Zadanie 2: zaimplementuj is_square")

    def scale(self, factor: Number) -> Rectangle:
        raise NotImplementedError("Zadanie 2: zaimplementuj scale")


# --------------------------------------------------------------------------- #
# Zadanie 3 - refaktoryzacja kodu łamiącego niezmiennik (2 pkt)
# --------------------------------------------------------------------------- #
# Poniższa klasa ``Player`` pozwala ustawić HP na wartość spoza zakresu 0..MAX_HP,
# przez co obiekt „kłamie” o swoim stanie. Przepisz ją tak, aby niezmiennik
# ``0 <= hp <= MAX_HP`` był zawsze spełniony.
#
#     class Player:
#         MAX_HP = 100
#         def __init__(self, name, hp=100):
#             self.name = name
#             self.hp = hp          # <- publiczne pole, brak walidacji
#         def heal(self, amount):
#             self.hp += amount     # <- potrafi przekroczyć MAX_HP
#
# Wymagania dla wersji poprawionej:
#  * ``hp`` jest właściwością; setter podnosi ``ValueError``, gdy
#    ``hp < 0`` lub ``hp > MAX_HP`` (komunikat zawiera "hp out of range"),
#  * ``take_damage(amount)`` odejmuje HP, ale nie poniżej zera (clamp),
#    dla ``amount < 0`` podnosi ``ValueError``,
#  * ``heal(amount)`` dodaje HP, ale nie powyżej ``MAX_HP`` (clamp),
#    dla ``amount < 0`` podnosi ``ValueError``,
#  * ``is_alive`` (właściwość tylko do odczytu) -> ``hp > 0``.
#
# Pytanie do przemyślenia: dlaczego dla ``take_damage``/``heal`` wybieramy
# *clamp*, a dla settera ``hp`` wybieramy *wyjątek*? To decyzja projektowa -
# uzasadnij ją jednym zdaniem w komentarzu ``# DECYZJA:``.
#
# Podpowiedź: setter ustawia „stan z zewnątrz” (błąd wołającego),
# a ``heal``/``take_damage`` są operacjami *wewnętrznej* logiki gry, gdzie
# nasycenie jest naturalną semantyką („nie da się wyleczyć ponad maksimum”).


class Player:
    MAX_HP: int = 100

    def __init__(self, name: str, hp: int = 100) -> None:
        raise NotImplementedError("Zadanie 3: zaimplementuj konstruktor")

    @property
    def hp(self) -> int:
        raise NotImplementedError("Zadanie 3: zaimplementuj getter hp")

    @hp.setter
    def hp(self, value: int) -> None:
        raise NotImplementedError("Zadanie 3: zaimplementuj setter hp")

    @property
    def is_alive(self) -> bool:
        raise NotImplementedError("Zadanie 3: zaimplementuj is_alive")

    def take_damage(self, amount: int) -> int:
        raise NotImplementedError("Zadanie 3: zaimplementuj take_damage")

    def heal(self, amount: int) -> int:
        raise NotImplementedError("Zadanie 3: zaimplementuj heal")


# --------------------------------------------------------------------------- #
# Zadanie 4 (dla chętnych) - obiekt niemutowalny (2 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``FrozenPoint``: punkt, którego współrzędnych **nie da się**
# zmienić po utworzeniu.
#
# Wymagania:
#  * ``__slots__ = ("_x", "_y")`` (bez ``__dict__`` - mniej pamięci i brak
#    możliwości dodania przypadkowego atrybutu),
#  * właściwości ``x``/``y`` **bez setterów**, więc ``p.x = 1`` podnosi
#    ``AttributeError``,
#  * ``__eq__``, ``__repr__`` i ``__hash__`` (na podstawie pary współrzędnych),
#  * ``shift(dx, dy) -> "FrozenPoint"`` zwraca nowy punkt (nie mutuje).
#
# Pytanie do przemyślenia: których testów **nie musisz** już pisać, jeśli
# obiekt jest niemutowalny? (Zapisz 2-3 zdania w komentarzu ``# WNIOSEK:``.)
#
# Podpowiedź: nowoczesna alternatywa to ``@dataclass(frozen=True, slots=True)``
# - po napisaniu własnej wersji porównaj liczbę linii kodu.
