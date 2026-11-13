"""Step definitions dla uruchamialnych przykładów struktury Behave."""

from behave import given, then, when
from flight_model import Flight, Passenger


@given('istnieje lot "{number}" z {capacity:d} miejscami')
def create_flight(context, number: str, capacity: int) -> None:
    context.flight = Flight(number, capacity)


@given('istnieje lot "{number}" z {capacity:d} miejscem')
def create_flight_with_one_place(context, number: str, capacity: int) -> None:
    create_flight(context, number, capacity)


@given('istnieje lot "{number}" z {capacity:d} miejscami i przebiegiem {mileage:d} km')
def create_flight_with_mileage(
    context,
    number: str,
    capacity: int,
    mileage: int,
) -> None:
    context.flight = Flight(number, capacity, mileage=mileage)


@given('pasażer "{name}" ma status "{status}"')
def create_passenger(context, name: str, status: str) -> None:
    context.passengers[name] = Passenger(name, status)


@given('lot ma następujących pasażerów:')
def create_passengers_from_table(context) -> None:
    context.passengers = {
        row["name"]: Passenger(row["name"], row["status"])
        for row in context.table
    }


@given('operator dodał pasażera "{name}" do lotu')
def add_passenger_as_given(context, name: str) -> None:
    _add_passenger(context, name)


@when('operator dodaje pasażera "{name}" do lotu')
def add_passenger(context, name: str) -> None:
    _add_passenger(context, name)


def _add_passenger(context, name: str) -> None:
    try:
        context.flight.add_passenger(context.passengers[name])
    except ValueError as error:
        context.error = error


@when('obliczam punkty dla pasażera "{name}"')
def calculate_points(context, name: str) -> None:
    context.points = context.flight.bonus_points(context.passengers[name])


@then('lot ma {count:d} pasażerów')
def flight_has_passenger_count(context, count: int) -> None:
    assert len(context.flight.passengers) == count


@then('lot ma {count:d} pasażera')
def flight_has_one_passenger(context, count: int) -> None:
    flight_has_passenger_count(context, count)


@then('pasażer "{name}" jest na liście')
def passenger_is_on_list(context, name: str) -> None:
    assert any(item.name == name for item in context.flight.passengers)
    assert context.error is None


@then('operacja kończy się błędem "{message}"')
def operation_has_error(context, message: str) -> None:
    assert context.error is not None
    assert str(context.error) == message


@then('pasażer otrzymuje {points:d} punktów')
def passenger_has_points(context, points: int) -> None:
    assert context.points == points
