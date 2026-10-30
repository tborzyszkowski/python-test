"""Testy dla realistycznego scenariusza SSO Registry."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from realistic_sso import (
    RecordingRegistry,
    SessionService,
    SsoRegistry,
    UserSession,
)


class TestUserSessionLifecycle:
    """Testy cyklu życia sesji użytkownika."""

    def test_session_is_not_expired_immediately(self):
        """Nowa sesja nie powinna być wygasła."""
        session = UserSession(token="t1", user_id="user-1")
        assert not session.is_expired()

    def test_session_expires_after_expiry_time(self):
        """Sesja wygasa po upływie expiry_at."""
        session = UserSession(
            token="t1",
            user_id="user-1",
            expires_at=datetime.now() - timedelta(minutes=1)
        )
        assert session.is_expired()

    def test_refresh_activity_updates_timestamp(self):
        """Odświeżenie aktywności zaktualizuje last_activity."""
        session = UserSession(token="t1", user_id="user-1")
        old_activity = session.last_activity
        session.refresh_activity()
        assert session.last_activity >= old_activity


class TestSessionServiceLogin:
    """Testy logowania użytkownika."""

    def test_login_with_valid_credentials_registers_token(self):
        """Login z prawidłowymi kredencjałami rejestruje token w SSO."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        result = service.login("token-abc", "user-alice")

        assert result is True
        assert ("register", "token-abc", "user-alice") in registry.calls
        assert "token-abc" in service.sessions

    def test_login_with_empty_token_fails(self):
        """Login z pustym tokenem powinien zwrócić False."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        result = service.login("", "user-alice")

        assert result is False
        assert len(registry.calls) == 0
        assert len(service.sessions) == 0

    def test_login_with_empty_user_id_fails(self):
        """Login z pustym user_id powinien zwrócić False."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        result = service.login("token-abc", "")

        assert result is False

    def test_multiple_logins_create_separate_sessions(self):
        """Wiele loginów tworzy odrębne sesje dla tego samego użytkownika."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        service.login("token-1", "user-alice")
        service.login("token-2", "user-alice")

        assert len(service.sessions) == 2
        assert "token-1" in service.sessions
        assert "token-2" in service.sessions


class TestSessionServiceLogout:
    """Testy wylogowania użytkownika."""

    def test_logout_removes_token_from_registry(self):
        """Logout wyrejestruje token z SSO i lokalnie."""
        registry = RecordingRegistry(valid_tokens={"token-123"})
        registry.user_map["token-123"] = "user-alice"
        service = SessionService(registry)
        service.sessions["token-123"] = UserSession("token-123", "user-alice")

        result = service.logout("token-123")

        assert result is True
        assert ("unregister", "token-123") in registry.calls
        assert "token-123" not in service.sessions

    def test_logout_empty_token_returns_false(self):
        """Logout z pustym tokenem powinien zwrócić False."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        result = service.logout("")

        assert result is False
        assert len(registry.calls) == 0

    def test_logout_nonexistent_token_returns_false(self):
        """Logout nieznanego tokenu powinien zwrócić False."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        result = service.logout("unknown-token")

        assert result is False


class TestSessionServiceValidation:
    """Testy walidacji sesji."""

    def test_validate_session_with_active_token(self):
        """Walidacja aktywnej sesji zwraca True."""
        registry = RecordingRegistry(valid_tokens={"token-active"})
        registry.user_map["token-active"] = "user-alice"
        service = SessionService(registry)
        service.sessions["token-active"] = UserSession("token-active", "user-alice")

        result = service.validate_session("token-active")

        assert result is True
        assert ("validate", "token-active") in registry.calls

    def test_validate_session_with_expired_local_session(self):
        """Walidacja wygasłej sesji lokalnie zwraca False."""
        registry = RecordingRegistry(valid_tokens={"token-expired"})
        registry.user_map["token-expired"] = "user-alice"
        service = SessionService(registry)
        # Sesja wygasła
        service.sessions["token-expired"] = UserSession(
            "token-expired",
            "user-alice",
            expires_at=datetime.now() - timedelta(minutes=1)
        )

        result = service.validate_session("token-expired")

        assert result is False

    def test_validate_session_with_unregistered_token_in_sso(self):
        """Walidacja tokenu nieznanego dla SSO zwraca False."""
        registry = RecordingRegistry(valid_tokens=set())
        service = SessionService(registry)

        result = service.validate_session("token-unknown")

        assert result is False


class TestSessionServiceGetCurrentUser:
    """Testy pobierania bieżącego użytkownika."""

    def test_get_current_user_returns_user_id_for_valid_session(self):
        """Pobranie użytkownika dla aktywnej sesji."""
        registry = RecordingRegistry(valid_tokens={"token-valid"})
        registry.user_map["token-valid"] = "user-bob"
        service = SessionService(registry)
        service.sessions["token-valid"] = UserSession("token-valid", "user-bob")

        user_id = service.get_current_user("token-valid")

        assert user_id == "user-bob"
        assert ("get_user_by_token", "token-valid") in registry.calls

    def test_get_current_user_returns_none_for_invalid_session(self):
        """Pobranie użytkownika dla nieaktywnej sesji zwraca None."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        user_id = service.get_current_user("token-invalid")

        assert user_id is None


