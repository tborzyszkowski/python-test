from __future__ import annotations

import io

import pytest
from racing_and_html import HtmlPagesConverter, RacingCar, StubPressureSensor


def test_stub_pressure_outside_norm_makes_car_not_ready():
    car = RacingCar(StubPressureSensor([1.2, 1.1, 1.0, 0.7]))

    assert car.check_tires() is False


def test_stub_pressure_in_norm_makes_car_ready():
    car = RacingCar(StubPressureSensor([1.2, 1.1, 1.0, 1.3]))

    assert car.check_tires() is True


def test_missing_pressure_reading_is_an_error():
    car = RacingCar(StubPressureSensor([1.2]))

    with pytest.raises(RuntimeError, match="unavailable"):
        car.check_tires()


def test_converter_returns_markdown():
    converter = HtmlPagesConverter()

    assert converter.convert("<h1>Title</h1><p>Text</p>") == "# Title\nText\n"


def test_converter_writes_to_stringio_fake():
    output = io.StringIO()
    converter = HtmlPagesConverter()

    converter.convert("<p>Hello</p>", output)

    assert output.getvalue() == "Hello\n"
