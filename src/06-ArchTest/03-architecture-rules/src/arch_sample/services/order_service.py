from __future__ import annotations

from arch_sample.domain.order import Order
from arch_sample.services.base import BaseService


class OrderService(BaseService):
    def __init__(self, order: Order) -> None:
        self.order = order

    def execute(self) -> Order:
        return self.order
