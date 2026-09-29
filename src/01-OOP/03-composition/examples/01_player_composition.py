"""Przykład 01 - kompozycja: klasy zawierające instancje innych klas.

Uruchomienie::

    python src/01-OOP/03-composition/examples/01_player_composition.py

Trzy rzeczy, które pokazuje ten plik:

1. **Kompozycja (``has-a``)** - ``Player`` *ma* ``Wallet`` i ``Backpack``.
   Nie dziedziczy po nich: gracz nie *jest* portfelem.
2. **Delegacja** - ``Player.total_weight()`` nie liczy wagi samodzielnie,
   tylko przekazuje pytanie do plecaka. To minimalizuje duplikację logiki.
3. **Wstrzykiwanie zależności (dependency injection)** - ``Player`` może
   przyjąć gotowy portfel/plecak. Domyślne obiekty powstają w środku
   (wygoda), ale w testach podajemy własne (kontrola stanu!).

To trzeci punkt jest kluczowy dla testowania: obiekt, który sam tworzy sobie
współpracowników, jest **nietestowalny w izolacji**. Obiekt, który je przyjmuje,
testuje się bez żadnej infrastruktury.
"""

from __future__ import annotations

from collections.abc import Iterator


class Wallet:
    """Portfel z monetami - prosta klasa używana jako element kompozycji."""

    def __init__(self, gold: int = 0) -> None:
        if gold < 0:
            raise ValueError(f"gold must be non-negative, got {gold}")
        self._gold = gold

    @property
    def gold(self) -> int:
        return self._gold

    def deposit(self, amount: int) -> int:
        if amount < 0:
            raise ValueError(f"amount must be non-negative, got {amount}")
        self._gold += amount
        return self._gold

    def withdraw(self, amount: int) -> int:
        if amount < 0:
            raise ValueError(f"amount must be non-negative, got {amount}")
        if amount > self._gold:
            raise ValueError(f"not enough gold: have {self._gold}, need {amount}")
        self._gold -= amount
        return self._gold

    def __repr__(self) -> str:
        return f"Wallet(gold={self._gold})"


class Item:
    """Przedmiot o nazwie i wadze (kolejny element kompozycji)."""

    def __init__(self, name: str, weight_kg: float) -> None:
        if not name:
            raise ValueError("item name must not be empty")
        if weight_kg < 0:
            raise ValueError(f"weight must be non-negative, got {weight_kg}")
        self.name = name
        self.weight_kg = weight_kg

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, weight_kg={self.weight_kg!r})"


class Backpack:
    """Kolekcja przedmiotów z limitem udźwigu."""

    def __init__(self, capacity_kg: float = 20.0) -> None:
        if capacity_kg <= 0:
            raise ValueError(f"capacity must be positive, got {capacity_kg}")
        self.capacity_kg = capacity_kg
        self._items: list[Item] = []

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Item]:
        return iter(self._items)

    @property
    def total_weight(self) -> float:
        return sum(item.weight_kg for item in self._items)

    @property
    def is_overloaded(self) -> bool:
        return self.total_weight > self.capacity_kg

    def add(self, item: Item) -> None:
        if self.total_weight + item.weight_kg > self.capacity_kg:
            raise ValueError(f"backpack would be overloaded by {item.name!r}")
        self._items.append(item)

    def remove(self, name: str) -> Item:
        for index, item in enumerate(self._items):
            if item.name == name:
                return self._items.pop(index)
        raise KeyError(f"no item named {name!r} in backpack")

    def __repr__(self) -> str:
        return f"Backpack(capacity_kg={self.capacity_kg!r}, items={self._items!r})"


class Player:
    """Gracz złożony z portfela i plecaka (kompozycja + wstrzykiwanie zależności)."""

    def __init__(
        self,
        name: str,
        wallet: Wallet | None = None,
        backpack: Backpack | None = None,
    ) -> None:
        self.name = name
        # Domyślne wartości tworzymy w środku (wygodne API)...
        # ...ale przyjęcie argumentu pozwala wstrzyknąć własny obiekt w testach.
        self.wallet = wallet if wallet is not None else Wallet()
        self.backpack = backpack if backpack is not None else Backpack()

    # ------------------------------------------------------------------ #
    # Delegacja: Player NIE liczy wagi ani nie zarządza monetami sam.      #
    # ------------------------------------------------------------------ #
    @property
    def gold(self) -> int:
        return self.wallet.gold

    @property
    def total_weight(self) -> float:
        return self.backpack.total_weight

    def pick_up(self, item: Item) -> None:
        self.backpack.add(item)

    def buy(self, item: Item, price: int) -> None:
        """Kupuje przedmiot: pobiera monety i wkłada go do plecaka."""
        self.wallet.withdraw(price)  # może podnieść ValueError - i tak ma być
        try:
            self.backpack.add(item)
        except ValueError:
            self.wallet.deposit(price)  # wycofanie transakcji (rollback)
            raise

    def __repr__(self) -> str:
        return f"Player(name={self.name!r}, gold={self.gold}, backpack={self.backpack!r})"


def demo_composition_basics() -> None:
    print("== 1. Kompozycja i delegacja ==")
    player = Player("Aragorn", wallet=Wallet(gold=100))
    player.pick_up(Item("sword", 3.5))
    player.pick_up(Item("shield", 5.0))
    print(f"player               -> {player}")
    print(f"player.total_weight  -> {player.total_weight}   # delegacja do plecaka")
    print()


def demo_injection_for_tests() -> None:
    print("== 2. Wstrzykiwanie zależności w praktyce ==")
    # W teście chcę ustalić stan początkowy dokładnie - wstrzykuję gotowe obiekty.
    wallet = Wallet(gold=10)
    backpack = Backpack(capacity_kg=1.0)
    player = Player("Biedak", wallet=wallet, backpack=backpack)

    try:
        player.buy(Item("zbroja", 8.0), price=5)
    except ValueError as exc:
        print(f"buy(zbroja, 5)       -> ValueError: {exc}")
    print(f"po nieudanym zakupie -> gold={player.gold}, "
          f"items={len(player.backpack)}   # transakcja wycofana")


def demo_backpack_rules() -> None:
    print("== 3. Reguły egzekwowane przez współpracownika ==")
    backpack = Backpack(capacity_kg=5.0)
    backpack.add(Item("sword", 3.0))
    try:
        backpack.add(Item("zbroja", 3.0))
    except ValueError as exc:
        print(f"add(zbroja)          -> ValueError: {exc}")
    removed = backpack.remove("sword")
    print(f"remove('sword')      -> {removed}")
    try:
        backpack.remove("sword")
    except KeyError as exc:
        print(f"remove('sword') ponownie -> KeyError: {exc}")
    print()


def main() -> None:
    demo_composition_basics()
    demo_injection_for_tests()
    demo_backpack_rules()


if __name__ == "__main__":
    main()
