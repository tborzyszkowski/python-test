"""Shopping Cart - logika cen rozwijana iteracyjnie przez TDD."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    category: str
    price_cents: int

    def __post_init__(self) -> None:
        if not self.sku:
            raise ValueError("sku must not be empty")
        if self.price_cents < 0:
            raise ValueError("price must be non-negative")


@dataclass
class CartLine:
    product: Product
    quantity: int


class ShoppingCart:
    def __init__(self) -> None:
        self._lines: dict[str, CartLine] = {}
        self._threshold_discount: tuple[int, float] | None = None
        self._three_for_two_categories: set[str] = set()

    def add(self, product: Product, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if product.sku in self._lines:
            self._lines[product.sku].quantity += quantity
        else:
            self._lines[product.sku] = CartLine(product, quantity)

    def remove(self, sku: str) -> None:
        try:
            del self._lines[sku]
        except KeyError:
            raise KeyError(f"unknown sku: {sku}") from None

    def apply_threshold_discount(self, minimum_cents: int, percent: float) -> None:
        if minimum_cents < 0 or not 0 <= percent <= 100:
            raise ValueError("invalid threshold discount")
        self._threshold_discount = (minimum_cents, percent)

    def enable_three_for_two(self, category: str) -> None:
        self._three_for_two_categories.add(category)

    def subtotal_cents(self) -> int:
        return sum(line.product.price_cents * line.quantity for line in self._lines.values())

    def promotion_discount_cents(self) -> int:
        discount = 0
        for line in self._lines.values():
            if line.product.category in self._three_for_two_categories:
                free_items = line.quantity // 3
                discount += free_items * line.product.price_cents
        return discount

    def threshold_discount_cents(self) -> int:
        if self._threshold_discount is None:
            return 0
        minimum, percent = self._threshold_discount
        base = self.subtotal_cents() - self.promotion_discount_cents()
        if base < minimum:
            return 0
        return int(base * percent // 100)

    def total_cents(self) -> int:
        subtotal = self.subtotal_cents()
        return max(0, subtotal - self.promotion_discount_cents() - self.threshold_discount_cents())

    def __len__(self) -> int:
        return sum(line.quantity for line in self._lines.values())


def main() -> None:
    book = Product("book", "ksiazka", "books", 5000)
    cart = ShoppingCart()
    cart.add(book, quantity=3)
    cart.enable_three_for_two("books")
    print("subtotal:", cart.subtotal_cents)
    print("three for two:", cart.promotion_discount_cents())
    print("total:", cart.total_cents())


if __name__ == "__main__":
    main()
