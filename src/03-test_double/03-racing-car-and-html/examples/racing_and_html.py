"""Stub czujnika i Fake StringIO w praktycznych komponentach."""

from __future__ import annotations

import io
from collections.abc import Iterable
from typing import TextIO


class StubPressureSensor:
    """Stub: symuluje czujnik ciśnienia z przygotowaną sekwencją odczytów."""
    def __init__(self, readings: Iterable[float]) -> None:
        self._readings = iter(readings)

    def read_pressure(self) -> float:
        """Zwróć następny odczyt ciśnienia lub zgłoś RuntimeError."""
        try:
            return next(self._readings)
        except StopIteration:
            raise RuntimeError("pressure reading unavailable") from None


class RacingCar:
    """Samochód wyścigowy: sprawdza ciśnienie przed startem."""
    MIN_PRESSURE = 1.0

    def __init__(self, sensor: StubPressureSensor) -> None:
        self.sensor = sensor

    def check_tires(self) -> bool:
        """Sprawdzić czy wszystkie 4 koła mają wystarczające ciśnienie."""
        return all(self.sensor.read_pressure() >= self.MIN_PRESSURE for _ in range(4))


class HtmlPagesConverter:
    """Konwerter HTML na Markdown."""
    def convert(self, html: str, output: TextIO | None = None) -> str:
        """Zamień HTML na Markdown. Opcjonalnie zapisz do strumienia."""
        markdown = self._to_markdown(html)
        if output is not None:
            output.write(markdown)
        return markdown

    @staticmethod
    def _to_markdown(html: str) -> str:
        """Prywatna metoda: transformacja HTML -> Markdown."""
        result = html.replace("<h1>", "# ").replace("</h1>", "\n")
        result = result.replace("<p>", "").replace("</p>", "\n")
        return result.strip() + "\n"


def main() -> None:
    """Demonstruje użycie Stub i Fake."""
    car = RacingCar(StubPressureSensor([1.2, 1.1, 1.0, 0.7]))
    print("tyres ready:", car.check_tires())
    output = io.StringIO()
    markdown = HtmlPagesConverter().convert("<h1>Title</h1><p>Text</p>", output)
    print("markdown:", markdown, "fake file:", output.getvalue())


if __name__ == "__main__":
    main()
