from tdd_solutions_03 import build_invoice, safe_total


def test_solution_keeps_invoice_contract():
    invoice = build_invoice()
    assert invoice.discounted_cents == 9000
    assert safe_total() == 11_070
