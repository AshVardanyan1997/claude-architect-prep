"""A small MCP server over the orders API (stdio transport).

Claude Code starts it from .mcp.json and talks to it over stdin/stdout. Its tool
names, descriptions and errors are all Claude ever sees of it.
"""

import json
import os
import re

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

mcp = FastMCP("orders")

ORDERS = {
    "A1002": {"customer_id": "C-101", "total": 64.00, "status": "delivered", "item": "Blender"},
    "A1007": {"customer_id": "C-204", "total": 899.00, "status": "processing", "item": "Espresso machine"},
    "B2210": {"customer_id": "C-301", "total": 120.00, "status": "in_transit", "item": "Running shoes"},
}
CARRIER_DOWN = {"B2210"}  # the carrier's tracking API times out for this order
STATUSES = ["processing", "in_transit", "delivered", "cancelled"]


class CarrierTimeout(Exception):
    pass


def _fail(category: str, retryable: bool, message: str):
    """Raise an MCP error (isError: true) whose text is structured JSON the agent can act on."""
    raise ToolError(json.dumps({"errorCategory": category, "isRetryable": retryable, "message": message}))


def _require_token():
    if not os.environ.get("ORDERS_API_TOKEN"):
        _fail("permission", False, "The orders API token isn't configured, so no order data can be read. "
                                   "Tell the user to set ORDERS_API_TOKEN; retrying won't help.")


def _fetch(order_id: str) -> dict:
    if order_id in CARRIER_DOWN:
        raise CarrierTimeout(f"carrier tracking API timed out for {order_id}")
    return ORDERS[order_id]


@mcp.tool()
def lookup_order(order_id: str) -> str:
    """Get one order by its exact order ID, for example 'A1002' (a letter followed by 4 digits).

    Returns the order's customer_id, item, total in USD and status (processing, in_transit,
    delivered or cancelled). Use this when the user gives an order number. If you only have a
    customer ID such as 'C-101', or want all of a customer's orders, use search_orders instead.
    Prefer this tool over searching the repository: order data is not in the code.
    """
    _require_token()
    order_id = order_id.strip().upper()
    if not re.fullmatch(r"[A-Z]\d{4}", order_id):
        _fail("validation", False, f"'{order_id}' isn't an order ID. IDs look like 'A1002'. Ask the user to check it.")
    try:
        return json.dumps({"order_id": order_id, **_fetch(order_id)})
    except CarrierTimeout:
        _fail("transient", True, f"The carrier's tracking service timed out for {order_id}. Retry once; if it "
                                 "fails again, tell the user the status is temporarily unavailable.")
    except KeyError:
        _fail("validation", False, f"No order {order_id} exists. Ask the user to check the number, or use "
                                   "search_orders with their customer ID.")


@mcp.tool()
def search_orders(customer_id: str, status: str = "") -> str:
    """List a customer's orders by customer ID, for example 'C-101', optionally filtered by status.

    status is one of processing, in_transit, delivered, cancelled; leave it empty for all orders.
    Returns {"orders": [...]}, each with order_id, item, total and status. An empty list means the
    customer has no matching orders, which is a valid answer, not an error. If the user gives a
    specific order number like 'A1002', use lookup_order instead.
    """
    _require_token()
    if status and status not in STATUSES:
        _fail("validation", False, f"Unknown status '{status}'. Use one of: {', '.join(STATUSES)}, or leave it empty.")
    customer_id = customer_id.strip().upper()
    hits = [{"order_id": k, **v} for k, v in ORDERS.items()
            if v["customer_id"] == customer_id and (not status or v["status"] == status)]
    return json.dumps({"orders": hits})


@mcp.resource("orders://statuses")
def order_statuses() -> str:
    """The order status values and what each means, so the agent doesn't have to probe for them."""
    return json.dumps({"processing": "paid, not shipped", "in_transit": "with the carrier",
                       "delivered": "carrier confirmed delivery", "cancelled": "no charge, no shipment"})


if __name__ == "__main__":
    mcp.run()
