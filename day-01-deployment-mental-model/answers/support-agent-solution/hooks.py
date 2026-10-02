"""Deterministic rules that run in YOUR code, around every tool call.

This is the layer that makes guarantees (exam tasks 1.4 and 1.5). The system
prompt can ask Claude to verify identity first; only code here can make sure it
always happens.

before_tool runs before a tool executes and can block it.
after_tool runs after a tool returns and can record facts or trim output.
"""

from datetime import datetime, timezone

REFUND_LIMIT = 500.00


def before_tool(name: str, tool_input: dict, state: dict) -> tuple[bool, str]:
    """Return (allowed, reason). If not allowed, the reason goes back to Claude as an error.

    EXERCISE 2: implement these two rules, then run `python test_hooks.py`.
      a) process_refund is blocked until state["verified_customer_id"] is set.
      b) process_refund above REFUND_LIMIT is blocked, and the reason tells Claude
         to use escalate_to_human instead (redirect, don't just refuse).
    """
    if name != "process_refund":
        return True, ""
    if not state.get("verified_customer_id"):
        return False, ("Blocked: the customer isn't verified. Call get_customer with their customer ID "
                       "or email first, then retry.")
    if tool_input.get("amount", 0) > REFUND_LIMIT:
        return False, (f"Blocked: refunds over ${REFUND_LIMIT:.0f} need a human. Call escalate_to_human "
                       "with a full handoff (customer, order, amount, what you checked, recommendation).")
    order = state.get("orders", {}).get(tool_input.get("order_id", "").upper())
    if order and order["customer_id"] != state["verified_customer_id"]:
        return False, "Blocked: this order belongs to a different customer."
    return True, ""


def after_tool(name: str, tool_input: dict, result: dict, state: dict) -> dict:
    """Record case facts, and optionally reshape the result before Claude sees it."""
    # A customer counts as verified only when one record matches their ID or email.
    # A name alone isn't enough, because names collide.
    if name == "get_customer" and result.get("match_count") == 1:
        match = result["matches"][0]
        if tool_input["query"].strip().lower() in (match["id"].lower(), match["email"].lower()):
            state["verified_customer_id"] = match["id"]
    if name == "lookup_order" and not result.get("isError"):
        state.setdefault("orders", {})[result["order_id"]] = {
            "amount": result["amount"], "status": result["status"], "customer_id": result["customer_id"]}

    # STRETCH (exam task 5.1): trim to what a support agent needs and normalise the timestamp.
    if name == "lookup_order" and not result.get("isError"):
        delivered = result.get("delivered_at")
        return {
            "order_id": result["order_id"], "customer_id": result["customer_id"], "item": result["item"],
            "amount": result["amount"], "status": result["status"],
            "delivered_at": datetime.fromtimestamp(delivered, timezone.utc).date().isoformat() if delivered else None,
            "return_window_days": result["return_window_days"],
        }
    return result
