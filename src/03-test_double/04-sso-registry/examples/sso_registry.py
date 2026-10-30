"""SSO Registry: SessionService, Spy i Mock w testach."""

from __future__ import annotations

from dataclasses import dataclass


class SsoRegistry:
    """Interfejs rejestru SSO: zarządzanie tokenami."""
    def unregister(self, token: str) -> bool:
        raise NotImplementedError


class RecordingRegistry:
    """Spy: rejestruje wszystkie interakcje dla testów."""
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    def unregister(self, token: str) -> bool:
        self.calls.append(("unregister", token))
        return self.result


@dataclass
class SessionService:
    """Usługa sesji: zarządza wylogowaniem użytkownika."""
    registry: SsoRegistry

    def logout(self, token: str) -> bool:
        """Wyloguj użytkownika. Zwraca False dla pustych tokenów bez kontaktu z SSO."""
        if not token.strip():
            return False
        return self.registry.unregister(token)


def main() -> None:
    """Demonstruje Spy i Mock w testach wylogowania."""
    registry = RecordingRegistry()
    service = SessionService(registry)
    print("logout:", service.logout("token-123"))
    print("calls:", registry.calls)
    print("empty:", service.logout(""), registry.calls)


if __name__ == "__main__":
    main()
