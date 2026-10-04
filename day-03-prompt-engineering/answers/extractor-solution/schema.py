"""The extraction tool. Its input_schema IS the output format (exam task 4.3).

Claude never "runs" this tool. It calls record_invoice with the extracted data
as the tool input, and the host code reads that input. strict: true makes the
API guarantee the input matches the schema: no JSON syntax errors, no missing
fields, no values outside an enum.
"""


def nullable(schema: dict, description: str) -> dict:
    """A field that may legitimately be absent from the document."""
    return {"anyOf": [schema, {"type": "null"}], "description": description}


DATE = {"type": "string", "format": "date"}  # YYYY-MM-DD

LINE_ITEM = {
    "type": "object",
    "properties": {
        "description": {"type": "string", "description": "The item as written, translated to English if needed."},
        "quantity": nullable({"type": "number"}, "Quantity if stated, else null."),
        "unit_price": nullable({"type": "number"}, "Price per unit if stated, else null."),
        "amount": {"type": "number", "description": "The line total as printed."},
    },
    "required": ["description", "quantity", "unit_price", "amount"],
    "additionalProperties": False,
}

EXTRACT_TOOL = {
    "name": "record_invoice",
    "description": (
        "Record the data extracted from one invoice, receipt or billing document. Call it exactly "
        "once per document. Every field must come from the document itself: use null for anything "
        "the document doesn't state, rather than guessing or calculating it."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor_name": {"type": "string", "description": "The business that issued the document."},
            "invoice_number": nullable({"type": "string"}, "The document's own number or reference, exactly as printed."),
            "issue_date": nullable(DATE, "Date the document was issued, as YYYY-MM-DD."),
            "due_date": nullable(DATE, "Payment due date as YYYY-MM-DD, only if a calendar date is printed."),
            "payment_terms": nullable({"type": "string"}, "Payment terms as written, e.g. 'Net 30', 'Due on receipt'."),
            "purchase_order": nullable({"type": "string"}, "The customer's purchase order number, if printed."),
            "currency": nullable({"type": "string"}, "ISO 4217 code (USD, EUR, GBP), only if a symbol, code or name appears."),
            "line_items": {"type": "array", "items": LINE_ITEM},
            "subtotal": nullable({"type": "number"}, "Pre-tax amount as printed."),
            "tax_amount": nullable({"type": "number"}, "Tax as printed. 0 if the document says no tax is charged; null if tax isn't mentioned."),
            "total": {"type": "number", "description": "The final amount due or paid, as printed."},
            "category": {
                "type": "string",
                "enum": ["goods", "services", "software_subscription", "travel", "other", "unclear"],
                "description": "Expense category. 'other' when none of the named categories fits; "
                               "'unclear' when the document doesn't say what was bought.",
            },
            "category_detail": nullable({"type": "string"}, "Required when category is 'other': what the expense is. Otherwise null."),
        },
        "required": ["vendor_name", "invoice_number", "issue_date", "due_date", "payment_terms",
                     "purchase_order", "currency", "line_items", "subtotal", "tax_amount", "total",
                     "category", "category_detail"],
        "additionalProperties": False,
    },
}
