"""Zadania do samodzielnego wykonania - temat 03 (kompozycja).

Rozwiązania: ``solutions_03.py``. Testy: ``test_solutions_03.py``.

    python -m pytest src/01-OOP/03-composition/exercises/test_solutions_03.py -v

Motyw przewodni: **obiekt, który sam tworzy sobie zależności, jest trudny do
przetestowania; obiekt, który je przyjmuje - jest łatwy.** W zadaniach 2 i 3
zobaczysz dokładnie ten mechanizm.
"""

from __future__ import annotations

from typing import Protocol

# --------------------------------------------------------------------------- #
# Zadanie 1 - kompozycja i delegacja (3 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``Engine`` oraz ``Car``, gdzie ``Car`` **zawiera** silnik.
#
# ``Engine``:
#  * konstruktor ``Engine(power_kw: float, consumption_l_per_100km: float)``,
#  * obie wartości muszą być dodatnie -> ``ValueError``,
#  * właściwości tylko do odczytu ``power_kw``, ``consumption_l_per_100km``,
#  * ``__repr__`` -> ``Engine(power_kw=110.0, consumption_l_per_100km=5.5)``.
#
# ``Car``:
#  * konstruktor ``Car(model: str, engine: Engine, tank_l: float = 50.0)``,
#    który **przyjmuje** silnik (wstrzykiwanie zależności!), a nie tworzy go,
#  * ``fuel_l`` - właściwość z setterem: ``0 <= fuel_l <= tank_l`` inaczej
#    ``ValueError``; ``tank_l`` musi być dodatnie,
#  * ``range_km`` - właściwość wyliczana: ``fuel_l / consumption * 100``,
#  * ``refuel(liters: float) -> float`` - dolewa paliwo, ale nie ponad
#    ``tank_l`` (nasycenie), zwraca stan po dolaniu; dla ``liters <= 0``
#    podnosi ``ValueError``,
#  * ``drive(km: float) -> float`` - zużywa paliwo; jeżeli zabraknie paliwa na
#    pokonanie całego dystansu, podnosi ``ValueError`` i **nie zmienia stanu**,
#  * ``__repr__`` zawiera model, poziom paliwa i silnik.
#
# Podpowiedzi:
#  * delegacja: ``Car`` nie duplikuje logiki silnika, tylko korzysta z jego
#    właściwości (``self.engine.consumption_l_per_100km``),
#  * „nie zmienia stanu przy błędzie” testujemy tak: zapisz stan, wywołaj
#    operację w ``pytest.raises``, porównaj stan,
#  * zapotrzebowanie na paliwo: ``km * consumption / 100``.


class Engine:
    def __init__(self, power_kw: float, consumption_l_per_100km: float) -> None:
        raise NotImplementedError("Zadanie 1: zaimplementuj Engine")


class Car:
    def __init__(self, model: str, engine: Engine, tank_l: float = 50.0) -> None:
        raise NotImplementedError("Zadanie 1: zaimplementuj Car")


# --------------------------------------------------------------------------- #
# Zadanie 2 - kompozycja z protokołem i atrapą (3 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``AlertService``, który wysyła alerty przez **wstrzyknięty**
# notifier zgodny z protokołem ``Notifier``.
#
# Wymagania:
#  * ``AlertService(notifier: Notifier)``,
#  * ``alert(message: str, level: str = "info") -> str``:
#      - odrzuca pusty ``message`` -> ``ValueError`` (komunikat: "empty"),
#      - odrzuca ``level`` spoza ``{"info", "warning", "critical"}`` ->
#        ``ValueError`` (komunikat: "unknown level"),
#      - formatuje tekst jako ``f"[{level.upper()}] {message}"`` i przekazuje
#        do ``notifier.send(...)``, zwracając jego wynik,
#  * ``history`` - lista wysłanych tekstów w kolejności (właściwość tylko do
#    odczytu, zwracająca **kopię** listy!),
#  * ``critical(message) -> str`` - skrót wołający ``alert(message, "critical")``.
#
# Dodatkowo napisz ``RecordingNotifier``: minimalną ręczną atrapę (test double),
# która zapisuje otrzymane wiadomości i potrafi zwrócić ustaloną odpowiedź:
#  * ``RecordingNotifier(reply: str = "ok")``,
#  * ``send(message: str) -> str`` zapisuje wiadomość w ``self.sent`` i
#    zwraca ``self.reply``.
#
# Podpowiedzi:
#  * ``AlertService`` **nie może** tworzyć notifiera samodzielnie,
#  * „zwróć kopię listy” to ``return list(self._history)`` - chroni
#    wewnętrzny stan przed modyfikacją z zewnątrz (test na to też napiszemy),
#  * asercja ``notifier.sent == ["[WARNING] niski stan paliwa"]`` to
#    sprawdzenie *interakcji* (czy współpracownik został zawołany).


