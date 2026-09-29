from td_solutions_03 import converted_text, safe_car


def test_solution_car():
    assert safe_car([1.0, 1.1, 1.2, 1.3]) is True


def test_solution_converter():
    assert converted_text("<p>Hello</p>") == "Hello\n"
