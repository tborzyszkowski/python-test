"""Przykłady pięciu test doubles i monkeypatchingu dla SubscriptionService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
import subscription_service
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

PLAN = SubscriptionPlan("Premium", Decimal("100.00"))


class TestDummy:
    """Dummy wypełnia wymagany argument, ale nie jest przedmiotem testu."""

    def test_quote_does_not_need_a_real_audit_logger(self, monkeypatch):
        monkeypatch.setenv("SUBSCRIPTION_DISCOUNT", "0.10")
        service = SubscriptionService(
            Mock(spec=DatabaseRepository),
            Mock(),
            Mock(),
            DummyAuditLogger(),
        )

        assert service.quote(PLAN) == Decimal("110.70")

    def test_dummy_can_be_reused_for_another_price_case(self):
        service = SubscriptionService(Mock(), Mock(), Mock(), DummyAuditLogger())

        assert service.quote(SubscriptionPlan("Basic", Decimal("50.00"))) == Decimal("61.50")


class TestStub:
    """Stub kontroluje odpowiedź zewnętrznego API bez sieci."""

    def test_successful_payment_returns_subscription(self):
        repository = InMemorySubscriptionRepository()
        gateway = PaymentGatewayStub(PaymentResult("success", "tx-101"))
        service = SubscriptionService(repository, gateway, Mock(), DummyAuditLogger())

        subscription = service.activate("user-1", PLAN, "card-token")

        assert subscription.transaction_id == "tx-101"
        assert repository.get_for_user("user-1") == subscription

    def test_declined_payment_becomes_domain_error(self):
        gateway = PaymentGatewayStub(PaymentResult("declined"))
        service = SubscriptionService(Mock(), gateway, Mock(), DummyAuditLogger())

        with pytest.raises(RuntimeError, match="declined"):
            service.activate("user-1", PLAN, "bad-card")


class TestFake:
    """Fake zachowuje stan i pozwala testować repozytorium bez SQL."""

    def test_saved_subscription_can_be_read_back(self):
        repository = InMemorySubscriptionRepository()
        subscription = Subscription(
            "user-1",
            "Premium",
            "tx-1",
            datetime(2026, 1, 1),
            datetime(2027, 1, 1),
        )

        repository.save(subscription)

        assert repository.get_for_user("user-1") == subscription

    def test_fake_supports_multiple_users_without_shared_state(self):
        repository = InMemorySubscriptionRepository()
        first = Subscription("user-1", "Basic", "tx-1", datetime(2026, 1, 1), datetime(2027, 1, 1))
        second = Subscription("user-2", "Premium", "tx-2", datetime(2026, 1, 1), datetime(2027, 1, 1))
        repository.save(first)
        repository.save(second)

        assert repository.get_for_user("user-1") == first
        assert repository.get_for_user("user-2") == second


class TestSpy:
    """Spy pozwala sprawdzać wynik i zapisane dane interakcji."""

    def test_activation_records_confirmation_email(self):
        notifications = EmailNotificationSpy()
        service = SubscriptionService(
            InMemorySubscriptionRepository(),
            PaymentGatewayStub(PaymentResult("success", "tx-2")),
            notifications,
            DummyAuditLogger(),
        )

        service.activate("user-1", PLAN, "token")

        assert len(notifications.sent_emails) == 1
        user_id, subject, body = notifications.sent_emails[0]
        assert user_id == "user-1"
        assert "aktywowana" in subject
        assert "Dziękujemy za subskrypcję" in body

    def test_spy_keeps_order_of_two_notifications(self):
        notifications = EmailNotificationSpy()
        notifications.send("user-1", "first", "one")
        notifications.send("user-1", "second", "two")

        assert [email[1] for email in notifications.sent_emails] == ["first", "second"]


class TestMock:
    """Mock precyzyjnie weryfikuje kontrakt interakcji."""

    def test_repository_failure_rolls_back_exact_transaction(self):
        repository = Mock(spec=DatabaseRepository)
        repository.save.side_effect = OSError("database unavailable")
        gateway = Mock()
        gateway.charge.return_value = PaymentResult("success", "tx-404")
        service = SubscriptionService(repository, gateway, Mock(), DummyAuditLogger())

        with pytest.raises(OSError, match="database unavailable"):
            service.activate("user-1", PLAN, "token")

        gateway.rollback_transaction.assert_called_once_with("tx-404")

    def test_success_sends_one_confirmation_with_expected_arguments(self):
        repository = Mock(spec=DatabaseRepository)
        gateway = Mock()
        gateway.charge.return_value = PaymentResult("success", "tx-505")
        notifications = Mock()
        service = SubscriptionService(repository, gateway, notifications, DummyAuditLogger())

        service.activate("user-1", PLAN, "token")

        notifications.send.assert_called_once_with(
            "user-1",
            "Subskrypcja aktywowana",
            "Dziękujemy za subskrypcję planu Premium.",
        )


class FrozenDateTime(datetime):
    """Stały zegar używany tylko przez test monkeypatchingu."""

    @classmethod
    def now(cls, tz=None):
        return cls(2026, 11, 12, 12, 0, 0)


class TestMonkeypatch:
    """monkeypatch podmienia czas i konfigurację bez edycji kodu produkcyjnego."""

    def test_expired_subscription_is_inactive_at_controlled_time(self, monkeypatch):
        monkeypatch.setattr(subscription_service, "datetime", FrozenDateTime)
        repository = InMemorySubscriptionRepository()
        repository.save(
            Subscription(
                "user-1",
                "Premium",
                "tx-old",
                FrozenDateTime(2025, 1, 1),
                FrozenDateTime(2026, 1, 1),
            )
        )
        service = SubscriptionService(repository, Mock(), Mock(), DummyAuditLogger())

        assert service.is_subscription_active("user-1") is False

    def test_environment_changes_quote_without_changing_source(self, monkeypatch):
        monkeypatch.setenv("SUBSCRIPTION_DISCOUNT", "0.20")
        monkeypatch.setenv("SUBSCRIPTION_TAX", "0.08")
        service = SubscriptionService(Mock(), Mock(), Mock(), DummyAuditLogger())

        assert service.quote(PLAN) == Decimal("86.40")
