from first_rules import is_business_day, normalize_code, percentage


def discount_for_total(total_cents: int) -> int:
    return percentage(total_cents, 10)


__all__ = ["discount_for_total", "is_business_day", "normalize_code", "percentage"]
