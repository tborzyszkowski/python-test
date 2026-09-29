"""Przyklady rol atrap testowych na jednej zaleznosci Notifier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> str:
        ...


class AlertService:
    def __init__(self, notifier: Notifier) -> None:
        self.notifier = notifier

    def alert(self, message: str) -> str:
        if not message.strip():
            raise ValueError("message must not be empty")
        return self.notifier.send(message.strip())


class UnusedNotifier:
    """Dummy: istnieje tylko po to, by wypelnic konstruktor."""

    def send(self, message: str) -> str:
        raise AssertionError("Dummy must not be called")


@dataclass
class StubNotifier:
    response: str = "accepted"

    def send(self, message: str) -> str:
        return self.response


class InMemoryNotifier:
    """Fake: dzialajaca uproszczona implementacja."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> str:
        self.messages.append(message)
        return "accepted"


class RecordingNotifier:
    """Spy: jawnie zapisuje wywolania."""

    def __init__(self) -> None:
        self.calls: list[tuple[str]] = []

    def send(self, message: str) -> str:
        self.calls.append((message,))
        return "accepted"


def demo() -> None:
    print("stub:", AlertService(StubNotifier()).alert("stub"))
    fake = InMemoryNotifier()
    print("fake:", AlertService(fake).alert("fake"), fake.messages)
    spy = RecordingNotifier()
    print("spy:", AlertService(spy).alert("spy"), spy.calls)
    # Dummy jest uzywany w scenariuszu, ktory nie powinien wyslac alertu.
    try:
        AlertService(UnusedNotifier()).alert("   ")
    except ValueError as exc:
        print("dummy:", exc)


if __name__ == "__main__":
    demo()
