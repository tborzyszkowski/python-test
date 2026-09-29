"""Testy sprawdzające rozwiązania zadań - temat 02.

    python -m pytest src/01-OOP/02-encapsulation-property/exercises/test_solutions_02.py -v

Testy pokazują trzy wzorce, które wykorzystasz w każdym kolejnym zadaniu:

1. **Test niezmiennika** - „obiekt zawsze spełnia warunek X” (np. ``0 <= hp <= MAX``).
2. **Test ścieżki błędu** - ``pytest.raises`` z ``match=`` (regex na komunikat),
   żeby sprawdzić *typ* i *powód* błędu, a nie tylko to, że „coś poleciało”.
3. **Test właściwości wyliczanej** - po zmianie stanu wynik musi być liczony od nowa.
"""

from __future__ import annotations

import pytest

from solutions_02 import (
    FrozenPoint,
    FrozenPointDataclass,
    Player,
    Rectangle,
    Temperature,
)

# --------------------------------------------------------------------------- #
# Fixture'y
# --------------------------------------------------------------------------- #


@pytest.fixture
def room_temperature() -> Temperature:
    """Przykładowa temperatura pokojowa (25 stopni C)."""
    return Temperature(25)


# --------------------------------------------------------------------------- #
# Zadanie 1 - Temperature
# --------------------------------------------------------------------------- #


def test_celsius_is_stored_as_float(room_temperature, tolerance):
    assert room_temperature.celsius == pytest.approx(25.0, abs=tolerance)
    assert isinstance(room_temperature.celsius, float)


def test_derived_units_are_computed_correctly(room_temperature):
    assert room_temperature.kelvin == pytest.approx(298.15)
    assert room_temperature.fahrenheit == pytest.approx(77.0)


def test_derived_units_follow_mutation(room_temperature):
    room_temperature.celsius = 0
    assert room_temperature.kelvin == pytest.approx(273.15)
    assert room_temperature.fahrenheit == pytest.approx(32.0)


def test_absolute_zero_boundary_is_accepted():
    # wartość brzegowa: 0 K jest poprawne, więc nie może podnosić błędu
    assert Temperature(-273.15).kelvin == pytest.approx(0.0)


def test_below_absolute_zero_is_rejected():
    with pytest.raises(ValueError, match="absolute zero"):
        Temperature(-273.16)
    with pytest.raises(ValueError, match="absolute zero"):
        Temperature(25).celsius = -300


@pytest.mark.parametrize("bad_value", ["25", None, True, [25]])
def test_non_numeric_celsius_is_rejected(bad_value):
    with pytest.raises(TypeError, match="number"):
        Temperature(bad_value)


def test_equality_uses_tolerance():
    assert Temperature(25) == Temperature(25.0000000001)
    assert Temperature(25) != Temperature(26)
    assert Temperature(25).__eq__("25") is NotImplemented


# --------------------------------------------------------------------------- #
# Zadanie 2 - Rectangle
# --------------------------------------------------------------------------- #


def test_rectangle_derived_properties():
    rect = Rectangle(3, 4)
    assert rect.area == pytest.approx(12.0)
    assert rect.perimeter == pytest.approx(14.0)
    assert rect.is_square is False


def test_rectangle_is_square_when_sides_equal():
    assert Rectangle(5, 5).is_square is True
    assert Rectangle(5, 5.0000000001).is_square is True


@pytest.mark.parametrize("bad_value", [0, -1, -0.5])
def test_non_positive_dimension_is_rejected(bad_value):
    with pytest.raises(ValueError, match="positive"):
        Rectangle(bad_value, 1)
    with pytest.raises(ValueError, match="positive"):
        Rectangle(1, bad_value)


@pytest.mark.parametrize("bad_value", ["3", None, True])
def test_non_numeric_dimension_is_rejected(bad_value):
    with pytest.raises(TypeError, match="number"):
        Rectangle(bad_value, 1)


def test_derived_properties_track_mutation():
    rect = Rectangle(2, 3)
    assert rect.area == pytest.approx(6.0)
    rect.width = 4
    assert rect.area == pytest.approx(12.0)
    assert rect.perimeter == pytest.approx(14.0)


