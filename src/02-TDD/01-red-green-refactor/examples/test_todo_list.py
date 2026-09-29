"""Testy koncowego kontraktu TodoList; historia iteracji jest w README."""

from __future__ import annotations

import pytest
from red_green_refactor_demo import TodoList


def test_new_list_has_no_pending_items():
    todos = TodoList()

    assert todos.pending() == []


def test_adding_title_creates_pending_item():
    todos = TodoList()
    todos.add("napisac test")

    assert todos.pending() == ["napisac test"]
    assert len(todos) == 1


def test_completing_item_removes_it_from_pending():
    todos = TodoList()
    todos.add("napisac test")

    todos.complete("napisac test")

    assert todos.pending() == []


def test_empty_title_is_rejected_without_changing_list():
    todos = TodoList()

    with pytest.raises(ValueError, match="empty"):
        todos.add("   ")

    assert len(todos) == 0


def test_missing_title_is_rejected():
    todos = TodoList()

    with pytest.raises(KeyError, match="missing"):
        todos.complete("nie ma")
