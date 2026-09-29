"""Testy sprawdzające rozwiązania zadań - temat 03 (kompozycja).

    python -m pytest src/01-OOP/03-composition/exercises/test_solutions_03.py -v

Trzy rodzaje asercji, które tu ćwiczymy:

1. **Stan** - ``assert car.fuel_l == ...`` (co się zmieniło w obiekcie).
2. **Interakcja** - ``assert notifier.sent == [...]`` (kogo zawołaliśmy i z czym).
3. **Brak zmiany stanu przy błędzie** - najważniejsza asercja dla operacji,
   które mogą zawieść w połowie.
"""

from __future__ import annotations

import json

import pytest

from solutions_03 import (
    AlertService,
    Car,
    Engine,
    FakeHttpClient,
    Playlist,
    RecordingNotifier,
    Track,
    WeatherService,
)

# --------------------------------------------------------------------------- #
# Zadanie 1 - Engine i Car
# --------------------------------------------------------------------------- #


@pytest.fixture
def engine() -> Engine:
    return Engine(power_kw=110, consumption_l_per_100km=5.5)


@pytest.fixture
def car(engine: Engine) -> Car:
    return Car("Skoda", engine, tank_l=50)


def test_engine_validates_parameters():
    with pytest.raises(ValueError, match="power_kw"):
        Engine(0, 5.5)
    with pytest.raises(ValueError, match="consumption"):
        Engine(110, 0)


def test_engine_repr_and_equality():
    assert repr(Engine(110, 5.5)) == "Engine(power_kw=110.0, consumption_l_per_100km=5.5)"
    assert Engine(110, 5.5) == Engine(110, 5.5)
    assert Engine(110, 5.5) != Engine(110, 6.0)


def test_car_starts_with_full_tank(car):
    assert car.fuel_l == pytest.approx(50.0)
    assert car.model == "Skoda"


def test_car_range_delegates_to_engine(car):
    # 50 l przy 5.5 l/100 km -> 909.09 km; gdyby Car miał własną stałą, test padnie
    assert car.range_km == pytest.approx(50 / 5.5 * 100)


def test_car_uses_injected_engine_not_a_copy(car, engine):
    assert car.engine is engine


def test_car_accepts_engine_subclass(car):
    class EcoEngine(Engine):
        pass

    eco = Car("Eco", EcoEngine(70, 3.0), tank_l=40)
    assert eco.range_km == pytest.approx(40 / 3.0 * 100)


def test_car_rejects_non_engine():
    with pytest.raises(TypeError, match="Engine"):
        Car("Skoda", engine="to nie silnik")  # type: ignore[arg-type]


def test_drive_consumes_fuel(car):
    assert car.drive(100) == pytest.approx(50 - 5.5)


def test_drive_does_not_change_state_when_fuel_is_missing(car):
    with pytest.raises(ValueError, match="not enough fuel"):
        car.drive(10_000)
    assert car.fuel_l == pytest.approx(50.0)  # stan nietknięty


@pytest.mark.parametrize("km", [0, -5])
def test_drive_rejects_non_positive_distance(car, km):
    with pytest.raises(ValueError, match="positive"):
        car.drive(km)


def test_refuel_is_clamped_to_tank(car):
    car.drive(500)
    assert car.fuel_l < car.tank_l
    assert car.refuel(1_000) == pytest.approx(car.tank_l)   # nasycenie do baku
    assert car.fuel_l <= car.tank_l


def test_refuel_rejects_non_positive_liters(car):
    with pytest.raises(ValueError, match="positive"):
        car.refuel(-1)


def test_fuel_setter_validates_range(car):
    with pytest.raises(ValueError, match="out of range"):
        car.fuel_l = -1
    with pytest.raises(ValueError, match="out of range"):
        car.fuel_l = 51


# --------------------------------------------------------------------------- #
# Zadanie 2 - AlertService + RecordingNotifier
# --------------------------------------------------------------------------- #


def test_alert_formats_and_delegates_to_notifier():
    notifier = RecordingNotifier(reply="wysłano")
    service = AlertService(notifier)

    result = service.alert("niski stan paliwa", "warning")

    assert result == "wysłano"                                   # zwrotka od atrapy
    assert notifier.sent == ["[WARNING] niski stan paliwa"]      # asercja interakcji
    assert service.history == ["[WARNING] niski stan paliwa"]


def test_default_level_is_info():
    notifier = RecordingNotifier()
    AlertService(notifier).alert("gotowe")
    assert notifier.sent == ["[INFO] gotowe"]


def test_critical_uses_critical_level():
    notifier = RecordingNotifier()
    AlertService(notifier).critical("awaria")
    assert notifier.sent == ["[CRITICAL] awaria"]


