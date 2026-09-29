from __future__ import annotations

import pytest
from tdd_solutions_01 import TodoList


def test_solution_supports_full_red_green_refactor_contract():
    todos = TodoList()
    todos.add("zadanie")
    assert todos.pending() == ["zadanie"]
    todos.complete("zadanie")
    assert todos.pending() == []


def test_solution_rejects_empty_title():
    with pytest.raises(ValueError, match="empty"):
        TodoList().add("")
