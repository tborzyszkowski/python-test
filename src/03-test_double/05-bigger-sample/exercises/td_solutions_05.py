"""Przykładowe rozwiązania ćwiczeń z tematu SubscriptionService."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

from subscription_service import (
    DatabaseRepository,
    DummyAuditLogger,
    EmailNotificationSpy,
    InMemorySubscriptionRepository,
    PaymentGatewayStub,
    PaymentResult,
    Subscription,
    SubscriptionPlan,
    SubscriptionService,
)


class TimeoutPaymentGatewayStub(PaymentGatewayStub):
    """Stub pokazujący awarię sieci, a nie odrzucenie karty."""

    def charge(self, user_id, amount, payment_token):
        raise TimeoutError("payment provider timed out")


def activate_with_translated_timeout(
    service: SubscriptionService,
    user_id: str,
    plan: SubscriptionPlan,
    payment_token: str,
) -> Subscription:
    """Tłumaczy techniczny timeout na błąd zrozumiały dla warstwy domenowej."""
    try:
        return service.activate(user_id, plan, payment_token)
    except TimeoutError as error:
        raise RuntimeError("payment provider unavailable") from error


class DeletableInMemoryRepository(InMemorySubscriptionRepository):
    """Rozszerzony Fake z operacją usuwania danych użytkownika."""

    def delete_for_user(self, user_id: str) -> bool:
        if self.get_for_user(user_id) is None:
            return False
        del self._subscriptions[user_id]
        return True


def delete_subscription_example() -> bool:
    """Ćwiczenie 2: zapisuje, usuwa i zwraca wynik operacji usuwania."""
    repository = DeletableInMemoryRepository()
    repository.save(
        Subscription(
            "user-1",
            "Premium",
            "tx-delete",
            datetime(2026, 1, 1),
            datetime(2027, 1, 1),
        )
    )

    deleted = repository.delete_for_user("user-1")
    assert repository.get_for_user("user-1") is None
    return deleted


class AuditLoggerSpy:
    """Spy audytu przechowujący zdarzenia zamiast wysyłać je do logów."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, str]]] = []

    def log(self, event: str, **details: str) -> None:
        self.events.append((event, details))


def declined_payment_has_no_audit_event(plan: SubscriptionPlan) -> bool:
    """Ćwiczenie 3: odrzucona płatność nie tworzy zdarzenia audytowego."""
    audit = AuditLoggerSpy()
    service = SubscriptionService(
        InMemorySubscriptionRepository(),
        PaymentGatewayStub(PaymentResult("declined")),
        EmailNotificationSpy(),
        audit,
    )

    try:
        service.activate("user-1", plan, "token")
    except RuntimeError:
        pass

    return audit.events == []


def activate_with_notification_spy(
    plan: SubscriptionPlan,
) -> list[tuple[str, str, str]]:
    """Ćwiczenie 4: Spy zastępuje Mock dla powiadomień."""
    notifications = EmailNotificationSpy()
    service = SubscriptionService(
        InMemorySubscriptionRepository(),
        PaymentGatewayStub(PaymentResult("success", "tx-spy")),
        notifications,
        DummyAuditLogger(),
    )

    service.activate("user-1", plan, "token")
    return notifications.sent_emails


def calendar_expiry(started_at: datetime) -> datetime:
    """Zwraca rocznicę daty, obsługując 29 lutego jako 28 lutego."""
    try:
        return started_at.replace(year=started_at.year + 1)
    except ValueError:
        return started_at.replace(year=started_at.year + 1, day=28)


def is_active_at(subscription: Subscription, now: datetime) -> bool:
    """Sprawdza regułę półotwartego przedziału [start, expiry)."""
    return subscription.started_at <= now < subscription.expires_at


def calendar_expiry_examples() -> tuple[datetime, datetime]:
    """Ćwiczenie 5: przykłady zwykłej rocznicy i daty przestępnej."""
    regular = calendar_expiry(datetime(2026, 11, 12))
    leap_day = calendar_expiry(datetime(2028, 2, 29))
    assert regular == datetime(2027, 11, 12)
    assert leap_day == datetime(2029, 2, 28)
    return regular, leap_day


def mock_spec_example() -> DatabaseRepository:
    """Dodatkowy przykład: Fake pozostaje, a Mock pilnuje kontraktu."""
    repository = Mock(spec=DatabaseRepository)
    repository.get_for_user.return_value = None
    return repository
