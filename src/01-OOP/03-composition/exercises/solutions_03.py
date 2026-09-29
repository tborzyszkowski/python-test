"""Wzorcowe rozwiązania - temat 03 (kompozycja).

Demonstracja::

    python src/01-OOP/03-composition/exercises/solutions_03.py
"""

from __future__ import annotations

import json
from collections.abc import Iterator

_EPS = 1e-9

# --------------------------------------------------------------------------- #
# Rozwiązanie 1 - Engine + Car (kompozycja i delegacja)
# --------------------------------------------------------------------------- #


class Engine:
    """Silnik spalinowy o zadanej mocy i apetycie na paliwo."""

    def __init__(self, power_kw: float, consumption_l_per_100km: float) -> None:
        if power_kw <= 0:
            raise ValueError(f"power_kw must be positive, got {power_kw}")
        if consumption_l_per_100km <= 0:
            raise ValueError(
                f"consumption_l_per_100km must be positive, got {consumption_l_per_100km}"
            )
        self._power_kw = float(power_kw)
        self._consumption = float(consumption_l_per_100km)

    @property
    def power_kw(self) -> float:
        return self._power_kw

    @property
    def consumption_l_per_100km(self) -> float:
        return self._consumption

    def __repr__(self) -> str:
        return (f"Engine(power_kw={self._power_kw!r}, "
                f"consumption_l_per_100km={self._consumption!r})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Engine):
            return NotImplemented
        return (self._power_kw, self._consumption) == (other._power_kw, other._consumption)


class Car:
    """Samochód, który *ma* silnik (kompozycja), a nie *jest* silnikiem."""

    def __init__(self, model: str, engine: Engine, tank_l: float = 50.0) -> None:
        if not model:
            raise ValueError("model must not be empty")
        if not isinstance(engine, Engine):
            raise TypeError(f"engine must be an Engine, got {type(engine).__name__}")
        if tank_l <= 0:
            raise ValueError(f"tank_l must be positive, got {tank_l}")

        self.model = model
        self.engine = engine          # wstrzyknięta zależność
        self.tank_l = float(tank_l)
        self._fuel_l = float(tank_l)  # wyjeżdża z pełnym bakiem

    # --- stan paliwa ---------------------------------------------------- #
    @property
    def fuel_l(self) -> float:
        return self._fuel_l

    @fuel_l.setter
    def fuel_l(self, value: float) -> None:
        if not 0 <= value <= self.tank_l + _EPS:
            raise ValueError(f"fuel_l out of range 0..{self.tank_l}: {value}")
        self._fuel_l = float(value)

    # --- delegacja do współpracownika ---------------------------------- #
    @property
    def range_km(self) -> float:
        """Zasięg liczony z zużycia silnika (Car nie zna tej reguły sam)."""
        return self._fuel_l / self.engine.consumption_l_per_100km * 100

    def refuel(self, liters: float) -> float:
        if liters <= 0:
            raise ValueError(f"liters must be positive, got {liters}")
        self._fuel_l = min(self.tank_l, self._fuel_l + liters)
        return self._fuel_l

    def drive(self, km: float) -> float:
        """Przejedź ``km``. Przy braku paliwa podnosi błąd i NIE zmienia stanu."""
        if km <= 0:
            raise ValueError(f"distance must be positive, got {km}")
        needed = km * self.engine.consumption_l_per_100km / 100
        if needed > self._fuel_l + _EPS:
            raise ValueError(
                f"not enough fuel: need {needed:.3f} l, have {self._fuel_l:.3f} l"
            )
        self._fuel_l -= needed
        return self._fuel_l

    def __repr__(self) -> str:
        return (f"Car(model={self.model!r}, fuel_l={self._fuel_l!r}, "
                f"engine={self.engine!r})")


# --------------------------------------------------------------------------- #
# Rozwiązanie 2 - AlertService z wstrzykniętym notifierem
# --------------------------------------------------------------------------- #

_KNOWN_LEVELS = ("info", "warning", "critical")


class AlertService:
    """Serwis alertów: logika własna + delegacja wysyłki do notifiera."""

    def __init__(self, notifier) -> None:
        self._notifier = notifier
        self._history: list[str] = []

    def alert(self, message: str, level: str = "info") -> str:
        if not message:
            raise ValueError("message must not be empty")
        if level not in _KNOWN_LEVELS:
            raise ValueError(f"unknown level: {level!r}")
        text = f"[{level.upper()}] {message}"
        result = self._notifier.send(text)
        self._history.append(text)
        return result

    def critical(self, message: str) -> str:
        return self.alert(message, "critical")

    @property
    def history(self) -> list[str]:
        # Kopia! Inaczej wołający mógłby dopisać coś do naszej historii.
        return list(self._history)

    def __repr__(self) -> str:
        return f"AlertService(notifier={self._notifier!r}, sent={len(self._history)})"


class RecordingNotifier:
    """Ręczna atrapa (spy): zapisuje wywołania i zwraca ustaloną odpowiedź."""

    def __init__(self, reply: str = "ok") -> None:
        self.reply = reply
        self.sent: list[str] = []

    def send(self, message: str) -> str:
        self.sent.append(message)
        return self.reply

    def __repr__(self) -> str:
        return f"RecordingNotifier(sent={self.sent!r})"


# --------------------------------------------------------------------------- #
# Rozwiązanie 3 - WeatherService z wstrzykniętym klientem HTTP
# --------------------------------------------------------------------------- #
# DLACZEGO: wstrzyknięcie klienta sprawia, że test nie wykonuje żadnego
# wejścia/wyjścia - jest natychmiastowy i deterministyczny (brak sieci, brak
# limitów API, brak zmienności pogody). Możemy też łatwo zasymulować sytuacje
# trudne do wywołania w rzeczywistości (brak pola w JSON, błąd 500), bo
# wystarczy przygotować inną odpowiedź atrapy. Bez wstrzykiwania testy
# musiałyby działać na prawdziwym API, czyli być wolne i niestabilne.


class WeatherService:
    """Serwis pogodowy czytający dane z klienta zgodnego z ``HttpClientPort``."""

    def __init__(self, client) -> None:
        self._client = client

    def temperature(self, city: str) -> float:
        if not city:
            raise ValueError("city must not be empty")
        raw = self._client.get(f"/weather/{city}")
        payload = json.loads(raw)
        if "temp_c" not in payload:
            raise ValueError(f"temp_c missing in response for {city!r}")
        return float(payload["temp_c"])

    def is_freezing(self, city: str) -> bool:
        return self.temperature(city) < 0

    def __repr__(self) -> str:
        return f"WeatherService(client={self._client!r})"


class FakeHttpClient:
    """Atrapa klienta HTTP: odpowiedzi podane z góry, bez sieci."""

    def __init__(self, responses: dict[str, str]) -> None:
        self.responses = dict(responses)
        self.requested: list[str] = []

    def get(self, path: str) -> str:
        self.requested.append(path)
        try:
            return self.responses[path]
        except KeyError:
            raise KeyError(f"FakeHttpClient has no response for {path!r}") from None

    def __repr__(self) -> str:
        return f"FakeHttpClient(responses={self.responses!r})"


# --------------------------------------------------------------------------- #
# Rozwiązanie 4 (dla chętnych) - Playlist jako agregacja
# --------------------------------------------------------------------------- #


class Track:
    """Pojedynczy utwór."""

    def __init__(self, title: str, artist: str, duration_s: int) -> None:
        if not title:
            raise ValueError("title must not be empty")
        if duration_s <= 0:
            raise ValueError(f"duration_s must be positive, got {duration_s}")
        self.title = title
        self.artist = artist
        self.duration_s = duration_s

    def __repr__(self) -> str:
        return f"Track(title={self.title!r}, artist={self.artist!r}, duration_s={self.duration_s})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return NotImplemented
        return (self.title, self.artist, self.duration_s) == (
            other.title, other.artist, other.duration_s,
        )


class Playlist:
    """Lista odtwarzania: agreguje utwory i liczy statystyki."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._tracks: list[Track] = []

    def add(self, track: Track) -> None:
        if not isinstance(track, Track):
            raise TypeError(f"expected Track, got {type(track).__name__}")
        self._tracks.append(track)

    def remove(self, title: str) -> Track:
        for index, track in enumerate(self._tracks):
            if track.title == title:
                return self._tracks.pop(index)
        raise KeyError(f"no track titled {title!r}")

    @property
    def total_duration_s(self) -> int:
        return sum(track.duration_s for track in self._tracks)

    @property
    def longest_track(self) -> Track | None:
        return max(self._tracks, key=lambda t: t.duration_s, default=None)

    def by_artist(self, artist: str) -> list[Track]:
        return [track for track in self._tracks if track.artist == artist]

    def __len__(self) -> int:
        return len(self._tracks)

    def __iter__(self) -> Iterator[Track]:
        return iter(self._tracks)

    def __repr__(self) -> str:
        return f"Playlist(name={self.name!r}, tracks={len(self._tracks)}, " \
               f"total_duration_s={self.total_duration_s})"


# --------------------------------------------------------------------------- #
# Demonstracja
# --------------------------------------------------------------------------- #


def main() -> None:
    print("== 1. Car + Engine ==")
    car = Car("Skoda", Engine(110, 5.5), tank_l=50)
    print(f"{car}")
    print(f"range_km             -> {car.range_km:.1f}")
    car.drive(100)
    print(f"po drive(100)        -> fuel_l={car.fuel_l:.2f}, range_km={car.range_km:.1f}")
    print(f"refuel(10)           -> {car.refuel(10):.2f}")
    print(f"refuel(1000)         -> {car.refuel(1000):.2f} (nasycenie do baku)")
    try:
        car.drive(10000)
    except ValueError as exc:
        print(f"drive(10000)         -> ValueError: {exc}")
    print()

    print("== 2. AlertService + RecordingNotifier ==")
    notifier = RecordingNotifier(reply="wysłano")
    alerts = AlertService(notifier)
    print(f"alert(...)           -> {alerts.alert('niski stan paliwa', 'warning')}")
    print(f"critical(...)        -> {alerts.critical('silnik przegrzany')}")
    print(f"notifier.sent        -> {notifier.sent}")
    print(f"history              -> {alerts.history}")
    print()

    print("== 3. WeatherService + FakeHttpClient ==")
    client = FakeHttpClient({
        "/weather/Warszawa": json.dumps({"temp_c": -3.5}),
        "/weather/Gdansk": json.dumps({"temp_c": 7.0}),
        "/weather/Lodz": json.dumps({"humidity": 80}),
    })
    weather = WeatherService(client)
    print(f"Warszawa             -> {weather.temperature('Warszawa')} C, "
          f"is_freezing={weather.is_freezing('Warszawa')}")
    print(f"Gdansk               -> {weather.temperature('Gdansk')} C")
    try:
        weather.temperature("Lodz")
    except ValueError as exc:
        print(f"Lodz                 -> ValueError: {exc}")
    print(f"client.requested     -> {client.requested}")
    print()

    print("== 4. Playlist ==")
    playlist = Playlist("Trening")
    playlist.add(Track("Eye of the Tiger", "Survivor", 245))
    playlist.add(Track("Stronger", "Kanye West", 312))
    playlist.add(Track("Believer", "Imagine Dragons", 204))
    print(f"{playlist}")
    print(f"longest_track        -> {playlist.longest_track}")
    print(f"by_artist('Survivor')-> {playlist.by_artist('Survivor')}")


if __name__ == "__main__":
    main()
