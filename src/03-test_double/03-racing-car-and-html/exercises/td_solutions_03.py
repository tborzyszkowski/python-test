import io

from racing_and_html import HtmlPagesConverter, RacingCar, StubPressureSensor


def safe_car(readings: list[float]) -> bool:
    return RacingCar(StubPressureSensor(readings)).check_tires()


def converted_text(html: str) -> str:
    output = io.StringIO()
    HtmlPagesConverter().convert(html, output)
    return output.getvalue()
