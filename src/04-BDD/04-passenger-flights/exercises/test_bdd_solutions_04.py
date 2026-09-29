import pytest
from bdd_solutions_04 import economy_with_passenger, premium_for_vip
from flight_domain import PassengerNotAllowedError


def test_solution_economy_passenger():
    assert economy_with_passenger("Alice").has_passenger("Alice")


def test_solution_premium_vip():
    assert premium_for_vip("Victor").has_passenger("Victor")


def test_solution_economy_vip_cannot_be_removed():
    flight = economy_with_passenger("Victor", vip=True)
    with pytest.raises(PassengerNotAllowedError):
        flight.remove_passenger("Victor")
