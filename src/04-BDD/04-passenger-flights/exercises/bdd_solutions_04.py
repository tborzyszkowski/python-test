from flight_domain import EconomyFlight, Passenger, PremiumFlight


def economy_with_passenger(name: str, vip: bool = False) -> EconomyFlight:
    flight = EconomyFlight("EC-SOLUTION", mileage=1000)
    flight.add_passenger(Passenger(name, vip=vip))
    return flight


def premium_for_vip(name: str) -> PremiumFlight:
    flight = PremiumFlight("PR-SOLUTION", mileage=1000)
    flight.add_passenger(Passenger(name, vip=True))
    return flight
