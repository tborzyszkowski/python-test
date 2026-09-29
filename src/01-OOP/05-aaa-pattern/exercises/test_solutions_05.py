"""Wzorcowe rozwiązanie tematu 05 - zestaw testów w strukturze AAA.

    python -m pytest src/01-OOP/05-aaa-pattern/exercises/test_solutions_05.py -v

Każdy test ma trzy sekcje oddzielone komentarzami:

    # Arrange  - przygotowanie danych i stanu (tworzymy WSZYSTKO, co potrzebne)
    # Act      - jedna operacja pod testem (jedno wywołanie!)
    # Assert   - weryfikacja wyniku

Zasady, które widać w każdym teście poniżej:

* **jedna własność na test** - jeśli test ma dwie niezależne asercje, to prawie
  zawsze powinny być dwa testy (inaczej nie wiesz, co padło),
* **Act to jedno wywołanie** - jeśli w jednym teście wołamy i ``add``, i
  ``remove``, i ``apply_discount``, test sprawdza zbyt wiele naraz,
* **brak stanu współdzielonego** - każdy test tworzy własny ``ShoppingCart``,
  więc kolejność wykonania nie ma znaczenia,
* **asercje na zachowanie, nie na implementację** - nigdy nie zaglądamy do
  ``cart._items``,
* ścieżki błędów sprawdzamy przez ``pytest.raises(Type, match="...")``.
"""

from __future__ import annotations

import pytest

from shopping_cart import ShoppingCart, parse_price

# --------------------------------------------------------------------------- #
# 1. Dodawanie pozycji
# --------------------------------------------------------------------------- #


def test_add_new_item_increases_subtotal():
    # Arrange
    cart = ShoppingCart()

    # Act
    cart.add("apple", price_cents=100, quantity=3)

    # Assert
    assert cart.subtotal_cents == 300


def test_add_two_different_items_sums_their_values():
    # Arrange
    cart = ShoppingCart()

    # Act
    cart.add("apple", 100, quantity=2)      # 200
    cart.add("banana", 250)                 # 250

    # Assert
    assert cart.subtotal_cents == 450
    assert cart.item_count == 3
    assert cart.skus == ["apple", "banana"]


def test_empty_cart_has_zero_totals():
    # Arrange + Act
    cart = ShoppingCart()

    # Assert
    assert cart.subtotal_cents == 0
    assert cart.item_count == 0
    assert cart.tax_cents == 0
    assert cart.total_cents == 0


# --------------------------------------------------------------------------- #
# 2. Scalanie tego samego SKU
# --------------------------------------------------------------------------- #


def test_adding_same_sku_merges_quantities():
    # Arrange
    cart = ShoppingCart()
    cart.add("apple", 100, quantity=2)

    # Act
    cart.add("apple", 100, quantity=3)

    # Assert
    assert len(cart.skus) == 1        # nadal jedna pozycja
    assert cart.item_count == 5       # ale pięć sztuk
    assert cart.subtotal_cents == 500


# --------------------------------------------------------------------------- #
# 3. Usuwanie i ścieżka błędu
# --------------------------------------------------------------------------- #


def test_remove_returns_cart_to_previous_state():
    # Arrange
    cart = ShoppingCart()
    cart.add("apple", 100)
    cart.add("banana", 200)

    # Act
    cart.remove("apple")

    # Assert
    assert cart.skus == ["banana"]
    assert cart.subtotal_cents == 200


def test_remove_unknown_sku_raises_and_keeps_state():
    # Arrange
    cart = ShoppingCart()
    cart.add("apple", 100)

    # Act + Assert (dwa w jednym, bo wyjątek przerywa normalny przepływ)
    with pytest.raises(KeyError, match="pear"):
        cart.remove("pear")

    # Assert - stan bez zmian
    assert cart.skus == ["apple"]
    assert cart.subtotal_cents == 100


# --------------------------------------------------------------------------- #
# 4. Rabaty
# --------------------------------------------------------------------------- #


def test_ten_percent_discount_reduces_subtotal():
    # Arrange
    cart = ShoppingCart()
    cart.add("laptop", 100_000)        # 1000,00 zł

    # Act
    cart.apply_discount(10)

    # Assert
    assert cart.subtotal_cents == 90_000


def test_zero_and_full_discount_are_allowed():
    # Arrange
    cart = ShoppingCart()
    cart.add("laptop", 100_000)

    # Act
    cart.apply_discount(0)
    subtotal_without_discount = cart.subtotal_cents
    cart.apply_discount(100)

    # Assert
    assert subtotal_without_discount == 100_000
    assert cart.subtotal_cents == 0


@pytest.mark.parametrize("bad_discount", [-1, 100.5, 1000])
def test_invalid_discount_is_rejected_and_previous_value_is_kept(bad_discount):
    # Arrange
    cart = ShoppingCart()
    cart.add("laptop", 100_000)
    cart.apply_discount(10)

    # Act + Assert
    with pytest.raises(ValueError, match="discount"):
        cart.apply_discount(bad_discount)

    # Assert - poprzedni rabat nietknięty
    assert cart.discount_percent == 10
    assert cart.subtotal_cents == 90_000


# --------------------------------------------------------------------------- #
# 5. Podatek
# --------------------------------------------------------------------------- #


def test_tax_is_calculated_after_discount():
    """Pułapka: podatek od ceny katalogowej dałby 2300, a ma być 2070."""
    # Arrange
    cart = ShoppingCart(tax_rate=0.23)
    cart.add("laptop", 100_000)        # 1000,00 zł netto

    # Act
    cart.apply_discount(10)            # 900,00 zł netto
    tax = cart.tax_cents

    # Assert
    assert tax == 20_700               # 23% z 900,00 zł
    assert cart.total_cents == 110_700


def test_confirmation_of_the_trap_without_discount():
    """Ten sam koszyk bez rabatu - dla porównania (podatek 23 000)."""
    # Arrange
    cart = ShoppingCart(tax_rate=0.23)
    cart.add("laptop", 100_000)

    # Act + Assert
    assert cart.tax_cents == 23_000


# --------------------------------------------------------------------------- #
# 6. Walidacja wejścia w `add`
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("quantity", [0, -1])
def test_add_rejects_non_positive_quantity(quantity):
    # Arrange
    cart = ShoppingCart()

    # Act + Assert
    with pytest.raises(ValueError, match="quantity"):
        cart.add("apple", 100, quantity=quantity)

    # Assert - nieudany `add` nie tworzy pozycji
    assert cart.skus == []


def test_add_rejects_negative_price():
    # Arrange
    cart = ShoppingCart()

    # Act + Assert
    with pytest.raises(ValueError, match="price_cents"):
        cart.add("apple", -1)

    # Assert
    assert cart.skus == []


# --------------------------------------------------------------------------- #
# 7. `parse_price` - test jednostkowy czystej funkcji
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("text", "expected_cents"),
    [
        ("12,99 zł", 1299),
        ("12.99", 1299),
        (" 5 PLN ", 500),
        ("0", 0),
        ("1000 EUR", 100_000),
    ],
)
def test_parse_price_accepts_supported_formats(text, expected_cents):
    # Arrange + Act
    result = parse_price(text)

    # Assert
    assert result == expected_cents


@pytest.mark.parametrize("text", ["abc", "", "12,999", "-5", None])
def test_parse_price_rejects_garbage(text):
    # Arrange + Act + Assert
    with pytest.raises(ValueError, match="cannot parse price"):
        parse_price(text)
