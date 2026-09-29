from td_solutions_01 import fake_messages, spy_calls, stub_alert


def test_stub_solution():
    assert stub_alert("queued") == "queued"


def test_fake_solution():
    assert fake_messages() == ["hello"]


def test_spy_solution():
    assert spy_calls() == [("hello",)]
