"""Free tests (no API calls) for the schema, the host code and the validator.

Run:  python test_offline.py
The starter fails most of these on purpose. Each failure names the exercise that fixes it.
"""

from types import SimpleNamespace

from extract import extract
from schema import EXTRACT_TOOL
from validate import check_semantics

PROPS = EXTRACT_TOOL["input_schema"]["properties"]
results = []


def check(name, condition):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def accepts_null(prop):
    if not isinstance(prop, dict):
        return False
    if prop.get("type") == "null" or (isinstance(prop.get("type"), list) and "null" in prop["type"]):
        return True
    return any(accepts_null(p) for p in prop.get("anyOf", []))


def objects(schema):
    if not isinstance(schema, dict):  # e.g. a Python set typo; check_schema.py names it
        return
    if schema.get("type") == "object":
        yield schema
        for p in schema.get("properties", {}).values():
            yield from objects(p)
    for p in schema.get("anyOf", []):
        yield from objects(p)
    if "items" in schema:
        yield from objects(schema["items"])


# A record shaped like a correct extraction of d1-formal-invoice.txt
GOOD = {"vendor_name": "Northwind Supplies Ltd", "invoice_number": "INV-2026-0412", "issue_date": "2026-09-03",
        "due_date": "2026-10-03", "payment_terms": "Net 30", "purchase_order": "PO-7781", "currency": "USD",
        "line_items": [{"description": "Ergonomic office chair", "quantity": 3, "unit_price": 149.0, "amount": 447.0},
                       {"description": "LED desk lamp", "quantity": 2, "unit_price": 32.5, "amount": 65.0}],
        "subtotal": 512.0, "tax_amount": 40.96, "total": 552.96, "category": "goods", "category_detail": None}


def variant(**changes):
    return {**GOOD, **changes}


print("Exercise 1: the schema (schema.py)")
check("strict: true is set on the tool", EXTRACT_TOOL.get("strict") is True)
check("every object lists all its properties as required and sets additionalProperties: false (strict mode rule)",
      all(set(o.get("required", [])) == set(o.get("properties", {})) and o.get("additionalProperties") is False
          for o in objects(EXTRACT_TOOL["input_schema"])))
for field in ("invoice_number", "issue_date", "due_date", "purchase_order", "currency", "subtotal", "tax_amount"):
    check(f"{field} accepts null (documents can lack it)", field in PROPS and accepts_null(PROPS[field]))
enum = PROPS.get("category", {}).get("enum", [])
check("category enum has 'other' and 'unclear'", "other" in enum and "unclear" in enum)
check("category_detail exists and accepts null", "category_detail" in PROPS and accepts_null(PROPS["category_detail"]))

print("\nExercise 3: host code (extract.py)")


def text(t):
    return SimpleNamespace(type="text", text=t)


def tool(data):
    return SimpleNamespace(type="tool_use", name=EXTRACT_TOOL["name"], id="toolu_1", input=data)


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.sent = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.sent.append([dict(m) for m in kwargs["messages"]])
        content = self.responses.pop(0)
        stop = "tool_use" if any(b.type == "tool_use" for b in content) else "end_turn"
        return SimpleNamespace(content=content, stop_reason=stop)


r = extract("doc", FakeClient([tool(GOOD)]))
check("a tool call on the first response becomes the record", r["record"] == GOOD and r["error"] is None)

fake = FakeClient([text('Here is the data: {"total": 1}')], [tool(GOOD)])
r = extract("doc", fake)
check("a text-only reply is NOT parsed as the record; the host asks again", r["record"] == GOOD and len(fake.sent) == 2)
check("the retry tells the model it didn't call the tool",
      len(fake.sent) == 2 and "record_invoice" in str(fake.sent[1][-1]["content"]))

r = extract("doc", FakeClient([text("I can't find an invoice here.")], [text("Still no invoice.")]))
check("two text-only replies give record None and an error, not an empty record",
      r["record"] is None and bool(r.get("error")))

print("\nExercise 4: semantic validator (validate.py)")
check("a consistent invoice has no problems", check_semantics(GOOD) == [])
problems = check_semantics(variant(subtotal=522.0, total=562.96))
check("line items that don't sum to the subtotal are flagged", any("subtotal" in p for p in problems))
check("subtotal + tax != total is flagged", check_semantics(variant(total=600.0)) != [])
bad_line = variant(line_items=[{**GOOD["line_items"][0], "amount": 400.0}, GOOD["line_items"][1]],
                   subtotal=465.0, total=505.96)
check("quantity x unit price != line amount is flagged", any("line 1" in p for p in check_semantics(bad_line)))
check("due_date before issue_date is flagged", check_semantics(variant(due_date="2026-08-01")) != [])
check("'other' without category_detail is flagged", check_semantics(variant(category="other")) != [])
receipt = variant(invoice_number=None, due_date=None, payment_terms=None, purchase_order=None, subtotal=None,
                  tax_amount=None, total=512.0)
check("nulls are handled: no subtotal and no tax, items equal the total -> no problems",
      check_semantics(receipt) == [])
check("nulls are handled: no subtotal, items don't reach the total -> flagged",
      check_semantics({**receipt, "total": 600.0}) != [])

print(f"\n{sum(results)}/{len(results)} passed")
