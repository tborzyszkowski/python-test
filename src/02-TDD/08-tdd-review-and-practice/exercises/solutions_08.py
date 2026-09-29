"""Minimalny szablon sprawozdania z laboratorium TDD."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TddIteration:
    number: int
    red_test: str
    green_change: str
    refactor: str
    test_level: str


ITERATIONS = [
    TddIteration(1, "empty state", "return empty result", "name public query", "unit"),
    TddIteration(2, "add item", "store item", "extract value object", "unit"),
    TddIteration(3, "invalid item", "raise domain error", "centralize validation", "unit"),
    TddIteration(4, "two components", "wire fake", "separate adapter", "integration"),
    TddIteration(5, "acceptance scenario", "compose workflow", "remove duplication", "acceptance"),
]
