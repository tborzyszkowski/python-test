"""Kod produkcyjny do ćwiczeń z tematu 05 (struktura AAA).

Ten plik **nie jest testem** - to kod, który będziemy testować. Współdzielą go
``tasks_05.py`` (treść zadania) i ``test_solutions_05.py`` (wzorcowe testy),
dzięki czemu nie mamy dwóch kopii tego samego kodu.

Zwróć uwagę na dwie decyzje projektowe, które ułatwiają testowanie:

* kwoty trzymamy w **groszach** (``int``), więc nie ma problemu porównywania
  ``float``-ów,
* wszystkie reguły (walidacja, rabat, podatek) są **właściwościami lub metodami**
  obiektu, więc test nie musi nic wiedzieć o reprezentacji wewnętrznej.
"""

from __future__ import annotations

import re


class ShoppingCart:
    """Koszyk zakupowy. Ceny w groszach (int) - pieniądze nie lubią floatów."""

    def __init__(self, tax_rate: float = 0.0) -> None:
        if not 0.0 <= tax_rate <= 1.0:
            raise ValueError(f"tax_rate must be in 0..1, got {tax_rate}")
        self.tax_rate = tax_rate
        self._items: dict[str, tuple[int, int]] = {}   # sku -> (price_cents, quantity)
        self._discount_percent = 0.0

    # --- modyfikacja zawartości ---------------------------------------- #
    def add(self, sku: str, price_cents: int, quantity: int = 1) -> None:
        if not sku:
            raise ValueError("sku must not be empty")
        if price_cents < 0:
            raise ValueError(f"price_cents must be non-negative, got {price_cents}")
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")

        if sku in self._items:
            _, old_quantity = self._items[sku]
            self._items[sku] = (price_cents, old_quantity + quantity)
        else:
            self._items[sku] = (price_cents, quantity)

    def remove(self, sku: str) -> None:
        if sku not in self._items:
            raise KeyError(f"no item with sku {sku!r}")
        del self._items[sku]

    def clear(self) -> None:
        self._items.clear()

    def apply_discount(self, percent: float) -> None:
        if not 0.0 <= percent <= 100.0:
            raise ValueError(f"discount must be in 0..100, got {percent}")
        self._discount_percent = percent

    # --- właściwości wyliczane ----------------------------------------- #
    @property
    def discount_percent(self) -> float:
        return self._discount_percent

    @property
    def skus(self) -> list[str]:
        return list(self._items)

    @property
    def item_count(self) -> int:
        return sum(quantity for _, quantity in self._items.values())

    @property
    def subtotal_cents(self) -> int:
        """Suma pozycji po rabacie, przed podatkiem (zaokrąglona w dół)."""
        gross = sum(price * quantity for price, quantity in self._items.values())
        return gross * int(100 - self._discount_percent) // 100

    @property
    def tax_cents(self) -> int:
        """Podatek naliczony od kwoty PO rabacie."""
        return int(self.subtotal_cents * self.tax_rate)

    @property
    def total_cents(self) -> int:
        return self.subtotal_cents + self.tax_cents

    def __repr__(self) -> str:
        return (f"ShoppingCart(items={self._items!r}, "
                f"discount={self._discount_percent}, tax_rate={self.tax_rate})")


_PRICE_PATTERN = re.compile(
    r"^\s*(?P<amount>\d+(?:[.,]\d{1,2})?)\s*(?P<currency>zł|PLN|EUR|USD)?\s*$"
)


def parse_price(text: str) -> int:
    """Zamienia napis ceny na grosze: ``"12,99 zł"`` -> ``1299``.

    Akceptuje kropkę lub przecinek jako separator, opcjonalny sufiks waluty
    (``zł``, ``PLN``, ``EUR``, ``USD``) i białe znaki wokół liczby.
    """
    match = _PRICE_PATTERN.match(text or "")
    if match is None:
        raise ValueError(f"cannot parse price: {text!r}")
    amount = float(match.group("amount").replace(",", "."))
    return round(amount * 100)
