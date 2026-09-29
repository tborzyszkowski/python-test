from debt_interest import Invoice, LineItem, total_legacy


def test_legacy_and_refactored_invoice_have_same_public_result():
    items = [LineItem("book", 5000, 2), LineItem("pen", 1000)]

    assert Invoice(items, 10.5).total_cents() == total_legacy(
        [item.__dict__ for item in items], 10.5
    )


def test_invoice_subtotal_is_independent_from_tax():
    invoice = Invoice([LineItem("book", 5000, 2)], discount_percent=10)

    assert invoice.subtotal_cents == 10_000
    assert invoice.discounted_cents == 9_000
    assert invoice.tax_cents == 2_070
