"""Orders API handlers."""

ORDERS = {"A1002": {"customer": "C-101", "total": 64.0, "status": "delivered"}}


def get_order(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": {"code": "not_found", "message": f"order {order_id} not found"}}
    return {"data": order}
