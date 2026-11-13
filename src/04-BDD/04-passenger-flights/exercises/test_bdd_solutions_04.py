import pytest
from bdd_solutions_04 import (
    economy_standard_can_be_removed,
    economy_with_passenger,
    passengers_from_table,
    premium_duplicate_error,
    premium_for_vip,
    student_bonus_points,
)
from flight_domain import PassengerNotAllowedError


def test_solution_economy_passenger():
    assert economy_with_passenger("Alice").has_passenger("Alice")


def test_solution_premium_vip():
    assert premium_for_vip("Victor").has_passenger("Victor")


def test_solution_economy_vip_cannot_be_removed():
    flight = economy_with_passenger("Victor", vip=True)
    with pytest.raises(PassengerNotAllowedError):
        flight.remove_passenger("Victor")


def test_solution_economy_standard_can_be_removed():
    assert economy_standard_can_be_removed("Alice").has_passenger("Alice") is False


def test_solution_premium_duplicate_is_rejected():
    assert premium_duplicate_error("Victor") == "passenger already on flight: Victor"


def test_solution_student_points():
    assert student_bonus_points(1000) == 66


def test_solution_table_creates_domain_passengers():
    passengers = passengers_from_table(
        [
            {"name": "Alice", "status": "STANDARD"},
            {"name": "Sara", "status": "STUDENT"},
        ]
    )

    assert [passenger.status for passenger in passengers] == ["STANDARD", "STUDENT"]
