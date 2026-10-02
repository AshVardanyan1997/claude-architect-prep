"""Unit tests for the hooks. No API key needed and no cost, because no model is involved.

Run:  python test_hooks.py

These pass only once you've done exercise 2. Notice that they pass the same way
every time. That's the point of putting a rule in code instead of in the prompt.
"""

from hooks import before_tool

CASES = [
    # (description, tool, input, state, expected_allowed)
    ("refund blocked when customer not verified",
     "process_refund", {"order_id": "A1002", "amount": 64, "reason": "damaged"}, {}, False),
    ("refund allowed when verified and under limit",
     "process_refund", {"order_id": "A1002", "amount": 64, "reason": "damaged"}, {"verified_customer_id": "C-101"}, True),
    ("refund over $500 blocked even when verified",
     "process_refund", {"order_id": "A1007", "amount": 899, "reason": "defect"}, {"verified_customer_id": "C-101"}, False),
    ("refund of exactly $500 allowed",
     "process_refund", {"order_id": "A1007", "amount": 500, "reason": "partial"}, {"verified_customer_id": "C-101"}, True),
    ("other tools are never blocked",
     "lookup_order", {"order_id": "A1002"}, {}, True),
]

failed = 0
for desc, name, tool_input, state, expected in CASES:
    allowed, reason = before_tool(name, tool_input, state)
    ok = allowed == expected
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {desc}" + (f"  (reason: {reason})" if reason else ""))

# A blocked over-limit refund should redirect Claude to escalation, not just say no.
_, reason = before_tool("process_refund", {"order_id": "A1007", "amount": 899, "reason": "x"},
                        {"verified_customer_id": "C-101"})
redirect_ok = "escalate_to_human" in reason
failed += not redirect_ok
print(f"{'PASS' if redirect_ok else 'FAIL'}  over-limit reason points Claude to escalate_to_human")

print(f"\n{len(CASES) + 1 - failed}/{len(CASES) + 1} passed")
raise SystemExit(1 if failed else 0)
