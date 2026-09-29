from __future__ import annotations

import pytest
from bank_account import BankAccount, InsufficientFundsError


def test_new_account_has_zero_balance_and_empty_history():
    account = BankAccount()

    assert account.balance_cents == 0
    assert account.history == []


def test_deposit_increases_balance_and_records_transaction():
    account = BankAccount()
    account.deposit(1000)

    assert account.balance_cents == 1000
    assert [(item.kind, item.amount_cents) for item in account.history] == [("deposit", 1000)]


def test_withdrawal_decreases_balance():
    account = BankAccount()
    account.deposit(1000)
    account.withdraw(300)

    assert account.balance_cents == 700
    assert account.history[-1].kind == "withdrawal"
    assert account.history[-1].amount_cents == -300


def test_insufficient_withdrawal_keeps_balance_and_history():
    account = BankAccount()
    account.deposit(1000)
    before = account.history

    with pytest.raises(InsufficientFundsError, match="need"):
        account.withdraw(1001)

    assert account.balance_cents == 1000
    assert account.history == before


def test_transfer_records_transfer_and_fee():
    account = BankAccount()
    account.deposit(10_000)
    account.transfer(3_000, fee_cents=100)

    assert account.balance_cents == 6_900
    assert [(item.kind, item.amount_cents) for item in account.history[-2:]] == [
        ("transfer", -3000),
        ("fee", -100),
    ]


def test_transfer_rejects_total_above_balance_without_partial_history():
    account = BankAccount()
    account.deposit(1000)
    before = account.history

    with pytest.raises(InsufficientFundsError):
        account.transfer(900, fee_cents=101)

    assert account.balance_cents == 1000
    assert account.history == before


@pytest.mark.parametrize("amount", [0, -1])
def test_deposit_rejects_non_positive_amount(amount):
    with pytest.raises(ValueError, match="positive"):
        BankAccount().deposit(amount)


def test_history_is_returned_as_copy():
    account = BankAccount()
    account.deposit(100)
    history = account.history
    history.clear()

    assert len(account.history) == 1
