from debt_interest import Invoice, LineItem


def build_invoice() -> Invoice:
    return Invoice([LineItem("book", 5000, 2)], discount_percent=10)


def safe_total() -> int:
    return build_invoice().total_cents()
