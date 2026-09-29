from __future__ import annotations

import inspect

from arch_sample.services.base import BaseService
from arch_sample.services.order_service import OrderService


def test_service_classes_are_in_services_and_extend_base_service():
    service_classes = [OrderService]
    for service_class in service_classes:
        assert service_class.__name__.endswith("Service")
        assert issubclass(service_class, BaseService)
        assert inspect.getmodule(service_class).__name__.startswith("arch_sample.services")
