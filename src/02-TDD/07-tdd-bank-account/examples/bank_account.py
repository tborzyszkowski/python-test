"""Konto bankowe rozwijane przez kolejne iteracje TDD."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


class InsufficientFundsError(ValueError):
    """Wyplata lub przelew przekracza dostepne saldo."""


@dataclass(frozen=True)
class Transaction:
    kind: str
    amount_cents: int
    balance_after_cents: int
    created_at: datetime


class BankAccount:
    def __init__(self) -> None:
        self._balance_cents = 0
        self._history: list[Transaction] = []

    @property
    def balance_cents(self) -> int:
        return self._balance_cents

    @property
    def history(self) -> list[Transaction]:
        return list(self._history)

    def _record(self, kind: str, amount_cents: int) -> None:
        self._history.append(
            Transaction(kind, amount_cents, self._balance_cents, datetime.now())
        )

    def deposit(self, amount_cents: int) -> None:
        if amount_cents <= 0:
            raise ValueError("deposit must be positive")
        self._balance_cents += amount_cents
        self._record("deposit", amount_cents)

    def withdraw(self, amount_cents: int) -> None:
        if amount_cents <= 0:
            raise ValueError("withdrawal must be positive")
        if amount_cents > self._balance_cents:
            raise InsufficientFundsError(
                f"need {amount_cents}, have {self._balance_cents}"
            )
        self._balance_cents -= amount_cents
        self._record("withdrawal", -amount_cents)

    def transfer(self, amount_cents: int, fee_cents: int = 0) -> None:
        if amount_cents <= 0:
            raise ValueError("transfer must be positive")
        if fee_cents < 0:
            raise ValueError("fee must be non-negative")
        total = amount_cents + fee_cents
        if total > self._balance_cents:
            raise InsufficientFundsError(f"need {total}, have {self._balance_cents}")
        self._balance_cents -= amount_cents
        self._record("transfer", -amount_cents)
        if fee_cents:
            self._balance_cents -= fee_cents
            self._record("fee", -fee_cents)


def main() -> None:
    account = BankAccount()
    account.deposit(10_000)
    account.transfer(3_000, fee_cents=100)
    print("balance:", account.balance_cents)
    for transaction in account.history:
        print(transaction.kind, transaction.amount_cents, transaction.balance_after_cents)


if __name__ == "__main__":
    main()
