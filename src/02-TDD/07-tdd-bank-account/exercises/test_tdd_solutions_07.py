import pytest
from tdd_solutions_07 import InsufficientFundsError, funded_account, transfer_total


def test_solution_transfer_with_fee():
    assert transfer_total(funded_account(), 3000, 100) == 6900


def test_solution_preserves_balance_on_error():
    account = funded_account(100)
    with pytest.raises(InsufficientFundsError):
        transfer_total(account, 100, 1)
    assert account.balance_cents == 100