def test_area_is_read_only():
    with pytest.raises(AttributeError):
        Rectangle(2, 3).area = 100


def test_scale_returns_new_object_and_keeps_original():
    rect = Rectangle(3, 4)
    scaled = rect.scale(2)
    assert scaled == Rectangle(6, 8)
    assert rect == Rectangle(3, 4)
    assert scaled is not rect


@pytest.mark.parametrize("bad_factor", [0, -2])
def test_scale_rejects_non_positive_factor(bad_factor):
    with pytest.raises(ValueError, match="positive"):
        Rectangle(3, 4).scale(bad_factor)


def test_rectangles_with_different_side_order_are_not_equal():
    assert Rectangle(2, 3) != Rectangle(3, 2)


# --------------------------------------------------------------------------- #
# Zadanie 3 - Player
# --------------------------------------------------------------------------- #


def test_player_starts_alive():
    player = Player("Aragorn")
    assert player.hp == Player.MAX_HP
    assert player.is_alive is True


def test_damage_is_clamped_at_zero():
    player = Player("Aragorn")
    assert player.take_damage(1000) == 0
    assert player.hp == 0
    assert player.is_alive is False


def test_heal_is_clamped_at_max():
    player = Player("Aragorn", hp=10)
    assert player.heal(1000) == Player.MAX_HP


@pytest.mark.parametrize("hp", [-1, 101, 1000])
def test_hp_setter_rejects_values_out_of_range(hp):
    with pytest.raises(ValueError, match="hp out of range"):
        Player("Aragorn", hp=hp)


@pytest.mark.parametrize("amount", [-1, -100])
def test_negative_amount_is_rejected(amount):
    player = Player("Aragorn")
    with pytest.raises(ValueError, match="non-negative"):
        player.take_damage(amount)
    with pytest.raises(ValueError, match="non-negative"):
        player.heal(amount)


@pytest.mark.parametrize("hp", [0, 1, 50, 100])
def test_invariant_always_holds(hp):
    """Test niezmiennika: dla dowolnej poprawnej wartości HP warunek jest prawdziwy."""
    player = Player("Aragorn", hp=hp)
    assert 0 <= player.hp <= Player.MAX_HP


def test_hp_must_be_int():
    with pytest.raises(TypeError, match="int"):
        Player("Aragorn").hp = 50.5


# --------------------------------------------------------------------------- #
# Zadanie 4 - FrozenPoint
# --------------------------------------------------------------------------- #


def test_frozen_point_is_immutable():
    point = FrozenPoint(1, 2)
    with pytest.raises(AttributeError):
        point.x = 10
    with pytest.raises(AttributeError):
        point.y = 10


def test_frozen_point_has_no_dict():
    # __slots__ => brak __dict__, więc nie da się dodać dowolnego atrybutu
    assert not hasattr(FrozenPoint(1, 2), "__dict__")
    with pytest.raises(AttributeError):
        FrozenPoint(1, 2).color = "red"


def test_shift_returns_new_point():
    point = FrozenPoint(1, 2)
    shifted = point.shift(1, 1)
    assert shifted == FrozenPoint(2, 3)
    assert point == FrozenPoint(1, 2)


def test_frozen_point_can_be_used_in_set_and_dict():
    points = {FrozenPoint(1, 2), FrozenPoint(1, 2), FrozenPoint(3, 4)}
    assert len(points) == 2
    lookup = {FrozenPoint(3, 4): "cel"}
    assert lookup[FrozenPoint(3, 4)] == "cel"


def test_frozen_point_equality_with_foreign_type():
    assert FrozenPoint(1, 2).__eq__((1, 2)) is NotImplemented
    assert FrozenPoint(1, 2) != (1, 2)


def test_dataclass_variant_matches_handwritten_behaviour():
    a = FrozenPointDataclass(1, 2)
    b = FrozenPointDataclass(1, 2)
    assert a == b
    with pytest.raises(AttributeError):
        a.x = 5


def test_is_square_of_scaled_square_stays_true():
    square = Rectangle(2, 2).scale(3)
    assert square.is_square is True
    assert square.area == pytest.approx(36.0)
