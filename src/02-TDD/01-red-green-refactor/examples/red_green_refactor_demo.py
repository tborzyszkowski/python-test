"""Finalny kod demonstracyjny do cyklu Red-Green-Refactor."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TodoItem:
    title: str
    done: bool = False


class TodoList:
    """Minimalny model listy zadan wypracowany przyrostowo przez TDD."""

    def __init__(self) -> None:
        self._items: list[TodoItem] = []

    def add(self, title: str) -> None:
        if not title.strip():
            raise ValueError("title must not be empty")
        self._items.append(TodoItem(title=title))

    def pending(self) -> list[str]:
        return [item.title for item in self._items if not item.done]

    def complete(self, title: str) -> None:
        for item in self._items:
            if item.title == title:
                item.done = True
                return
        raise KeyError(f"missing todo: {title!r}")

    def __len__(self) -> int:
        return len(self._items)


def main() -> None:
    todos = TodoList()
    todos.add("napisac test Red")
    todos.add("uruchomic Green")
    print("pending:", todos.pending())
    todos.complete("napisac test Red")
    print("after complete:", todos.pending())


if __name__ == "__main__":
    main()
