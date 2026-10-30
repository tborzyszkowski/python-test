from __future__ import annotations

import pytest
from layered_system import CatalogService, MemoryCatalog, Product


class StubCatalog:
    """Minimalna zależność kontrolowana przez test jednostkowy."""

    def __init__(self, product: Product) -> None:
        self.product = product
        self.lookups: list[str] = []

    def find(self, sku: str) -> Product:
        self.lookups.append(sku)
        if sku != self.product.sku:
            raise KeyError(f"unknown sku: {sku}")
        return self.product


def test_unit_level_business_rule_calculates_total():
    catalog = StubCatalog(Product("book", "TDD", 5000))
    service = CatalogService(catalog)

    assert service.price_for("book", quantity=2) == 10_000
    assert catalog.lookups == ["book"]


def test_integration_level_connects_service_and_catalog():
    catalog = MemoryCatalog([Product("book", "TDD", 5000)])
    service = CatalogService(catalog)

    assert service.buy("book", 2) == {
        "sku": "book",
        "name": "TDD",
        "quantity": 2,
        "total_cents": 10_000,
    }


def test_unknown_product_is_reported_at_boundary():
    service = CatalogService(MemoryCatalog())

    with pytest.raises(KeyError, match="unknown sku"):
        service.buy("missing")


@pytest.mark.parametrize("quantity", [0, -1])
def test_buy_rejects_non_positive_quantity_before_catalog_lookup(quantity):
    catalog = StubCatalog(Product("book", "TDD", 5000))

    with pytest.raises(ValueError, match="quantity must be positive"):
        CatalogService(catalog).buy("book", quantity)

    assert catalog.lookups == []
