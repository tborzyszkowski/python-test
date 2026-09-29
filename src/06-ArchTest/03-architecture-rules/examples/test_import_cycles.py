from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "arch_sample"


def import_graph(root: Path) -> dict[str, set[str]]:
    modules = {
        path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
        for path in root.rglob("*.py")
    }
    modules = {f"arch_sample.{name}" for name in modules if not name.endswith("__init__")}
    graph: dict[str, set[str]] = defaultdict(set)
    for path in root.rglob("*.py"):
        module = f"arch_sample.{path.relative_to(root).with_suffix('').as_posix().replace('/', '.') }"
        if module.endswith(".__init__"):
            module = module.removesuffix(".__init__")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                graph[module].update(alias.name for alias in node.names if alias.name in modules)
            elif isinstance(node, ast.ImportFrom) and node.module:
                target = node.module if node.level == 0 else module.rsplit(".", node.level)[0] + "." + node.module
                if target in modules:
                    graph[module].add(target)
    return graph


def has_cycle(graph: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def test_arch_sample_has_no_import_cycle():
    assert has_cycle(import_graph(PACKAGE_ROOT)) is False
