from taxonomy_examples import (
    AlertService,
    InMemoryNotifier,
    RecordingNotifier,
    StubNotifier,
    UnusedNotifier,
)


def stub_alert(response: str = "accepted") -> str:
    return AlertService(StubNotifier(response)).alert("hello")


def fake_messages() -> list[str]:
    notifier = InMemoryNotifier()
    AlertService(notifier).alert("hello")
    return notifier.messages


def spy_calls() -> list[tuple[str]]:
    notifier = RecordingNotifier()
    AlertService(notifier).alert("hello")
    return notifier.calls


__all__ = ["UnusedNotifier", "fake_messages", "spy_calls", "stub_alert"]
