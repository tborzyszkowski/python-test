from __future__ import annotations

import inspect

from arch_sample.services.base import BaseService
from arch_sample.services.order_service import OrderService


def valid_service_class() -> bool:
    return (
        OrderService.__name__.endswith("Service")
        and issubclass(OrderService, BaseService)
        and inspect.getmodule(OrderService).__name__.startswith("arch_sample.services")
    )
