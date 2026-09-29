from td_solutions_04 import mock_logout, spy_logout


def test_spy_solution():
    assert spy_logout("abc") == [("unregister", "abc")]


def test_mock_solution():
    registry = mock_logout("abc")
    registry.unregister.assert_called_once_with("abc")
