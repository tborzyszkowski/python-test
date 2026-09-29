from __future__ import annotations

import pytest
from flight_domain import (
    DuplicatePassengerError,
    EconomyFlight,
    Passenger,
    PassengerNotAllowedError,
    PremiumFlight,
)


def test_economy_adds_and_removes_standard_passenger():
    flight = EconomyFlight("EC1", mileage=1000)
    flight.add_passenger(Passenger("Alice"))
    flight.remove_passenger("Alice")
    assert flight.has_passenger("Alice") is False


def test_economy_protects_vip():
    flight = EconomyFlight("EC1", mileage=1000)
    flight.add_passenger(Passenger("Victor", vip=True))
    with pytest.raises(PassengerNotAllowedError):
        flight.remove_passenger("Victor")


def test_premium_accepts_only_vip():
    flight = PremiumFlight("PR1", mileage=1000)
    with pytest.raises(PassengerNotAllowedError):
        flight.add_passenger(Passenger("Alice"))
    flight.add_passenger(Passenger("Victor", vip=True))
    assert flight.has_passenger("Victor")


def test_duplicate_passenger_is_rejected():
    flight = EconomyFlight("EC1", mileage=1000)
    flight.add_passenger(Passenger("Alice"))
    with pytest.raises(DuplicatePassengerError):
        flight.add_passenger(Passenger("Alice"))


def test_bonus_points_depend_on_vip_status():
    flight = EconomyFlight("EC1", mileage=1000)
    assert flight.bonus_points(Passenger("VIP", vip=True)) == 100
    assert flight.bonus_points(Passenger("Standard")) == 50
