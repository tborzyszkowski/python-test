from collections.abc import Iterable

from flight_domain import (
    DuplicatePassengerError,
    EconomyFlight,
    Passenger,
    PremiumFlight,
)


def economy_with_passenger(name: str, vip: bool = False) -> EconomyFlight:
    flight = EconomyFlight("EC-SOLUTION", mileage=1000)
    flight.add_passenger(Passenger(name, vip=vip))
    return flight


def premium_for_vip(name: str) -> PremiumFlight:
    flight = PremiumFlight("PR-SOLUTION", mileage=1000)
    flight.add_passenger(Passenger(name, vip=True))
    return flight


def economy_standard_can_be_removed(name: str) -> EconomyFlight:
    """Rozwiązanie 1: zwykły pasażer może opuścić lot ekonomiczny."""
    flight = economy_with_passenger(name)
    flight.remove_passenger(name)
    return flight


def premium_duplicate_error(name: str) -> str:
    """Rozwiązanie 2: Premium dziedziczy regułę unikalności pasażera."""
    flight = premium_for_vip(name)
    try:
        flight.add_passenger(Passenger(name, vip=True))
    except DuplicatePassengerError as error:
        return str(error)
    raise AssertionError("duplicate passenger should have been rejected")


def student_bonus_points(mileage: int) -> int:
    """Rozwiązanie 3: student otrzymuje mileage // 15 punktów."""
    flight = EconomyFlight("STUDENT-SOLUTION", mileage=mileage)
    return flight.bonus_points(Passenger("Student", status="STUDENT"))


def passengers_from_table(rows: Iterable[dict[str, str]]) -> list[Passenger]:
    """Rozwiązanie 4: mapuje wiersze tabeli Gherkina na obiekty domeny."""
    return [
        Passenger(row["name"], status=row["status"])
        for row in rows
    ]
