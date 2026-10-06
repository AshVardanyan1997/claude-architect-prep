from src.api.orders import get_order


def test_get_order_found():
    assert get_order("A1002")["data"]["total"] == 64.0


def test_get_order_missing():
    assert get_order("ZZZ")["error"]["code"] == "not_found"
