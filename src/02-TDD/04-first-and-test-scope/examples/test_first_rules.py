from datetime import date

import pytest
from first_rules import is_business_day, normalize_code, percentage


def test_percentage_rounds_down_by_contract():
    assert percentage(9999, 10) == 999


@pytest.mark.parametrize("bad_percent", [-1, 100.1])
def test_percentage_rejects_invalid_percent(bad_percent):
    with pytest.raises(ValueError, match="between"):
        percentage(100, bad_percent)


@pytest.mark.parametrize("day", [date(2026, 9, 28), date(2026, 9, 29)])
def test_weekdays_are_business_days(day):
    assert is_business_day(day) is True


def test_sunday_is_not_business_day():
    assert is_business_day(date(2026, 9, 27)) is False


def test_normalize_code_is_public_behavior():
    assert normalize_code("  tdd   red ") == "TDD-RED"


def test_normalize_code_rejects_empty_value():
    with pytest.raises(ValueError, match="empty"):
        normalize_code("  ")
