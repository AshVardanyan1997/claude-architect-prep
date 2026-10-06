"""Semantic checks the schema can't express (exam task 4.3).

strict: true guarantees the record has the right SHAPE. It can't guarantee the
numbers add up or the dates make sense. That's this file's job, in plain code.
"""

from datetime import date

TOLERANCE = 0.01


def _close(a, b):
    return abs(a - b) <= TOLERANCE


def check_semantics(record: dict) -> list[str]:
    """Return a list of human-readable problems. An empty list means the record is consistent."""
    problems = []
    items = record.get("line_items") or []
    subtotal, tax, total = record.get("subtotal"), record.get("tax_amount"), record.get("total")
    items_sum = round(sum(i["amount"] for i in items), 2)

    for i, item in enumerate(items, 1):
        q, p = item.get("quantity"), item.get("unit_price")
        if q is not None and p is not None and not _close(q * p, item["amount"]):
            problems.append(f"line {i}: {q} x {p} = {q * p:.2f}, but the amount is {item['amount']:.2f}")

    if items and subtotal is not None and not _close(items_sum, subtotal):
        problems.append(f"line items sum to {items_sum:.2f}, but the subtotal is {subtotal:.2f}")
    if subtotal is not None and not _close(subtotal + (tax or 0), total):
        problems.append(f"subtotal {subtotal:.2f} + tax {tax or 0:.2f} doesn't equal the total {total:.2f}")
    if items and subtotal is None and not _close(items_sum + (tax or 0), total):
        problems.append(f"line items {items_sum:.2f} + tax {tax or 0:.2f} doesn't equal the total {total:.2f}")

    parsed = {}
    for field in ("issue_date", "due_date"):
        value = record.get(field)
        if value is not None:
            try:
                parsed[field] = date.fromisoformat(value)
            except ValueError:
                problems.append(f"{field} '{value}' isn't a YYYY-MM-DD date")
    if len(parsed) == 2 and parsed["due_date"] < parsed["issue_date"]:
        problems.append("due_date is before issue_date")

    if record.get("category") == "other" and not record.get("category_detail"):
        problems.append("category is 'other' but category_detail is empty")
    return problems
