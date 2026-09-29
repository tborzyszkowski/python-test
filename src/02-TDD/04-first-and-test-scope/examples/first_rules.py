"""Deterministyczne reguly biznesowe dobrze nadajace sie do testow."""

from __future__ import annotations

from datetime import date


def percentage(value: int, percent: float) -> int:
    if value < 0:
        raise ValueError("value must be non-negative")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return int(value * percent // 100)


def is_business_day(day: date) -> bool:
    return day.weekday() < 5


def normalize_code(value: str) -> str:
    if not value.strip():
        raise ValueError("code must not be empty")
    return "-".join(value.strip().upper().split())


def main() -> None:
    print("10% z 9999 groszy:", percentage(9999, 10))
    print("kod:", normalize_code("  tdd  red  "))


if __name__ == "__main__":
    main()
