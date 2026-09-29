"""Testy sprawdzające rozwiązania zadań - temat 04.

    python -m pytest src/01-OOP/04-inheritance-polymorphism/exercises/test_solutions_04.py -v

Najważniejszy wzorzec tego pliku to **test kontraktu uruchamiany na całej
liście narzędzi** (``ALL_TOOLS``). Taki test:

* jest jeden, a chroni wszystkie podklasy (teraz i w przyszłości),
* natychmiast wykrywa naruszenie zasady podstawienia Liskov,
* jest naturalnym miejscem, gdzie polimorfizm „płaci za siebie” w testach.
"""

from __future__ import annotations

import pytest

from solutions_04 import (
    FancySaw,
    Hammer,
    MultiTool,
    Tool,
    ToolBrokenError,
    ToolError,
    ToolKit,
    use_anything,
)

# --------------------------------------------------------------------------- #
# Fabryki narzędzi - jedno miejsce, w którym dodajemy nowe przypadki
# --------------------------------------------------------------------------- #

TOOL_FACTORIES = [
    pytest.param(lambda: Hammer("młotek", weight_kg=1.0), id="hammer"),
    pytest.param(lambda: FancySaw("piła"), id="fancy-saw"),
]


# --------------------------------------------------------------------------- #
# Kontrakt klasy abstrakcyjnej
# --------------------------------------------------------------------------- #


def test_tool_is_abstract():
    with pytest.raises(TypeError):
        Tool("narzędzie")  # type: ignore[abstract]


def test_tool_subclass_without_effect_on_is_abstract():
    class HalfDone(Tool):
        pass

    with pytest.raises(TypeError):
        HalfDone("półprodukt")  # type: ignore[abstract]


# --------------------------------------------------------------------------- #
# Zadanie 1 - Hammer
# --------------------------------------------------------------------------- #


def test_hammer_effect_and_wear():
    hammer = Hammer("młotek", weight_kg=1.5, durability=30)
    assert hammer.use("gwóźdź") == "Uderzam w gwóźdź młotkiem 1.5 kg"
    assert hammer.durability == 27        # wear_per_use = 3
    assert hammer.uses == 1


def test_hammer_accepts_integer_weight():
    # format :g sprawia, że 2.0 drukuje się jako "2"
    assert Hammer("m", 2, durability=10).use("x") == "Uderzam w x młotkiem 2 kg"


@pytest.mark.parametrize("weight", [0, -1.5])
def test_hammer_rejects_non_positive_weight(weight):
    with pytest.raises(ValueError, match="weight_kg"):
        Hammer("młotek", weight)


def test_hammer_nail_uses_tool_count_times():
    hammer = Hammer("młotek", 1.0, durability=100)
    results = hammer.nail("gwóźdź", 3)
    assert len(results) == 3
    assert hammer.uses == 3
    assert hammer.durability == 100 - 9


@pytest.mark.parametrize("count", [0, -2])
def test_hammer_nail_rejects_non_positive_count(count):
    with pytest.raises(ValueError, match="count"):
        Hammer("młotek", 1.0).nail("gwóźdź", count)


def test_broken_tool_raises_domain_error():
    hammer = Hammer("młotek", 1.0, durability=3)
    hammer.use("gwóźdź")                      # durability 3 -> 0
    assert hammer.is_broken is True
    with pytest.raises(ToolBrokenError, match="broken"):
        hammer.use("gwóźdź")


def test_repair_restores_durability_with_cap():
    hammer = Hammer("młotek", 1.0, durability=10)
    assert hammer.repair(5) == 15
    assert hammer.repair(1000) == 100
    assert hammer.repair() == 100


def test_empty_target_is_rejected():
    with pytest.raises(ValueError, match="target"):
        Hammer("młotek", 1.0).use("")


# --------------------------------------------------------------------------- #
# Testy kontraktu - uruchamiane na każdym narzędziu
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("factory", TOOL_FACTORIES)
def test_tool_contract_effect_is_non_empty_string(factory):
    """Każde narzędzie musi zwrócić niepusty ``str`` (kontrakt ``effect_on``)."""
    tool = factory()
    effect = tool.use("deska")
    assert isinstance(effect, str)
    assert effect.strip() != ""


@pytest.mark.parametrize("factory", TOOL_FACTORIES)
def test_tool_contract_use_decreases_durability(factory):
    tool = factory()
    before = tool.durability
    tool.use("deska")
    assert tool.durability < before
    assert tool.durability >= 0


