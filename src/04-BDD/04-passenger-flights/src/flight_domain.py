"""Domena lotow i pasazerow - niezalezna od Behave."""

from __future__ import annotations

from dataclasses import dataclass


class FlightError(ValueError):
    """Błąd reguły domenowej lotu."""


class DuplicatePassengerError(FlightError):
    pass


class PassengerNotAllowedError(FlightError):
    pass


@dataclass(frozen=True)
class Passenger:
    name: str
    vip: bool = False


class Flight:
    def __init__(self, number: str, mileage: int) -> None:
        self.number = number
        self.mileage = mileage
        self._passengers: dict[str, Passenger] = {}

    def add_passenger(self, passenger: Passenger) -> None:
        if passenger.name in self._passengers:
            raise DuplicatePassengerError(f"passenger already on flight: {passenger.name}")
        self._validate_addition(passenger)
        self._passengers[passenger.name] = passenger

    def _validate_addition(self, passenger: Passenger) -> None:
        """Hook dla odmian lotu."""

    def remove_passenger(self, name: str) -> None:
        passenger = self._passengers.get(name)
        if passenger is None:
            raise FlightError(f"passenger not on flight: {name}")
        self._validate_removal(passenger)
        del self._passengers[name]

    def _validate_removal(self, passenger: Passenger) -> None:
        """Hook dla odmian lotu."""

    def has_passenger(self, name: str) -> bool:
        return name in self._passengers

    def bonus_points(self, passenger: Passenger) -> int:
        divisor = 10 if passenger.vip else 20
        return self.mileage // divisor

    @property
    def passengers(self) -> list[Passenger]:
        return list(self._passengers.values())


class EconomyFlight(Flight):
    def _validate_removal(self, passenger: Passenger) -> None:
        if passenger.vip:
            raise PassengerNotAllowedError("VIP passengers cannot be removed")


class PremiumFlight(Flight):
    def _validate_addition(self, passenger: Passenger) -> None:
        if not passenger.vip:
            raise PassengerNotAllowedError("only VIP passengers can join premium flight")
