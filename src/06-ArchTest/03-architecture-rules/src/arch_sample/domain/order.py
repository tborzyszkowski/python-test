from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    total_cents: int

    def is_free(self) -> bool:
        return self.total_cents == 0
