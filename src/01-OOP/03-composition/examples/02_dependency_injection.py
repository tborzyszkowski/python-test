"""Przykład 02 - kompozycja jako narzędzie wstrzykiwania zależności (DI).

Uruchomienie::

    python src/01-OOP/03-composition/examples/02_dependency_injection.py

Problem, który rozwiązujemy
---------------------------
``OrderService`` musi pobrać płatność. Jeżeli sam utworzy sobie bramkę
płatności (``StripeGateway()`` w ``__init__``), to każdy test tego serwisu
będzie próbował połączyć się z Internetem. To test **integocyjny**, wolny
i niedeterministyczny.

Rozwiązanie: ``OrderService`` przyjmuje *bramkę* przez konstruktor. Wtedy:

* w produkcji wstrzykujemy ``StripeGateway``,
* w testach wstrzykujemy ``FakeGateway`` (ręczna atrapa) albo ``Mock``.

Bramka opisana jest przez ``Protocol`` (typing strukturalny) - nie trzeba
dziedziczyć, wystarczy mieć zgodne metody. To w Pythonie naturalny sposób
definiowania "interfejsu" bez wspólnej klasy bazowej.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


# --------------------------------------------------------------------------- #
# "Interfejs": co musi umieć bramka płatności                                 #
# --------------------------------------------------------------------------- #
@runtime_checkable
class PaymentGateway(Protocol):
    """Kontrakt bramki płatności (protokół strukturalny)."""

    def charge(self, amount_cents: int, description: str) -> str:
        """Pobiera płatność i zwraca identyfikator transakcji."""
        ...


class PaymentError(RuntimeError):
    """Sygnatura problemu z płatnością (np. odrzucona karta)."""


@dataclass
class OrderLine:
    """Pozycja zamówienia."""

    name: str
    unit_price_cents: int
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.unit_price_cents < 0:
            raise ValueError("unit_price_cents must be non-negative")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    @property
    def total_cents(self) -> int:
        return self.unit_price_cents * self.quantity


# --------------------------------------------------------------------------- #
# Implementacja "produkcyjna" (tu: atrapa, bo nie chcemy prawdziwej bramki)   #
# --------------------------------------------------------------------------- #
class StripeGateway:
    """Wersja produkcyjna - w materiałach tylko udaje wywołanie sieciowe."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def charge(self, amount_cents: int, description: str) -> str:
        # w prawdziwym kodzie: żądanie HTTP do API operatora
        payload = f"{self.api_key}:{amount_cents}:{description}".encode()
        return f"stripe-{hashlib.sha256(payload).hexdigest()[:12]}"


class FakeGateway:
    """Ręczna atrapa (test double) - deterministyczna i natychmiastowa."""

    def __init__(self, *, fail_with: str | None = None) -> None:
        self.fail_with = fail_with
        self.calls: list[tuple[int, str]] = []

    def charge(self, amount_cents: int, description: str) -> str:
        self.calls.append((amount_cents, description))
        if self.fail_with is not None:
            raise PaymentError(self.fail_with)
        return f"fake-{len(self.calls):04d}"


# --------------------------------------------------------------------------- #
# Serwis, który *komponuje* bramkę (zamiast ją tworzyć)                       #
# --------------------------------------------------------------------------- #
@dataclass
class OrderService:
    """Składa zamówienie i pobiera płatność przez wstrzykniętą bramkę."""

    gateway: PaymentGateway
    lines: list[OrderLine] = field(default_factory=list)

    def add_line(self, line: OrderLine) -> None:
        self.lines.append(line)

    @property
    def total_cents(self) -> int:
        return sum(line.total_cents for line in self.lines)

    def checkout(self) -> str:
        if not self.lines:
            raise ValueError("cannot checkout an empty order")
        # Serwis nie wie, JAK płatność jest realizowana - zna tylko kontrakt.
        transaction_id = self.gateway.charge(self.total_cents, "order")
        self.lines.clear()
        return transaction_id


def demo_production_wiring() -> None:
    print("== 1. Ustawienie 'produkcyjne' ==")
    service = OrderService(gateway=StripeGateway("klucz-testowy"))
    service.add_line(OrderLine("książka", 4999, quantity=2))
    print(f"total_cents          -> {service.total_cents}")
    print(f"checkout()           -> {service.checkout()}")
    print()


def demo_test_wiring() -> None:
    print("== 2. Ustawienie 'testowe': ta sama logika, inna zależność ==")
    fake = FakeGateway()
    service = OrderService(gateway=fake)
    service.add_line(OrderLine("długopis", 999))
    transaction = service.checkout()

    print(f"checkout()           -> {transaction}")
    print(f"fake.calls           -> {fake.calls}")
    print("Asercje, które napisałbym w teście:")
    print("  assert transaction == 'fake-0001'")
    print("  assert fake.calls == [(999, 'order')]")
    print("  assert service.lines == []            # koszyk wyczyszczony po płatności")
    print()


def demo_error_path() -> None:
    print("== 3. Ścieżka błędu też jest testowalna bez Internetu ==")
    fake = FakeGateway(fail_with="karta odrzucona")
    service = OrderService(gateway=fake)
    service.add_line(OrderLine("bilet", 2500))
    try:
        service.checkout()
    except PaymentError as exc:
        print(f"checkout()           -> PaymentError: {exc}")
    print(f"lines po błędzie     -> {service.lines}   # zamówienie nie zostało wyczyszczone")
    print()


def demo_protocol_check() -> None:
    print("== 4. Protokół sprawdza 'kształt' obiektu, nie pochodzenie ==")
    print(f"isinstance(FakeGateway(), PaymentGateway)   -> "
          f"{isinstance(FakeGateway(), PaymentGateway)}")
    print(f"isinstance(StripeGateway('k'), PaymentGateway) -> "
          f"{isinstance(StripeGateway('k'), PaymentGateway)}")
    print("Dzięki temu serwis nie musi znać żadnej wspólnej klasy bazowej.")


def main() -> None:
    demo_production_wiring()
    demo_test_wiring()
    demo_error_path()
    demo_protocol_check()


if __name__ == "__main__":
    main()
