from __future__ import annotations

from behave import given, then, when
from flight_domain import EconomyFlight, Passenger, PremiumFlight


def _passenger(context, name: str) -> Passenger:
    try:
        return context.passengers[name]
    except KeyError:
        raise AssertionError(f"unknown passenger in scenario: {name}") from None


@given('istnieje lot ekonomiczny o numerze "{number}"')
def economy_flight(context, number: str) -> None:
    context.flight = EconomyFlight(number, mileage=1000)
    context.passengers = {}
    context.error = None


@given('istnieje lot premium o numerze "{number}"')
def premium_flight(context, number: str) -> None:
    context.flight = PremiumFlight(number, mileage=1000)
    context.passengers = {}
    context.error = None


@given('istnieje standardowy pasażer "{name}"')
def standard_passenger(context, name: str) -> None:
    context.passengers[name] = Passenger(name, vip=False)


@given('istnieje pasażer VIP "{name}"')
def vip_passenger(context, name: str) -> None:
    context.passengers[name] = Passenger(name, vip=True)


@given('pasażer "{name}" jest na locie')
def passenger_on_flight(context, name: str) -> None:
    context.flight.add_passenger(_passenger(context, name))


@when('dodaję pasażera "{name}" do lotu')
def add_passenger(context, name: str) -> None:
    try:
        context.flight.add_passenger(_passenger(context, name))
    except Exception as error:  # przechwytujemy, aby Then opisał rezultat biznesowy
        context.error = error


@when('ponownie dodaję pasażera "{name}" do lotu')
def add_duplicate_passenger(context, name: str) -> None:
    add_passenger(context, name)


@when('usuwam pasażera "{name}" z lotu')
def remove_passenger(context, name: str) -> None:
    try:
        context.flight.remove_passenger(name)
    except Exception as error:
        context.error = error


@then('pasażer "{name}" jest na locie')
def passenger_is_on_flight(context, name: str) -> None:
    assert context.flight.has_passenger(name)
    assert context.error is None


@then('pasażer "{name}" nie jest na locie')
def passenger_is_not_on_flight(context, name: str) -> None:
    assert not context.flight.has_passenger(name)
    assert context.error is None


@then('operacja jest odrzucona komunikatem "{message}"')
def operation_rejected(context, message: str) -> None:
    assert context.error is not None
    assert message in str(context.error)


@given('pasażer "{name}" ma status "{status}"')
def points_passenger(context, name: str, status: str) -> None:
    context.passengers = {name: Passenger(name, vip=status.upper() == "VIP")}


@given('przebieg lotu wynosi {mileage:d} kilometrów')
def mileage(context, mileage: int) -> None:
    context.mileage = mileage


@when('naliczam punkty dla pasażera "{name}"')
def calculate_points(context, name: str) -> None:
    context.points = context.mileage // (10 if _passenger(context, name).vip else 20)


@then('pasażer otrzymuje {points:d} punktów')
def points_result(context, points: int) -> None:
    assert context.points == points
