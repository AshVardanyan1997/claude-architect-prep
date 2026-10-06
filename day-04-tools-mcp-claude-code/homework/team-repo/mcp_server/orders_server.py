"""A small MCP server over the orders API (stdio transport).

Claude Code starts it from .mcp.json and talks to it over stdin/stdout. Its tool
names, descriptions and errors are all Claude ever sees of it.

EXERCISE 4 (exam 2.1, 2.2):
  - get_data and get_info overlap and their descriptions say almost nothing, so
    the agent can't tell which to use (or uses Grep on the repo instead).
    Rename them to lookup_order (one order by exact ID) and search_orders
    (orders for a customer, optionally by status). Describe each: what it's for,
    input format with an example, what it returns, and when to use the other one.
  - Every failure is "Operation failed". Raise ToolError with a JSON string
    containing errorCategory (transient / validation / permission), isRetryable,
    and a message saying what to do next.
  - A search that matches nothing is NOT an error. Return an empty list.
"""

import json
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

mcp = FastMCP("orders")

ORDERS = {
    "A1002": {"customer_id": "C-101", "total": 64.00, "status": "delivered", "item": "Blender"},
    "A1007": {"customer_id": "C-204", "total": 899.00, "status": "processing", "item": "Espresso machine"},
    "B2210": {"customer_id": "C-301", "total": 120.00, "status": "in_transit", "item": "Running shoes"},
}
CARRIER_DOWN = {"B2210"}  # the carrier's tracking API times out for this order


class CarrierTimeout(Exception):
    pass


def _authorised() -> bool:
    return bool(os.environ.get("ORDERS_API_TOKEN"))


def _fetch(order_id: str) -> dict:
    if order_id in CARRIER_DOWN:
        raise CarrierTimeout(f"carrier tracking API timed out for {order_id}")
    return ORDERS[order_id]


@mcp.tool()
def get_data(order_id: str) -> str:
    """Gets data."""
    try:
        if not _authorised():
            raise PermissionError("no token")
        return json.dumps({"order_id": order_id, **_fetch(order_id.strip().upper())})
    except Exception:
        raise ToolError("Operation failed")


@mcp.tool()
def get_info(customer_id: str, status: str = "") -> str:
    """Gets information about orders."""
    if not _authorised():
        raise ToolError("Operation failed")
    hits = [{"order_id": k, **v} for k, v in ORDERS.items()
            if v["customer_id"] == customer_id.strip().upper() and (not status or v["status"] == status)]
    if not hits:
        raise ToolError("Operation failed")
    return json.dumps(hits)


if __name__ == "__main__":
    mcp.run()
