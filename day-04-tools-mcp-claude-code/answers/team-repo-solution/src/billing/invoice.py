"""Invoice totals."""


def invoice_total(lines: list[dict], tax_rate: float) -> float:
    subtotal = sum(line["qty"] * line["unit_price"] for line in lines)
    return round(subtotal * (1 + tax_rate), 2)