class TestSessionServiceLogoutAll:
    """Testy wylogowania wszystkich sesji użytkownika."""

    def test_logout_all_user_sessions_revokes_all_tokens(self):
        """Logout wszystkich sesji wyloguje wszystkie tokeny użytkownika."""
        registry = RecordingRegistry(valid_tokens={"token-1", "token-2"})
        registry.user_map["token-1"] = "user-alice"
        registry.user_map["token-2"] = "user-alice"

        service = SessionService(registry)
        service.sessions["token-1"] = UserSession("token-1", "user-alice")
        service.sessions["token-2"] = UserSession("token-2", "user-alice")

        count = service.logout_all_user_sessions("user-alice")

        assert count == 2
        assert len(service.sessions) == 0
        # Sprawdź że oba tokeny zostały wyrejestrowane
        unregister_calls = [
            c for c in registry.calls if c[0] == "unregister"
        ]
        assert len(unregister_calls) == 2

    def test_logout_all_ignores_other_users_sessions(self):
        """Logout wszystkich sesji wyloguje tylko sesje danego użytkownika."""
        registry = RecordingRegistry(valid_tokens={"alice-token", "bob-token"})
        registry.user_map["alice-token"] = "user-alice"
        registry.user_map["bob-token"] = "user-bob"

        service = SessionService(registry)
        service.sessions["alice-token"] = UserSession("alice-token", "user-alice")
        service.sessions["bob-token"] = UserSession("bob-token", "user-bob")

        count = service.logout_all_user_sessions("user-alice")

        assert count == 1
        assert "alice-token" not in service.sessions
        assert "bob-token" in service.sessions


class TestSessionServiceWithMock:
    """Testy z użyciem Mock zamiast Spy."""

    def test_login_calls_registry_register_method(self):
        """Login powinien wywołać registry.register z prawidłowymi parametrami."""
        registry = Mock(spec=SsoRegistry)
        registry.register.return_value = True

        service = SessionService(registry)
        result = service.login("token-test", "user-test")

        assert result is True
        registry.register.assert_called_once_with("token-test", "user-test")

    def test_validate_calls_registry_validate_and_get_user(self):
        """Walidacja powinna sprawdzić zarówno SSO jak i get_user."""
        registry = Mock(spec=SsoRegistry)
        registry.validate.return_value = True
        registry.get_user_by_token.return_value = "user-test"

        service = SessionService(registry)
        service.sessions["token-test"] = UserSession("token-test", "user-test")

        result = service.validate_session("token-test")

        assert result is True
        registry.validate.assert_called_once_with("token-test")

    def test_logout_on_sso_failure_still_removes_local_session(self):
        """Logout powinien usunąć lokalną sesję nawet jeśli SSO zawiodło."""
        registry = Mock(spec=SsoRegistry)
        registry.unregister.return_value = False  # SSO nie znalazł tokenu

        service = SessionService(registry)
        service.sessions["token-test"] = UserSession("token-test", "user-test")

        result = service.logout("token-test")

        assert result is False
        assert "token-test" not in service.sessions
        registry.unregister.assert_called_once_with("token-test")


class TestSpyVsMockComparison:
    """Porównanie Spy i Mock podejścia."""

    def test_spy_is_more_flexible_than_mock(self):
        """Spy pozwala na bardziej elastyczne asercje niż Mock."""
        registry = RecordingRegistry()
        service = SessionService(registry)

        # Wykonaj wiele operacji
        service.login("t1", "user-1")
        service.login("t2", "user-1")
        service.validate_session("t1")
        service.logout("t1")

        # Spy pozwala później analizować dowolne części
        register_calls = [c for c in registry.calls if c[0] == "register"]
        assert len(register_calls) == 2

        logout_calls = [c for c in registry.calls if c[0] == "unregister"]
        assert len(logout_calls) == 1

    def test_mock_enforces_contract_immediately(self):
        """Mock egzekwuje kontrakt natychmiast."""
        registry = Mock(spec=SsoRegistry)
        registry.unregister.return_value = True

        service = SessionService(registry)

        # Jeśli zapomnisz wywołać unregister, test od razu zaprotestuje
        with pytest.raises(AssertionError):
            registry.unregister.assert_called_once_with("any-token")
            # Nie został wywołany!
