from __future__ import annotations

from arch_sample.domain.order import Order
from arch_sample.services.order_service import OrderService


def get_order(order_id: str) -> dict[str, object]:
    order = OrderService(Order(order_id, total_cents=1000)).execute()
    return {"order_id": order.order_id, "total_cents": order.total_cents}
