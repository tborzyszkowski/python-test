from unittest.mock import Mock

from sso_registry import RecordingRegistry, SessionService, SsoRegistry


def spy_logout(token: str) -> list[tuple[str, str]]:
    registry = RecordingRegistry()
    SessionService(registry).logout(token)
    return registry.calls


def mock_logout(token: str) -> Mock:
    registry = Mock(spec=SsoRegistry)
    registry.unregister.return_value = True
    SessionService(registry).logout(token)
    return registry
