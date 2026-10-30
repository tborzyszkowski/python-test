from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

import arch_sample.services
from arch_sample.services.base import BaseService


def test_service_classes_are_in_services_and_extend_base_service():
    services_path = Path(inspect.getfile(arch_sample.services)).parent
    modules = (
        importlib.import_module(module.name)
        for module in pkgutil.iter_modules(
            [str(services_path)],
            prefix="arch_sample.services.",
        )
    )
    service_classes = [
        member
        for module in modules
        for _, member in inspect.getmembers(module, inspect.isclass)
        if member.__module__ == module.__name__
        and not inspect.isabstract(member)
        and member is not BaseService
    ]

    assert service_classes, "at least one concrete service class must exist"
    for service_class in service_classes:
        assert service_class.__name__.endswith("Service")
        assert issubclass(service_class, BaseService)
        assert inspect.getmodule(service_class).__name__.startswith("arch_sample.services")
