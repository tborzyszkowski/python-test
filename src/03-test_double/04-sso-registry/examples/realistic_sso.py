"""Realistyczny scenariusz: SSO Registry z sesją użytkownika."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class TokenStatus(Enum):
    """Status tokenu w rejestrze."""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class SsoRegistry:
    """Interfejs rejestru SSO."""
    def register(self, token: str, user_id: str) -> bool:
        """Rejestruje nowy token dla użytkownika."""
        raise NotImplementedError

    def unregister(self, token: str) -> bool:
        """Wyrejestruje token."""
        raise NotImplementedError

    def validate(self, token: str) -> bool:
        """Weryfikuje czy token jest aktywny."""
        raise NotImplementedError

    def get_user_by_token(self, token: str) -> Optional[str]:
        """Zwraca user_id dla tokenu."""
        raise NotImplementedError


class RecordingRegistry:
    """Spy: rejestruje wszystkie interakcje dla testów."""
    def __init__(self, valid_tokens: Optional[set[str]] = None) -> None:
        self.valid_tokens = valid_tokens or set()
        self.calls: list[tuple[str, ...]] = []
        self.user_map: dict[str, str] = {}

    def register(self, token: str, user_id: str) -> bool:
        """Zapisz token i mapuj do użytkownika."""
        self.calls.append(("register", token, user_id))
        self.valid_tokens.add(token)
        self.user_map[token] = user_id
        return True

    def unregister(self, token: str) -> bool:
        """Wyrejestruj token."""
        self.calls.append(("unregister", token))
        if token in self.valid_tokens:
            self.valid_tokens.discard(token)
            return True
        return False

    def validate(self, token: str) -> bool:
        """Sprawdź czy token istnieje."""
        self.calls.append(("validate", token))
        return token in self.valid_tokens

    def get_user_by_token(self, token: str) -> Optional[str]:
        """Zwróć user_id dla tokenu."""
        self.calls.append(("get_user_by_token", token))
        return self.user_map.get(token)


@dataclass
class UserSession:
    """Sesja użytkownika z czasem życia."""
    token: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    last_activity: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        """Sprawdzić czy sesja wygasła."""
        return datetime.now() > self.expires_at

    def refresh_activity(self) -> None:
        """Zaktualizuj czas ostatniej aktywności."""
        self.last_activity = datetime.now()


@dataclass
class SessionService:
    """Usługa sesji: zarządzanie logowaniem, wylogowaniem, walidacją."""
    registry: SsoRegistry
    sessions: dict[str, UserSession] = field(default_factory=dict)

    def login(self, token: str, user_id: str) -> bool:
        """Zaloguj użytkownika, rejestrując token w SSO."""
        if not token.strip() or not user_id.strip():
            return False

        # Zarejestruj w SSO
        if not self.registry.register(token, user_id):
            return False

        # Utwórz lokalną sesję
        self.sessions[token] = UserSession(token, user_id)
        return True

    def logout(self, token: str) -> bool:
        """Wyloguj użytkownika, wyrejestrując token."""
        if not token.strip():
            return False

        # Wyrejestruj z SSO
        result = self.registry.unregister(token)

        # Usuń lokalną sesję
        self.sessions.pop(token, None)
        return result

    def validate_session(self, token: str) -> bool:
        """Sprawdzić czy sesja jest aktywna i nieprzeterminowana."""
        if not token.strip():
            return False

        # Sprawdzić w SSO
        if not self.registry.validate(token):
            return False

        # Sprawdzić lokalnie
        session = self.sessions.get(token)
        if not session or session.is_expired():
            return False

        session.refresh_activity()
        return True

    def get_current_user(self, token: str) -> Optional[str]:
        """Zwrócić aktualne user_id dla tokenu."""
        if not self.validate_session(token):
            return None

        return self.registry.get_user_by_token(token)

    def logout_all_user_sessions(self, user_id: str) -> int:
        """Wylogować wszystkie sesje danego użytkownika."""
        count = 0
        # Znajdź wszystkie tokeny dla tego użytkownika
        tokens_to_revoke = [
            token for token, session in self.sessions.items()
            if session.user_id == user_id
        ]

        for token in tokens_to_revoke:
            if self.logout(token):
                count += 1

        return count


def main() -> None:
    """Praktyczne przykłady."""
    registry = RecordingRegistry()
    service = SessionService(registry)

    # Zalogowanie
    print("Login:", service.login("token-123", "user-alice"))

    # Walidacja
    print("Validate:", service.validate_session("token-123"))

    # Wylogowanie
    print("Logout:", service.logout("token-123"))

    # Walidacja po wylogowaniu
    print("Validate after logout:", service.validate_session("token-123"))

    # Wszystkie operacje
    print("\nAll operations:")
    for call in registry.calls:
        print(f"  {call}")


if __name__ == "__main__":
    main()
