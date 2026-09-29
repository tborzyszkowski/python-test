"""Dlug technologiczny: dwie implementacje tego samego kontraktu."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineItem:
    name: str
    price_cents: int
    quantity: int = 1


class Invoice:
    """Czytelny model faktury, latwy do refaktoryzacji pod ochrona testow."""

    TAX_RATE = 0.23

    def __init__(self, items: list[LineItem], discount_percent: float = 0.0) -> None:
        self.items = list(items)
        self.discount_percent = discount_percent

    @property
    def subtotal_cents(self) -> int:
        return sum(item.price_cents * item.quantity for item in self.items)

    @property
    def discounted_cents(self) -> int:
        return int(self.subtotal_cents * (100 - self.discount_percent) // 100)

    @property
    def tax_cents(self) -> int:
        return int(self.discounted_cents * self.TAX_RATE)

    def total_cents(self) -> int:
        return self.discounted_cents + self.tax_cents


def total_legacy(items: list[dict[str, int]], discount_percent: float) -> int:
    """Wersja pozostawiona do porownania - dziala, ale laczy wiele odpowiedzialnosci."""
    gross = sum(item["price_cents"] * item["quantity"] for item in items)
    discounted = int(gross * (100 - discount_percent) // 100)
    return discounted + int(discounted * 0.23)


def main() -> None:
    items = [LineItem("ksiazka", 5000, 2), LineItem("notes", 1000)]
    invoice = Invoice(items, discount_percent=10.5)
    print("legacy:", total_legacy([item.__dict__ for item in items], 10.5))
    print("refactored:", invoice.total_cents())


if __name__ == "__main__":
    main()
