"""Fake backend systems (CRM, orders, billing, ticketing).

In a real deployment these are separate services, usually reached through MCP
servers. Here they are in-memory so you can run everything locally. Claude is
real; only the company data is made up.

Every function returns a plain dict. Errors use a structured shape on purpose
(exam task 2.2): errorCategory, isRetryable, and a human-readable message.
"""

import random

CUSTOMERS = {
    "C-101": {"id": "C-101", "name": "Maria Lopez", "email": "maria@example.com", "zip": "94107", "tier": "gold"},
    "C-204": {"id": "C-204", "name": "John Smith", "email": "john.smith@example.com", "zip": "10001", "tier": "standard"},
    "C-205": {"id": "C-205", "name": "John Smith", "email": "jsmith77@example.com", "zip": "60614", "tier": "standard"},
    "C-301": {"id": "C-301", "name": "Aiko Tanaka", "email": "aiko@example.com", "zip": "98101", "tier": "standard"},
}

ORDERS = {
    "A1002": {"order_id": "A1002", "customer_id": "C-101", "item": "Ceramic teapot", "amount": 64.00,
              "status": "delivered", "delivered_at": 1790812800, "return_window_days": 30},
    "A1007": {"order_id": "A1007", "customer_id": "C-101", "item": "65-inch TV", "amount": 899.00,
              "status": "delivered", "delivered_at": 1790985600, "return_window_days": 30},
    "B2210": {"order_id": "B2210", "customer_id": "C-301", "item": "Running shoes", "amount": 120.00,
              "status": "in_transit", "delivered_at": None, "return_window_days": 30},
}

REFUNDS = []
TICKETS = []


def _error(category, retryable, message):
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "message": message}


def get_customer(query: str) -> dict:
    """Search customers by ID, email, or name. Can return several matches."""
    q = query.strip().lower()
    matches = [c for c in CUSTOMERS.values()
               if q in (c["id"].lower(), c["email"].lower(), c["name"].lower())]
    return {"matches": matches, "match_count": len(matches)}


def lookup_order(order_id: str) -> dict:
    """Return the full order record. Occasionally times out, like real systems do."""
    if random.random() < 0.10:
        return _error("transient", True, "Order service timed out. Safe to retry once.")
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return _error("validation", False, f"No order with id '{order_id}'. Ask the customer to check the number.")
    # Real systems return far more than you need (exam task 5.1: trim tool output).
    return {**order, "warehouse": "SFO-3", "carrier": "UPS", "sku": "SKU-" + order["order_id"],
            "internal_notes": "", "fraud_score": 0.02, "tax": round(order["amount"] * 0.0875, 2)}


def process_refund(order_id: str, amount: float, reason: str) -> dict:
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return _error("validation", False, f"No order with id '{order_id}'.")
    if amount > order["amount"]:
        return _error("business", False, "Refund cannot exceed the order amount.")
    if order["status"] != "delivered":
        return _error("business", False, "Order has not been delivered yet, so it can't be refunded. Offer to cancel instead.")
    REFUNDS.append({"order_id": order["order_id"], "amount": amount, "reason": reason})
    return {"refund_id": f"R-{len(REFUNDS):04d}", "status": "approved", "amount": amount}


def escalate_to_human(handoff: dict) -> dict:
    TICKETS.append(handoff)
    return {"ticket_id": f"T-{len(TICKETS):04d}", "queue": "tier-2", "status": "queued"}
