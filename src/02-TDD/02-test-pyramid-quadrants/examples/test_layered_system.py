from __future__ import annotations

import pytest
from layered_system import CatalogService, MemoryCatalog, Product


def test_unit_level_business_rule_calculates_total():
    service = CatalogService(MemoryCatalog([Product("book", "TDD", 5000)]))

    assert service.price_for("book", quantity=2) == 10_000


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