@pytest.mark.parametrize("level", ["debug", "INFO", ""])
def test_unknown_level_is_rejected(level):
    service = AlertService(RecordingNotifier())
    with pytest.raises(ValueError, match="unknown level"):
        service.alert("cokolwiek", level)


def test_empty_message_is_rejected():
    notifier = RecordingNotifier()
    service = AlertService(notifier)
    with pytest.raises(ValueError, match="empty"):
        service.alert("")
    assert notifier.sent == []          # nic nie wysłaliśmy - poprawne zachowanie
    assert service.history == []


def test_history_returns_a_copy():
    service = AlertService(RecordingNotifier())
    service.alert("pierwszy")
    history = service.history
    history.append("podrobiony wpis")   # próba modyfikacji stanu z zewnątrz
    assert service.history == ["[INFO] pierwszy"]


def test_service_uses_injected_notifier():
    notifier = RecordingNotifier()
    service = AlertService(notifier)
    assert service._notifier is notifier  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# Zadanie 3 - WeatherService + FakeHttpClient
# --------------------------------------------------------------------------- #


@pytest.fixture
def weather_client() -> FakeHttpClient:
    return FakeHttpClient(
        {
            "/weather/Warszawa": json.dumps({"temp_c": -3.5}),
            "/weather/Gdansk": json.dumps({"temp_c": 7.0}),
            "/weather/Lodz": json.dumps({"humidity": 80}),
        }
    )


def test_temperature_parses_json(weather_client):
    service = WeatherService(weather_client)
    assert service.temperature("Warszawa") == pytest.approx(-3.5)
    assert weather_client.requested == ["/weather/Warszawa"]


def test_is_freezing(weather_client):
    service = WeatherService(weather_client)
    assert service.is_freezing("Warszawa") is True
    assert service.is_freezing("Gdansk") is False


def test_zero_temperature_is_not_freezing():
    client = FakeHttpClient({"/weather/X": json.dumps({"temp_c": 0})})
    assert WeatherService(client).is_freezing("X") is False


def test_missing_field_raises_value_error(weather_client):
    service = WeatherService(weather_client)
    with pytest.raises(ValueError, match="temp_c missing"):
        service.temperature("Lodz")


def test_empty_city_is_rejected(weather_client):
    service = WeatherService(weather_client)
    with pytest.raises(ValueError, match="city"):
        service.temperature("")
    assert weather_client.requested == []   # nie zawracamy głowy klientowi HTTP


def test_unknown_path_in_fake_client_is_loud():
    service = WeatherService(FakeHttpClient({}))
    with pytest.raises(KeyError, match="no response"):
        service.temperature("Krakow")


# --------------------------------------------------------------------------- #
# Zadanie 4 - Playlist
# --------------------------------------------------------------------------- #


@pytest.fixture
def playlist() -> Playlist:
    result = Playlist("Trening")
    result.add(Track("Eye of the Tiger", "Survivor", 245))
    result.add(Track("Stronger", "Kanye West", 312))
    result.add(Track("Believer", "Imagine Dragons", 204))
    return result


def test_track_validation():
    with pytest.raises(ValueError, match="duration_s"):
        Track("Pusty", "Nikt", 0)
    with pytest.raises(ValueError, match="title"):
        Track("", "Nikt", 100)


def test_playlist_aggregates_duration(playlist):
    assert playlist.total_duration_s == 245 + 312 + 204
    assert len(playlist) == 3


def test_longest_track(playlist):
    assert playlist.longest_track == Track("Stronger", "Kanye West", 312)


def test_longest_track_of_empty_playlist_is_none():
    assert Playlist("Pusta").longest_track is None


def test_by_artist_keeps_order():
    playlist = Playlist("Mix")
    playlist.add(Track("A", "X", 100))
    playlist.add(Track("B", "Y", 100))
    playlist.add(Track("C", "X", 100))
    assert [t.title for t in playlist.by_artist("X")] == ["A", "C"]
    assert playlist.by_artist("Z") == []


def test_remove_returns_track_and_reports_missing(playlist):
    removed = playlist.remove("Believer")
    assert removed.title == "Believer"
    assert len(playlist) == 2
    with pytest.raises(KeyError, match="Believer"):
        playlist.remove("Believer")


def test_playlist_is_iterable(playlist):
    assert [track.title for track in playlist] == [
        "Eye of the Tiger",
        "Stronger",
        "Believer",
    ]


def test_playlist_rejects_foreign_objects(playlist):
    with pytest.raises(TypeError, match="Track"):
        playlist.add("nie utwór")  # type: ignore[arg-type]
