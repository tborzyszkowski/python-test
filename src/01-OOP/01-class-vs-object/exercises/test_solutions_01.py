"""Testy sprawdzające rozwiązania zadań - temat 01.

Uruchomienie::

    python -m pytest src/01-OOP/01-class-vs-object/exercises/test_solutions_01.py -v

Testy pokazują dwie ważne techniki, które wrócą w kolejnych tematach:

* ``@pytest.mark.parametrize`` - jeden test, wiele danych wejściowych,
* ``autouse=True`` fixture - automatyczne przygotowanie i posprzątanie
  **stanu współdzielonego** (licznik ``Ammo.total_created``), dzięki czemu
  testy są od siebie niezależne.
"""

from __future__ import annotations

import pytest

from solutions_01 import Ammo, AmmoV1, BuggyInventory, Inventory, only_valid

# --------------------------------------------------------------------------- #
# Fixture'y - izolacja stanu
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def reset_ammo_counter():
    """Zeruje licznik klasowy przed i po każdym teście.

    Bez tego testy sprawdzające ``created_count()`` zależałyby od kolejności
    wykonania - klasyczny „flaky test”. Zwróć uwagę, że stan współdzielony
    (klasa) wymaga jawnego resetu, a stan instancyjny nie.
    """
    Ammo.reset_counter()
    yield
    Ammo.reset_counter()


@pytest.fixture(autouse=True)
def clean_buggy_inventory():
    """Czyści listę współdzieloną przez ``BuggyInventory`` (aby nie „przeciekała”)."""
    BuggyInventory.items.clear()
    yield
    BuggyInventory.items.clear()


# --------------------------------------------------------------------------- #
# Zadanie 1
# --------------------------------------------------------------------------- #


def test_ammo_stores_instance_state():
    # Arrange + Act
    ammo = AmmoV1("9mm", 10)
    # Assert
    assert ammo.caliber == "9mm"
    assert ammo.rounds == 10


def test_spend_returns_remaining_rounds():
    ammo = AmmoV1("9mm", 10)
    assert ammo.spend(4) == 6
    assert ammo.rounds == 6


def test_spend_raises_for_negative_amount():
    ammo = AmmoV1("9mm", 10)
    with pytest.raises(ValueError, match="negative"):
        ammo.spend(-1)


def test_spend_raises_when_not_enough_rounds():
    ammo = AmmoV1("9mm", 3)
    with pytest.raises(ValueError, match="not enough"):
        ammo.spend(4)
    # stan obiektu nie może się zmienić po nieudanej operacji
    assert ammo.rounds == 3


def test_negative_rounds_in_constructor_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        AmmoV1("9mm", -1)


def test_repr_is_informative():
    assert repr(AmmoV1("9mm", 10)) == "AmmoV1(caliber='9mm', rounds=10)"


def test_equality_is_logical_not_identity():
    assert AmmoV1("9mm", 10) == AmmoV1("9mm", 10)
    assert AmmoV1("9mm", 10) != AmmoV1("9mm", 9)


def test_equality_with_foreign_type_returns_not_implemented():
    # Python zamienia NotImplemented na False w operatorze ==,
    # ale sam operator porównania musi zwrócić NotImplemented.
    assert AmmoV1("9mm", 10).__eq__("9mm") is NotImplemented
    assert (AmmoV1("9mm", 10) == "9mm") is False


# --------------------------------------------------------------------------- #
# Zadanie 2
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("caliber", "expected"),
    [
        ("9mm", True),
        ("5.56mm", True),
        (".45cal", True),
        ("12", True),
        ("0.22", True),
        ("mm9", False),
        ("bum", False),
        ("", False),
        ("9 mm", False),
        ("9MM", False),
    ],
)
def test_is_valid_caliber(caliber, expected):
    assert Ammo.is_valid_caliber(caliber) is expected


def test_counter_counts_created_instances():
    assert Ammo.created_count() == 0
    Ammo("9mm", 10)
    Ammo("5.56mm", 30)
    assert Ammo.created_count() == 2


def test_counter_is_shared_with_subclasses():
    class SteelAmmo(Ammo):
        """Podklasa celowo nie nadpisuje licznika."""

    SteelAmmo("9mm", 5)
    # ``cls`` w metodzie klasowej oznacza klasę, na której wywołano metodę,
    # więc licznik klasy bazowej widzi także obiekty podklasy.
    assert Ammo.created_count() == 1


def test_invalid_caliber_rejected_in_constructor():
    with pytest.raises(ValueError, match="invalid caliber"):
        Ammo("bum!", 10)


def test_box_of_creates_full_magazines():
    boxes = Ammo.box_of("9mm", boxes=3)
    assert len(boxes) == 3
    assert {b.rounds for b in boxes} == {30}
    assert Ammo.created_count() == 3


# --------------------------------------------------------------------------- #
# Zadanie 3
# --------------------------------------------------------------------------- #


def test_inventory_instances_are_independent():
    a, b = Inventory(), Inventory()
    a.add("sword")
    assert a.items == ["sword"]
    assert b.items == []


def test_inventory_clear():
    inv = Inventory()
    inv.add("sword")
    inv.add("shield")
    inv.clear()
    assert inv.items == []
    assert len(inv) == 0


def test_buggy_inventory_demonstrates_shared_state():
    """Test dokumentujący *dlaczego* mutowalny atrybut klasowy jest pułapką."""
    a, b = BuggyInventory(), BuggyInventory()
    a.add("sword")
    assert b.items == ["sword"]  # nie zamierzone, ale prawdziwe


# --------------------------------------------------------------------------- #
# Zadanie 4
# --------------------------------------------------------------------------- #


def test_only_valid_filters_and_deduplicates():
    assert only_valid("9mm", "bum!", "9mm", "5.56") == ("9mm", "5.56")


def test_only_valid_on_empty_input():
    assert only_valid() == ()
