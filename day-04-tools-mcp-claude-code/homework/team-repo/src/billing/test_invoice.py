from src.billing.invoice import invoice_total


def test_invoice_total_with_tax():
    assert invoice_total([{"qty": 2, "unit_price": 10.0}], 0.1) == 22.0
