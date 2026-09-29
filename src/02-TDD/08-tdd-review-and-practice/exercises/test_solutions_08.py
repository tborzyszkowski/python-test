from solutions_08 import ITERATIONS


def test_final_lab_contains_five_iterations():
    assert len(ITERATIONS) == 5
    assert [item.number for item in ITERATIONS] == [1, 2, 3, 4, 5]


def test_each_iteration_has_all_tdd_phases():
    for item in ITERATIONS:
        assert item.red_test
        assert item.green_change
        assert item.refactor
        assert item.test_level
