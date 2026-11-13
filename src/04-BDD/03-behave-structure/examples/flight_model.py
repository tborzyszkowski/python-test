"""Minimalny model domeny używany przez przykłady Behave."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Passenger:
    name: str
    status: str


@dataclass
class Flight:
    number: str
    capacity: int
    mileage: int = 0
    passengers: list[Passenger] = field(default_factory=list)

    def add_passenger(self, passenger: Passenger) -> None:
        if len(self.passengers) >= self.capacity:
            raise ValueError("flight is full")
        if any(item.name == passenger.name for item in self.passengers):
            raise ValueError("passenger already exists")
        self.passengers.append(passenger)

    def bonus_points(self, passenger: Passenger) -> int:
        multiplier = 2 if passenger.status == "VIP" else 1
        return self.mileage // 10 * multiplier
