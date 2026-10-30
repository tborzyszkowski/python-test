"""Mock, MagicMock, patch i monkeypatch w malych przykladach."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, Mock, patch


class AlertService:
    """Usługa alertów z wysyłką przez zależność sender."""
    def __init__(self, sender) -> None:
        self.sender = sender

    def alert(self, message: str) -> str:
        return self.sender.send(message)


def read_mode() -> str:
    """Odczytaj tryb pracy z zmiennej środowiskowej."""
    return os.environ.get("APP_MODE", "production")


def demo_mock() -> None:
    """Demonstruje Mock: zwrócenie wartości i sprawdzenie interakcji."""
    sender = Mock()
    sender.send.return_value = "accepted"
    assert AlertService(sender).alert("hello") == "accepted"
    sender.send.assert_called_once_with("hello")
    print("Mock interaction:", sender.mock_calls)


def demo_magic_mock() -> None:
    """Demonstruje MagicMock: wspiera magiczne metody jak __len__."""
    cache = MagicMock()
    cache.__len__.return_value = 2
    print("MagicMock len:", len(cache))


def demo_patch() -> None:
    """Demonstruje patch: tymczasowa podmiana funkcji."""
    with patch("mock_tools.read_mode", return_value="test") as mocked:
        print("patched mode:", read_mode())
        mocked.assert_called_once_with()


def main() -> None:
    """Uruchom wszystkie demo narzędzi Mock, MagicMock i patch."""
    demo_mock()
    demo_magic_mock()
    demo_patch()
    print("real mode:", read_mode())


if __name__ == "__main__":
    main()
