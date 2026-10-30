"""Minimalny system pokazujacy poziomy piramidy testow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price_cents: int


class Catalog(Protocol):
    """Publiczny kontrakt używany przez usługę katalogu."""

    def find(self, sku: str) -> Product:
        """Zwróć produkt dla SKU albo zgłoś KeyError."""
        ...


class MemoryCatalog:
    """Prosta zaleznosc integracyjna udajaca repozytorium katalogu."""

    def __init__(self, products: list[Product] | None = None) -> None:
        self._products = {product.sku: product for product in products or []}

    def find(self, sku: str) -> Product:
        try:
            return self._products[sku]
        except KeyError:
            raise KeyError(f"unknown sku: {sku}") from None


class CatalogService:
    """Logika biznesowa, ktora korzysta z katalogu przez publiczny kontrakt."""

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def price_for(self, sku: str, quantity: int = 1) -> int:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        product = self.catalog.find(sku)
        return product.price_cents * quantity

    def buy(self, sku: str, quantity: int = 1) -> dict[str, object]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        product = self.catalog.find(sku)
        return {
            "sku": product.sku,
            "name": product.name,
            "quantity": quantity,
            "total_cents": product.price_cents * quantity,
        }


def main() -> None:
    catalog = MemoryCatalog([Product("book", "Python TDD", 5000)])
    service = CatalogService(catalog)
    print(service.buy("book", quantity=2))


if __name__ == "__main__":
    main()
