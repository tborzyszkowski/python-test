"""Spójny scenariusz do nauki test doubles: aktywacja subskrypcji."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class SubscriptionPlan:
    """Plan rocznej subskrypcji."""

    name: str
    annual_price: Decimal


@dataclass(frozen=True)
class PaymentResult:
    """Uproszczona odpowiedź bramki płatniczej."""

    status: str
    transaction_id: str | None = None


@dataclass
class Subscription:
    """Aktywna subskrypcja zapisana w repozytorium."""

    user_id: str
    plan_name: str
    transaction_id: str
    started_at: datetime
    expires_at: datetime

    def is_active(self, now: datetime) -> bool:
        return self.started_at <= now < self.expires_at


class DatabaseRepository(Protocol):
    def save(self, subscription: Subscription) -> None: ...

    def get_for_user(self, user_id: str) -> Subscription | None: ...


class PaymentGateway(Protocol):
    def charge(self, user_id: str, amount: Decimal, payment_token: str) -> PaymentResult: ...

    def rollback_transaction(self, transaction_id: str) -> None: ...


class NotificationService(Protocol):
    def send(self, user_id: str, subject: str, body: str) -> None: ...


class AuditLogger(Protocol):
    def log(self, event: str, **details: str) -> None: ...


class SubscriptionService:
    """Koordynuje płatność, zapis subskrypcji i powiadomienia."""

    def __init__(
        self,
        repository: DatabaseRepository,
        payment_gateway: PaymentGateway,
        notifications: NotificationService,
        audit_logger: AuditLogger,
    ) -> None:
        self.repository = repository
        self.payment_gateway = payment_gateway
        self.notifications = notifications
        self.audit_logger = audit_logger

    def quote(self, plan: SubscriptionPlan) -> Decimal:
        """Wylicza cenę po rabacie konfiguracyjnym i podatku."""
        discount = Decimal(os.environ.get("SUBSCRIPTION_DISCOUNT", "0"))
        tax = Decimal(os.environ.get("SUBSCRIPTION_TAX", "0.23"))
        discounted = plan.annual_price * (Decimal("1") - discount)
        return (discounted * (Decimal("1") + tax)).quantize(Decimal("0.01"))

    def activate(
        self,
        user_id: str,
        plan: SubscriptionPlan,
        payment_token: str,
    ) -> Subscription:
        """Opłaca i zapisuje roczną subskrypcję."""
        if not user_id.strip() or not payment_token.strip():
            raise ValueError("user_id and payment_token are required")

        result = self.payment_gateway.charge(
            user_id,
            self.quote(plan),
            payment_token,
        )
        if result.status != "success" or result.transaction_id is None:
            raise RuntimeError("payment was declined")

        now = datetime.now()
        subscription = Subscription(
            user_id=user_id,
            plan_name=plan.name,
            transaction_id=result.transaction_id,
            started_at=now,
            expires_at=now + timedelta(days=365),
        )
        try:
            self.repository.save(subscription)
        except Exception:
            self.payment_gateway.rollback_transaction(result.transaction_id)
            raise

        self.notifications.send(
            user_id,
            "Subskrypcja aktywowana",
            f"Dziękujemy za subskrypcję planu {plan.name}.",
        )
        self.audit_logger.log(
            "subscription_activated",
            user_id=user_id,
            plan=plan.name,
            transaction_id=result.transaction_id,
        )
        return subscription

    def is_subscription_active(self, user_id: str) -> bool:
        """Sprawdza subskrypcję użytkownika względem aktualnego czasu."""
        subscription = self.repository.get_for_user(user_id)
        return subscription is not None and subscription.is_active(datetime.now())


class InMemorySubscriptionRepository:
    """Fake repozytorium: działająca, uproszczona baza w pamięci."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._subscriptions[subscription.user_id] = subscription

    def get_for_user(self, user_id: str) -> Subscription | None:
        return self._subscriptions.get(user_id)


class PaymentGatewayStub:
    """Stub bramki płatniczej zwracający z góry ustaloną odpowiedź."""

    def __init__(self, result: PaymentResult) -> None:
        self.result = result

    def charge(self, user_id: str, amount: Decimal, payment_token: str) -> PaymentResult:
        return self.result

    def rollback_transaction(self, transaction_id: str) -> None:
        pass


class EmailNotificationSpy:
    """Spy powiadomień: nie wysyła maila, ale zachowuje wszystkie wywołania."""

    def __init__(self) -> None:
        self.sent_emails: list[tuple[str, str, str]] = []

    def send(self, user_id: str, subject: str, body: str) -> None:
        self.sent_emails.append((user_id, subject, body))


class DummyAuditLogger:
    """Dummy wymagany przez konstruktor, nieużywany w testowanym fragmencie."""

    def log(self, event: str, **details: str) -> None:
        pass
