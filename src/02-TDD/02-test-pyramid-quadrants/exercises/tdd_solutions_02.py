from layered_system import CatalogService, MemoryCatalog, Product


def build_service() -> CatalogService:
    return CatalogService(MemoryCatalog([Product("book", "TDD", 5000)]))


def acceptance_buy_book() -> dict[str, object]:
    return build_service().buy("book", quantity=2)