class Notifier(Protocol):
    def send(self, message: str) -> str:
        ...


class AlertService:
    def __init__(self, notifier: Notifier) -> None:
        raise NotImplementedError("Zadanie 2: zaimplementuj konstruktor")

    def alert(self, message: str, level: str = "info") -> str:
        raise NotImplementedError("Zadanie 2: zaimplementuj alert")

    def critical(self, message: str) -> str:
        raise NotImplementedError("Zadanie 2: zaimplementuj critical")

    @property
    def history(self) -> list[str]:
        raise NotImplementedError("Zadanie 2: zaimplementuj history")


class RecordingNotifier:
    def __init__(self, reply: str = "ok") -> None:
        raise NotImplementedError("Zadanie 2: zaimplementuj RecordingNotifier")


# --------------------------------------------------------------------------- #
# Zadanie 3 - refaktoryzacja do wstrzykiwania zależności (3 pkt)
# --------------------------------------------------------------------------- #
# Poniższy kod udaje serwis pogodowy, który sam tworzy klienta HTTP. Napisz
# jego wersję testowalną.
#
#     class HttpWeatherService:
#         def __init__(self, api_url: str):
#             self.api_url = api_url
#             self.client = HttpClient()      # <- zależność tworzona w środku!
#
#         def temperature(self, city: str) -> float:
#             raw = self.client.get(f"{self.api_url}/weather/{city}")
#             return float(json.loads(raw)["temp_c"])
#
# Wymagania dla wersji poprawionej (``WeatherService``):
#  * ``WeatherService(client: HttpClientPort)`` - klient wstrzykiwany,
#  * ``temperature(city: str) -> float``:
#      - czyta wartość z JSON-a zwróconego przez klienta (pole ``"temp_c"``),
#      - gdy klucza brakuje, podnosi ``ValueError`` z komunikatem "temp_c missing",
#      - przyjmuje ``city`` niepuste (inaczej ``ValueError``),
#  * ``is_freezing(city: str) -> bool`` -> ``temperature(city) < 0``,
#  * ``HttpClientPort`` to ``Protocol`` z metodą ``get(path: str) -> str``,
#  * napisz ``FakeHttpClient`` (atrapa): ``FakeHttpClient(responses: dict[str, str])``,
#    która zwraca przygotowaną odpowiedź, a dla nieznanej ścieżki podnosi
#    ``KeyError``.
#
# W komentarzu ``# DLACZEGO:`` (2-3 zdania) wyjaśnij, co konkretnie zyskują
# testy dzięki wstrzyknięciu klienta.
#
# Podpowiedzi:
#  * ``HttpClientPort`` definiuj przez ``typing.Protocol`` (jak ``Notifier``),
#  * do parsowania użyj ``json.loads``,
#  * atrapa nie potrzebuje żadnego dziedziczenia - wystarczy metoda ``get``.


class HttpClientPort(Protocol):
    def get(self, path: str) -> str:
        ...


class WeatherService:
    def __init__(self, client: HttpClientPort) -> None:
        raise NotImplementedError("Zadanie 3: zaimplementuj konstruktor")

    def temperature(self, city: str) -> float:
        raise NotImplementedError("Zadanie 3: zaimplementuj temperature")

    def is_freezing(self, city: str) -> bool:
        raise NotImplementedError("Zadanie 3: zaimplementuj is_freezing")


class FakeHttpClient:
    def __init__(self, responses: dict[str, str]) -> None:
        raise NotImplementedError("Zadanie 3: zaimplementuj FakeHttpClient")


# --------------------------------------------------------------------------- #
# Zadanie 4 (dla chętnych) - agregacja elementów kompozycji (2 pkt)
# --------------------------------------------------------------------------- #
# Zaimplementuj ``Playlist`` zawierającą wiele ``Track``.
#
# Wymagania:
#  * ``Track(title: str, artist: str, duration_s: int)`` - ``duration_s > 0``,
#  * ``Playlist(name: str)`` z metodami ``add(track)`` i ``remove(title)``
#    (usuwa pierwszy utwór o tytule; brak -> ``KeyError``),
#  * ``total_duration_s``, ``longest_track`` (zwraca ``Track`` lub ``None``
#    dla pustej playlisty), ``by_artist(artist)`` (lista utworów, zachowana
#    kolejność), ``__len__`` i ``__iter__``.
#
# Podpowiedzi:
#  * ``longest_track`` najprościej: ``max(self._tracks, key=..., default=None)``,
#  * ``__iter__`` pozwala pisać ``for track in playlist`` oraz używać
#    ``list(playlist)`` w testach,
#  * ``sum()`` z wyrażeniem generatorowym to najkrótsza droga do agregatu.
