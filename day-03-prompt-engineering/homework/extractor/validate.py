"""Semantic checks the schema can't express (exam task 4.3).

strict: true guarantees the record has the right SHAPE. It can't guarantee the
numbers add up or the dates make sense. That's this file's job, in plain code.

EXERCISE 4: implement check_semantics. It must flag:
  - a line where quantity x unit_price != amount (when both are present)
  - line items that don't sum to the subtotal (when there is a subtotal)
  - subtotal + tax != total (treat a null tax as 0)
  - no subtotal, and line items + tax != total
  - a date that isn't YYYY-MM-DD, and a due_date before the issue_date
  - category "other" with an empty category_detail
Compare money with a 0.01 tolerance, never with ==, because 0.1 + 0.2 != 0.3 in floats.
Every field may be None, so check before you add.
"""


def check_semantics(record: dict) -> list[str]:
    """Return a list of human-readable problems. An empty list means the record is consistent."""
    # TODO(exercise 4)
    return []
