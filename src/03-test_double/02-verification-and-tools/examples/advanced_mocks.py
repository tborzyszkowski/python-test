"""Zaawansowane użycie Mock: parametryzacja, side_effect, spec, MagicMock."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, Mock, PropertyMock, patch, call


# === Przykład 1: side_effect dla symulacji sekwencji i błędów ===

class DataFetcher:
    """Komponent pobierający dane z kilku prób."""

    def __init__(self, client) -> None:
        self.client = client

    def fetch_with_retry(self, url: str, max_retries: int = 3) -> dict[str, Any]:
        """Pobiera dane z ponownym próbami; rezygnuje po max_retries."""
        for attempt in range(max_retries):
            try:
                return self.client.get(url)
            except ConnectionError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed after {max_retries} retries") from e
        return {}


def demo_side_effect_sequence() -> None:
    """side_effect zwraca różne wartości w kolejnych wywołaniach."""
    client = Mock()
    # Pierwsze dwa razy blad, trzeci raz sukces
    client.get.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        {"status": "ok"}
    ]

    fetcher = DataFetcher(client)
    result = fetcher.fetch_with_retry("http://api.example.com")
    print(f"Retry result: {result}")
    assert result == {"status": "ok"}
    assert client.get.call_count == 3


# === Przykład 2: MagicMock dla protokołów (iterator, context manager, callable) ===

class StorageAdapter:
    """Adapter dla różnych rodzajów przechowywania."""

    def __init__(self, storage) -> None:
        self.storage = storage

    def process_items(self) -> list[str]:
        """Iteruje po elementach w przechowywaniu."""
        return [item.upper() for item in self.storage]

    def with_context(self) -> str:
        """Używa storage jako context manager."""
        with self.storage as ctx:
            return ctx.read()


def demo_magic_mock_iterator() -> None:
    """MagicMock automatycznie wspiera __iter__ i __enter__."""
    storage = MagicMock()
    storage.__iter__.return_value = iter(["apple", "banana"])

    adapter = StorageAdapter(storage)
    result = adapter.process_items()
    print(f"Iterated: {result}")
    assert result == ["APPLE", "BANANA"]


def demo_magic_mock_context_manager() -> None:
    """MagicMock wspiera with ... as: syntax."""
    storage = MagicMock()
    storage.__enter__.return_value.read.return_value = "secret data"

    adapter = StorageAdapter(storage)
    result = adapter.with_context()
    print(f"Context manager result: {result}")
    assert result == "secret data"


# === Przykład 3: spec dla ochrony przed literówkami ===

class UserRepository:
    def find_by_id(self, user_id: int) -> dict[str, Any]:
        raise NotImplementedError

    def save(self, user: dict) -> int:
        raise NotImplementedError

    def delete(self, user_id: int) -> bool:
        raise NotImplementedError


class UserService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_and_greet(self, name: str) -> str:
        user_id = self.repository.save({"name": name})
        return f"User {user_id}: {name}"


def demo_spec_protection() -> None:
    """spec=UserRepository chroni przed literówkami w API."""
    # Bez spec: literówka przechodzi cicho
    bad_mock = Mock()
    bad_mock.sav.return_value = 1  # literówka!
    # Powyższe nie wyrzuci błędu w Mock

    # Ze spec: literówka jest natychmiast wychwytana
    good_mock = Mock(spec=UserRepository)
    try:
        good_mock.sav.return_value = 1  # AttributeError!
    except AttributeError as e:
        print(f"spec caught typo: {e}")


# === Przykład 4: PropertyMock dla właściwości ===

class CacheManager:
    @property
    def size(self) -> int:
        raise NotImplementedError

    @property
    def hit_rate(self) -> float:
        raise NotImplementedError


class CacheService:
    def __init__(self, cache: CacheManager) -> None:
        self.cache = cache

    def get_stats(self) -> dict[str, Any]:
        """Zwraca statystyki cache; nie może być pusta."""
        if self.cache.size == 0:
            raise ValueError("Cache is empty")
        return {"size": self.cache.size, "hit_rate": self.cache.hit_rate}


def demo_property_mock() -> None:
    """PropertyMock pozwala mockować właściwości (properties)."""
    cache = Mock(spec=CacheManager)
    type(cache).size = PropertyMock(return_value=100)
    type(cache).hit_rate = PropertyMock(return_value=0.95)

    service = CacheService(cache)
    stats = service.get_stats()
    print(f"Cache stats: {stats}")
    assert stats["size"] == 100
    assert stats["hit_rate"] == 0.95


# === Przykład 5: patch.object dla metody konkretnego obiektu ===

class Logger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class DataProcessor:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def process(self, data: str) -> str:
        self.logger.log(f"Processing: {data}")
        result = data.upper()
        self.logger.log(f"Result: {result}")
        return result


def demo_patch_object() -> None:
    """patch.object mockuje metodę konkretnego obiektu instancji."""
    logger = Logger()
    processor = DataProcessor(logger)

    with patch.object(logger, "log") as mock_log:
        result = processor.process("hello")
        assert result == "HELLO"
        assert mock_log.call_count == 2
        # Sprawdź first i second call
        first_call = mock_log.call_args_list[0]
        assert "Processing" in first_call[0][0]
        print(f"patch.object captured calls: {mock_log.call_args_list}")


# === Przykład 6: patch.multiple dla kilku obiektów naraz ===

class WeatherAPI:
    def get_temperature(self, city: str) -> float:
        raise NotImplementedError


class LocationAPI:
    def get_coordinates(self, city: str) -> tuple[float, float]:
        raise NotImplementedError


class WeatherService:
    def __init__(self, weather_api: WeatherAPI, location_api: LocationAPI) -> None:
        self.weather_api = weather_api
        self.location_api = location_api

    def get_weather_with_coords(self, city: str) -> dict[str, Any]:
        """Pobiera temperaturę i współrzędne."""
        temp = self.weather_api.get_temperature(city)
        lat, lon = self.location_api.get_coordinates(city)
        return {"city": city, "temp": temp, "lat": lat, "lon": lon}


def demo_patch_multiple() -> None:
    """Mockowanie wielu zależności jednocześnie."""
    weather_api = Mock(spec=WeatherAPI)
    location_api = Mock(spec=LocationAPI)

    weather_api.get_temperature.return_value = 22.5
    location_api.get_coordinates.return_value = (52.2296, 21.0122)

    service = WeatherService(weather_api, location_api)
    result = service.get_weather_with_coords("Warsaw")
    print(f"Weather with coords: {result}")
    assert result["temp"] == 22.5


# === Przykład 7: assert_called_with i call() ===

class NotificationService:
    def __init__(self, sender) -> None:
        self.sender = sender

    def notify_users(self, user_ids: list[int], message: str) -> None:
        """Wysyła wiadomość do każdego użytkownika."""
        for user_id in user_ids:
            self.sender.send(user_id, message)


def demo_call_matching() -> None:
    """call() pozwala sformułować dokładne oczekiwanie dla każdego zavolania."""
    sender = Mock()
    service = NotificationService(sender)

    service.notify_users([1, 2, 3], "Hello")

    # Sprawdzenie każdego wołania
    sender.send.assert_has_calls([
        call(1, "Hello"),
        call(2, "Hello"),
        call(3, "Hello"),
    ])
    assert sender.send.call_count == 3
    print("call() matching verified multiple calls")


# === Przykład 8: reset_mock() dla ponownego użycia mock obiektu ===

def demo_reset_mock() -> None:
    """reset_mock() resetuje historię wołań mock obiektu."""
    sender = Mock()

    # Pierwsze użycie
    sender.send("msg1")
    assert sender.send.call_count == 1

    # Reset
    sender.reset_mock()
    assert sender.send.call_count == 0

    # Drugie użycie
    sender.send("msg2")
    assert sender.send.call_count == 1
    sender.send.assert_called_once_with("msg2")
    print("reset_mock() cleared call history")


def main() -> None:
    """Uruchom wszystkie demo."""
    print("=== 1. side_effect sequence ===")
    demo_side_effect_sequence()

    print("\n=== 2. MagicMock iterator ===")
    demo_magic_mock_iterator()

    print("\n=== 3. MagicMock context manager ===")
    demo_magic_mock_context_manager()

    print("\n=== 4. spec protection ===")
    demo_spec_protection()

    print("\n=== 5. PropertyMock ===")
    demo_property_mock()

    print("\n=== 6. patch.object ===")
    demo_patch_object()

    print("\n=== 7. patch.multiple ===")
    demo_patch_multiple()

    print("\n=== 8. call() matching ===")
    demo_call_matching()

    print("\n=== 9. reset_mock ===")
    demo_reset_mock()


if __name__ == "__main__":
    main()
