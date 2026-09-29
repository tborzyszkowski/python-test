from td_solutions_02 import send_with_mock


def test_solution_verifies_result_and_interaction():
    result, sender = send_with_mock("hello")
    assert result == "accepted"
    sender.send.assert_called_once_with("hello")
