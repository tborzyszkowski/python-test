from __future__ import annotations

from arch_sample.domain.order import Order
from arch_sample.services.order_service import OrderService


def use_service_without_outer_layer() -> Order:
    return OrderService(Order("lab", 100)).execute()
