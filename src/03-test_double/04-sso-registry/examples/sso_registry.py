"""SSO Registry: SessionService, Spy i Mock w testach."""

from __future__ import annotations

from dataclasses import dataclass


class SsoRegistry:
    def unregister(self, token: str) -> bool:
        raise NotImplementedError


class RecordingRegistry:
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    def unregister(self, token: str) -> bool:
        self.calls.append(("unregister", token))
        return self.result


@dataclass
class SessionService:
    registry: SsoRegistry

    def logout(self, token: str) -> bool:
        if not token.strip():
            return False
        return self.registry.unregister(token)


def main() -> None:
    registry = RecordingRegistry()
    service = SessionService(registry)
    print("logout:", service.logout("token-123"))
    print("calls:", registry.calls)
    print("empty:", service.logout(""), registry.calls)


if __name__ == "__main__":
    main()
