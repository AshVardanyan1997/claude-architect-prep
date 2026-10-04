"""The extraction tool. Its input_schema IS the output format (exam task 4.3).

Claude never "runs" this tool. It calls record_invoice with the extracted data
as the tool input, and the host code reads that input. strict: true makes the
API guarantee the input matches the schema: no JSON syntax errors, no missing
fields, no values outside an enum.

EXERCISE 1 (exam task 4.3): this schema forces Claude to fill in every field,
even ones the document doesn't have. A required string can't be empty-handed,
so the model invents a value. Fix the schema so that:
  - fields a document may lack accept null (invoice_number, issue_date, due_date,
    purchase_order, currency, subtotal, tax_amount; think about line-item fields too)
  - category has an "other" value plus a category_detail field, and an "unclear" value
  - each description says what goes in the field and in what format
Strict mode rules: every object lists ALL its properties in "required" and sets
"additionalProperties": False. "May be absent" is expressed as "may be null",
for example {"anyOf": [{"type": "string"}, {"type": "null"}]}.
"""

LINE_ITEM = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "quantity": {"type": "number"},
        "unit_price": {"type": "number"},
        "amount": {"type": "number"},
    },
    "required": ["description", "quantity", "unit_price", "amount"],
    "additionalProperties": False,
}

EXTRACT_TOOL = {
    "name": "record_invoice",
    # TODO(exercise 1): fields and descriptions.
    "description": "Saves invoice data.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor_name": {"type": "string"},
            "invoice_number": {"type": "string"},
            "issue_date": {"type": "string", "description": "The date"},
            "due_date": {"type": "string", "description": "The due date"},
            "payment_terms": {"type": "string"},
            "purchase_order": {"type": "string"},
            "currency": {"type": "string"},
            "line_items": {"type": "array", "items": LINE_ITEM},
            "subtotal": {"type": "number"},
            "tax_amount": {"type": "number"},
            "total": {"type": "number"},
            "category": {"type": "string", "enum": ["goods", "services", "software_subscription", "travel"]},
        },
        "required": ["vendor_name", "invoice_number", "issue_date", "due_date", "payment_terms",
                     "purchase_order", "currency", "line_items", "subtotal", "tax_amount", "total", "category"],
        "additionalProperties": False,
    },
}
