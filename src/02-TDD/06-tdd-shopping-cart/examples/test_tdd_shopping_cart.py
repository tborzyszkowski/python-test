from __future__ import annotations

import pytest
from tdd_shopping_cart import Product, ShoppingCart


@pytest.fixture
def book() -> Product:
    return Product("book", "ksiazka", "books", 5000)


def test_empty_cart_has_zero_total():
    assert ShoppingCart().total_cents() == 0


def test_adding_product_increases_total(book):
    cart = ShoppingCart()
    cart.add(book, quantity=2)

    assert cart.total_cents() == 10_000
    assert len(cart) == 2


def test_same_product_merges_quantity(book):
    cart = ShoppingCart()
    cart.add(book)
    cart.add(book, quantity=2)

    assert len(cart) == 3
    assert cart.subtotal_cents() == 15_000


def test_threshold_discount_applies_after_reaching_minimum(book):
    cart = ShoppingCart()
    cart.add(book, quantity=2)
    cart.apply_threshold_discount(minimum_cents=10_000, percent=10)

    assert cart.total_cents() == 9_000


def test_threshold_discount_does_not_apply_below_minimum(book):
    cart = ShoppingCart()
    cart.add(book)
    cart.apply_threshold_discount(minimum_cents=10_000, percent=10)

    assert cart.total_cents() == 5_000


def test_three_for_two_makes_cheapest_item_free(book):
    cart = ShoppingCart()
    cart.add(book, quantity=3)
    cart.enable_three_for_two("books")

    assert cart.promotion_discount_cents() == 5_000
    assert cart.total_cents() == 10_000


def test_remove_product_updates_total(book):
    cart = ShoppingCart()
    cart.add(book)
    cart.remove("book")

    assert cart.total_cents() == 0


def test_invalid_quantity_is_rejected(book):
    with pytest.raises(ValueError, match="positive"):
        ShoppingCart().add(book, quantity=0)


def test_invalid_price_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        Product("bad", "bad", "x", -1)
