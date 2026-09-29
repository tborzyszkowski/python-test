from __future__ import annotations

from unittest.mock import Mock

import pytest
from sso_registry import RecordingRegistry, SessionService, SsoRegistry


def test_spy_records_unregister_token():
    registry = RecordingRegistry()

    assert SessionService(registry).logout("token-123") is True
    assert registry.calls == [("unregister", "token-123")]


def test_spy_can_return_failure():
    registry = RecordingRegistry(result=False)

    assert SessionService(registry).logout("token-123") is False


def test_empty_token_does_not_call_spy():
    registry = RecordingRegistry()

    assert SessionService(registry).logout("   ") is False
    assert registry.calls == []


def test_mock_verifies_exact_interaction():
    registry = Mock(spec=SsoRegistry)
    registry.unregister.return_value = True

    assert SessionService(registry).logout("token-123") is True
    registry.unregister.assert_called_once_with("token-123")


def test_mock_side_effect_models_registry_failure():
    registry = Mock(spec=SsoRegistry)
    registry.unregister.side_effect = ConnectionError("registry unavailable")

    with pytest.raises(ConnectionError, match="unavailable"):
        SessionService(registry).logout("token-123")


def test_mock_is_not_called_for_empty_token():
    registry = Mock(spec=SsoRegistry)

    SessionService(registry).logout("")

    registry.unregister.assert_not_called()
