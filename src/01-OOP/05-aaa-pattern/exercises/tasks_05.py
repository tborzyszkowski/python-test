"""Zadania do samodzielnego wykonania - temat 05 (struktura AAA).

W tym temacie jest **odwrotnie niż w poprzednich**: kod produkcyjny dostajesz
gotowy (``shopping_cart.py``), a Twoim zadaniem jest napisać **testy**.
Dlatego **rozwiązaniem jest tutaj plik z testami** - znajdziesz je w
``test_solutions_05.py``. Uruchomienie::

    python -m pytest src/01-OOP/05-aaa-pattern/exercises/test_solutions_05.py -v

Twoje testy napisz w nowym pliku, np. ``exercises/test_moje_05.py``.
"""

from __future__ import annotations

from shopping_cart import ShoppingCart, parse_price  # noqa: F401  (potrzebne w Twoich testach)

# --------------------------------------------------------------------------- #
# CASES DO NAPISANIA
# --------------------------------------------------------------------------- #
# Każdy test napisz w strukturze AAA z komentarzami ``# Arrange``, ``# Act``,
# ``# Assert``. Nazwa testu ma opisywać **zachowanie**, nie nazwę metody.
#
#  1. Dodanie nowej pozycji zwiększa ``subtotal_cents`` o ``cena * ilość``.
#  2. Dodanie tego samego ``sku`` scala ilości: ``len(cart.skus)`` się nie
#     zmienia, a ``item_count`` rośnie.
#  3. ``remove`` nieznanego ``sku`` podnosi ``KeyError`` (komunikat zawiera
#     ``sku``), a stan koszyka **nie zmienia się**.
#  4. Rabat 10% obniża ``subtotal_cents`` proporcjonalnie (wybierz dane, dla
#     których wynik jest całkowity - ułamki groszy to inny test).
#  5. Rabat spoza zakresu 0..100 podnosi ``ValueError`` i **nie zmienia**
#     aktualnie ustawionego rabatu.
#  6. ``parse_price``: ``"12,99 zł"`` -> 1299, ``"12.99"`` -> 1299,
#     ``" 5 PLN "`` -> 500, ``"abc"`` -> ``ValueError`` (użyj ``parametrize``).
#  7. Podatek naliczany jest od kwoty **po rabacie**, nie od ceny katalogowej.
#  8. ``add`` z ``quantity <= 0`` oraz z ``price_cents < 0`` podnosi
#     ``ValueError`` (i nie tworzy pozycji).
#
# Kryteria jakości testu (będą oceniane):
#  * jedna własność na jeden test - jedna „przyczyna porażki”,
#  * brak zależności między testami (każdy test tworzy własny koszyk),
#  * asercje dotyczą **zachowania**, nie reprezentacji wewnętrznej
#    (``cart._items`` to szczegół implementacyjny),
#  * ``pytest.raises(ValueError, match="...")`` - sprawdź typ i komunikat.

# --------------------------------------------------------------------------- #
# PRZYKŁADY TESTÓW NAPISANYCH ŹLE (przerób je na AAA)
# --------------------------------------------------------------------------- #

# ❌ Stan współdzielony przez wszystkie przypadki - kolejność wykonania zmienia wynik.
_SHARED_CART = ShoppingCart()


def naive_add_and_remove():
    """❌ Brak Arrange/Act/Assert; sprawdza trzy rzeczy naraz; używa stanu globalnego."""
    _SHARED_CART.add("apple", 100)
    _SHARED_CART.add("banana", 200)
    _SHARED_CART.remove("apple")
    assert _SHARED_CART.subtotal_cents == 200
    assert _SHARED_CART.item_count == 1
    assert _SHARED_CART.skus == ["banana"]


def naive_discount():
    """❌ Asercje bez wartości diagnostycznej (``< 1000``, ``is not None``)."""
    cart = ShoppingCart()
    cart.add("apple", 1000)
    cart.apply_discount(10)
    assert cart.subtotal_cents < 1000              # ❌ nie mówi ILE ma być
    assert cart.apply_discount is not None         # ❌ zawsze prawdziwe
    assert cart.total_cents == cart.subtotal_cents + cart.tax_cents   # ❌ powtarza implementację


def naive_exception():
    """❌ Sprawdza tylko, że 'coś poleciało' - nie typ, nie komunikat."""
    try:
        parse_price("abc")
    except Exception:                              # ❌ łapie wszystko
        pass
    else:
        raise AssertionError("spodziewano się błędu")


def naive_implementation_coupling():
    """❌ Test zależy od reprezentacji wewnętrznej - refaktoring go zepsuje."""
    cart = ShoppingCart()
    cart.add("apple", 100, quantity=2)
    assert cart._items == {"apple": (100, 2)}      # ❌ prywatne pole!
