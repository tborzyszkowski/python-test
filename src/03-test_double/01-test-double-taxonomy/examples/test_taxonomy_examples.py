from __future__ import annotations

import pytest
from taxonomy_examples import (
    AlertService,
    InMemoryNotifier,
    RecordingNotifier,
    StubNotifier,
    UnusedNotifier,
)


def test_stub_controls_return_value():
    assert AlertService(StubNotifier("queued")).alert("hello") == "queued"


def test_fake_has_working_simplified_state():
    notifier = InMemoryNotifier()
    AlertService(notifier).alert("hello")
    assert notifier.messages == ["hello"]


def test_spy_records_interaction():
    notifier = RecordingNotifier()
    AlertService(notifier).alert("hello")
    assert notifier.calls == [("hello",)]


def test_dummy_is_not_called_for_invalid_input():
    with pytest.raises(ValueError):
        AlertService(UnusedNotifier()).alert(" ")