@pytest.mark.parametrize("factory", TOOL_FACTORIES)
def test_tool_contract_broken_tools_raise_tool_error(factory):
    """Zepsute narzędzie zgłasza ``ToolError`` - klient może łapać jedną rodzinę."""
    tool = factory()
    while not tool.is_broken:
        tool.use("deska")
    with pytest.raises(ToolError):
        tool.use("deska")


# --------------------------------------------------------------------------- #
# Zadanie 2 - ToolKit
# --------------------------------------------------------------------------- #


@pytest.fixture
def kit() -> ToolKit:
    return ToolKit([Hammer("młotek", 1.0, durability=60), FancySaw("piła", durability=80)])


def test_empty_kit_has_zero_aggregates():
    empty = ToolKit()
    assert len(empty) == 0
    assert empty.total_uses == 0
    assert empty.total_durability == 0
    assert empty.broken_tools == []
    assert empty.most_durable() is None


def test_kit_rejects_foreign_objects(kit):
    with pytest.raises(TypeError, match="Tool"):
        kit.add("nie narzędzie")  # type: ignore[arg-type]


def test_kit_use_all_is_polymorphic(kit):
    effects = kit.use_all("deska")
    assert set(effects) == {"młotek", "piła"}
    assert effects["młotek"] == "Uderzam w deska młotkiem 1 kg"
    assert effects["piła"] == "Piłuję deska"
    assert kit.total_uses == 2


def test_kit_skips_broken_tools():
    broken = Hammer("zepsuty", 1.0, durability=1)
    working = FancySaw("piła")
    kit = ToolKit([broken, working])
    broken.use("x")                                   # dobijamy młotek

    effects = kit.use_all("deska")

    assert set(effects) == {"piła"}
    assert kit.broken_tools == ["zepsuty"]


def test_kit_raises_when_nothing_works():
    broken = Hammer("zepsuty", 1.0, durability=1)
    broken.use("x")
    with pytest.raises(ToolError, match="no working tools"):
        ToolKit([broken]).use_all("deska")


def test_kit_is_iterable(kit):
    assert [tool.name for tool in kit] == ["młotek", "piła"]


def test_most_durable_returns_the_toughest_tool(kit):
    assert kit.most_durable() is kit._tools[1]  # type: ignore[attr-defined]


def test_adding_new_tool_type_requires_no_kit_change():
    """Klient nie zna typów - nowa podklasa działa bez zmian w ``ToolKit``."""

    class Crowbar(Tool):
        wear_per_use = 1

        def effect_on(self, target: str) -> str:
            return f"Podważam {target}"

    kit = ToolKit([Crowbar("łom"), Hammer("młotek", 1.0)])
    assert kit.use_all("skrzynia") == {
        "łom": "Podważam skrzynia",
        "młotek": "Uderzam w skrzynia młotkiem 1 kg",
    }


# --------------------------------------------------------------------------- #
# Zadanie 3 - FancySaw (LSP)
# --------------------------------------------------------------------------- #


def test_fancy_saw_handles_short_targets():
    assert FancySaw().effect_on("a") == "Piłuję a"


def test_fancy_saw_reports_unsupported_material_as_tool_error():
    with pytest.raises(ToolError, match="unsupported material"):
        FancySaw().use("metal")


def test_fancy_saw_does_not_return_none():
    effect = FancySaw().effect_on("dowolny krótki")
    assert effect is not None
    assert isinstance(effect, str)


def test_fancy_saw_wear():
    saw = FancySaw("piła", durability=10)
    saw.use("deska")
    assert saw.durability == 8


# --------------------------------------------------------------------------- #
# Zadanie 4 - duck typing i Protocol
# --------------------------------------------------------------------------- #


def test_multitool_satisfies_protocol_without_inheritance():
    multi = MultiTool("uniwersalny")
    assert isinstance(multi, Tool) is False           # nie dziedziczy po Tool
    assert use_anything(multi, "zadanie") == "Multitool rozwiązuje problem: zadanie"
    assert multi.uses == 1
    assert multi.is_broken is False


def test_use_anything_accepts_tool_subclasses():
    hammer = Hammer("młotek", 1.0)
    assert use_anything(hammer, "gwóźdź").startswith("Uderzam")


@pytest.mark.parametrize("bad_object", ["napis", 42, None, object()])
def test_use_anything_rejects_objects_without_use(bad_object):
    with pytest.raises(TypeError, match="does not implement ToolLike"):
        use_anything(bad_object, "cokolwiek")


def test_all_tools_share_a_single_error_family():
    assert issubclass(ToolBrokenError, ToolError)
