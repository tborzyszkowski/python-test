from __future__ import annotations

from abc import ABC, abstractmethod


class BaseService(ABC):
    @abstractmethod
    def execute(self) -> object:
        raise NotImplementedError
