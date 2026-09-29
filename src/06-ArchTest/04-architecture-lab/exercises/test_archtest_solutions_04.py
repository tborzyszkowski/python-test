from archtest_solutions_04 import use_service_without_outer_layer


def test_lab_solution_uses_inward_dependencies():
    assert use_service_without_outer_layer().order_id == "lab"
