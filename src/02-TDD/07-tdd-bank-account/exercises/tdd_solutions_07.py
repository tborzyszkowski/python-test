from bank_account import BankAccount, InsufficientFundsError, Transaction


def funded_account(amount: int = 10_000) -> BankAccount:
    account = BankAccount()
    account.deposit(amount)
    return account


def transfer_total(account: BankAccount, amount: int, fee: int = 0) -> int:
    account.transfer(amount, fee)
    return account.balance_cents


__all__ = ["BankAccount", "InsufficientFundsError", "Transaction", "funded_account", "transfer_total"]
