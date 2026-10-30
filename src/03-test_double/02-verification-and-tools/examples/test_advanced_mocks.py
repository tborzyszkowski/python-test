"""Testy zaawansowanych użyć Mock."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, PropertyMock, patch, call

import pytest
from advanced_mocks import (
    CacheManager,
    CacheService,
    DataFetcher,
    DataProcessor,
    Logger,
    LocationAPI,
    NotificationService,
    StorageAdapter,
    UserRepository,
    UserService,
    WeatherAPI,
    WeatherService,
)


def test_side_effect_sequence_returns_values_then_error():
    """side_effect może zwracać wiele wartości sekwencyjnie, potem błąd."""
    client = Mock()
    client.get.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        {"status": "ok"}
    ]

    fetcher = DataFetcher(client)
    result = fetcher.fetch_with_retry("http://api.example.com")

    assert result == {"status": "ok"}
    assert client.get.call_count == 3


def test_side_effect_raises_exception_on_final_retry():
    """side_effect może rzucić wyjątek po wyczerpaniu prób."""
    client = Mock()
    client.get.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        ConnectionError("timeout"),
    ]

    fetcher = DataFetcher(client)
    with pytest.raises(RuntimeError, match="Failed after 3 retries"):
        fetcher.fetch_with_retry("http://api.example.com", max_retries=3)


def test_magic_mock_iterator_protocol():
    """MagicMock wspiera __iter__ dla pętli for."""
    storage = MagicMock()
    storage.__iter__.return_value = iter(["apple", "banana", "cherry"])

    adapter = StorageAdapter(storage)
    result = adapter.process_items()

    assert result == ["APPLE", "BANANA", "CHERRY"]


def test_magic_mock_context_manager_protocol():
    """MagicMock wspiera with ... as: protokół context manager."""
    storage = MagicMock()
    storage.__enter__.return_value.read.return_value = "context data"

    adapter = StorageAdapter(storage)
    result = adapter.with_context()

    assert result == "context data"
    storage.__enter__.assert_called_once()
    storage.__exit__.assert_called_once()


def test_spec_rejects_unknown_methods():
    """spec=UserRepository odrzuca metody które nie istnieją."""
    repository = Mock(spec=UserRepository)

    with pytest.raises(AttributeError):
        repository.sav  # literówka w "save"


def test_spec_allows_valid_methods():
    """spec=UserRepository pozwala na prawidłowe metody."""
    repository = Mock(spec=UserRepository)
    repository.save.return_value = 42

    service = UserService(repository)
    result = service.create_and_greet("Alice")

    assert "User 42" in result
    repository.save.assert_called_once_with({"name": "Alice"})


def test_property_mock_for_read_only_property():
    """PropertyMock pozwala mockować właściwości."""
    cache = Mock(spec=CacheManager)
    type(cache).size = PropertyMock(return_value=256)
    type(cache).hit_rate = PropertyMock(return_value=0.92)

    service = CacheService(cache)
    stats = service.get_stats()

    assert stats["size"] == 256
    assert stats["hit_rate"] == 0.92


def test_property_mock_can_raise_exception():
    """PropertyMock może rzucić wyjątek."""
    cache = Mock(spec=CacheManager)
    type(cache).size = PropertyMock(side_effect=RuntimeError("Cache error"))

    service = CacheService(cache)

    with pytest.raises(RuntimeError, match="Cache error"):
        service.get_stats()


def test_patch_object_mocks_method_on_instance():
    """patch.object mockuje metodę konkretnego obiektu instancji."""
    logger = Logger()
    processor = DataProcessor(logger)

    with patch.object(logger, "log") as mock_log:
        result = processor.process("hello")

        assert result == "HELLO"
        assert mock_log.call_count == 2
        # Pierwszy call: Processing
        assert "Processing" in str(mock_log.call_args_list[0])
        # Drugi call: Result
        assert "Result" in str(mock_log.call_args_list[1])


def test_notification_service_calls_sender_for_each_user():
    """call() pozwala sprawdzić każde wołanie osobno."""
    sender = Mock()
    service = NotificationService(sender)

    service.notify_users([10, 20, 30], "Alert!")

    sender.send.assert_has_calls([
        call(10, "Alert!"),
        call(20, "Alert!"),
        call(30, "Alert!"),
    ])
    assert sender.send.call_count == 3


def test_reset_mock_clears_call_history():
    """reset_mock() resetuje historię wołań."""
    sender = Mock()

    # Pierwsze wołanie
    sender.send("msg1")
    assert sender.send.call_count == 1

    # Reset
    sender.reset_mock()
    assert sender.send.call_count == 0
    assert sender.send.call_args_list == []

    # Drugie wołanie po resecie
    sender.send("msg2")
    sender.send.assert_called_once_with("msg2")


def test_magic_mock_len_and_bool():
    """MagicMock wspiera magiczne metody jak __len__ i __bool__."""
    cache = MagicMock()
    cache.__len__.return_value = 5
    cache.__bool__.return_value = True

    assert len(cache) == 5
    assert bool(cache) is True


def test_side_effect_with_callable():
    """side_effect może być funkcją, która oblicza wartość."""
    dependency = Mock()

    def compute_result(x):
        return x * 2

    dependency.calculate.side_effect = compute_result

    result = dependency.calculate(21)
    assert result == 42


def test_mock_return_value_can_be_chained():
    """Mock pozwala łańcuchować return values dla metod."""
    api = Mock()
    api.fetch.return_value.json.return_value = {"status": "ok"}

    result = api.fetch().json()

    assert result == {"status": "ok"}
    api.fetch.assert_called_once()
