from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import mock_tools
import pytest
from mock_tools import AlertService


def test_return_value_is_separate_from_interaction():
    sender = Mock()
    sender.send.return_value = "accepted"
    service = AlertService(sender)

    result = service.alert("hello")

    assert result == "accepted"
    sender.send.assert_called_once_with("hello")


def test_mock_spec_rejects_unknown_api():
    sender = Mock(spec=["send"])
    with pytest.raises(AttributeError):
        sender.receive  # noqa: B018


def test_magic_mock_supports_magic_methods():
    cache = MagicMock()
    cache.__len__.return_value = 3
    assert len(cache) == 3


def test_patch_replaces_symbol_temporarily():
    with patch("mock_tools.read_mode", return_value="test") as mocked:
        assert mock_tools.read_mode() == "test"
        mocked.assert_called_once_with()


def test_patch_is_restored_after_context():
    with patch("mock_tools.read_mode", return_value="test"):
        pass
    assert mock_tools.read_mode() in {"production", "test"}


def test_monkeypatch_changes_environment_temporarily(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert mock_tools.read_mode() == "test"
