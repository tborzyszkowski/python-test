from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "arch_sample"
BAD_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "exercises" / "bad_architecture"


def _module_name(path: Path, root: Path, package_name: str) -> str:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(part for part in (package_name, *parts) if part)


def _resolve_imports(module: str, node: ast.Import | ast.ImportFrom, modules: set[str]) -> set[str]:
    if isinstance(node, ast.Import):
        return {
            alias.name
            for alias in node.names
            if alias.name in modules
        }

    if node.level == 0:
        base = node.module or ""
    else:
        package_parts = module.split(".")[:-1]
        remove_count = node.level - 1
        if remove_count:
            package_parts = package_parts[:-remove_count]
        base = ".".join((*package_parts, *(node.module or "").split("."))).strip(".")

    targets = {base} if base in modules else set()
    for alias in node.names:
        candidate = ".".join(part for part in (base, alias.name) if part)
        if candidate in modules:
            targets.add(candidate)
    return targets


def import_graph(root: Path, package_name: str = "arch_sample") -> dict[str, set[str]]:
    paths = sorted(root.rglob("*.py"))
    modules = {_module_name(path, root, package_name) for path in paths}
    graph: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        module = _module_name(path, root, package_name)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                graph[module].update(_resolve_imports(module, node, modules))
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


def test_known_bad_fixture_contains_an_import_cycle():
    graph = import_graph(BAD_PACKAGE_ROOT, package_name="")

    assert graph["cycle_a"] == {"cycle_b"}
    assert graph["cycle_b"] == {"cycle_a"}
    assert has_cycle(graph) is True


def test_import_graph_resolves_relative_imports_and_fromlist_submodules(tmp_path):
    package_root = tmp_path / "sample"
    services = package_root / "services"
    domain = package_root / "domain"
    services.mkdir(parents=True)
    domain.mkdir()
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (services / "__init__.py").write_text("", encoding="utf-8")
    (domain / "__init__.py").write_text("", encoding="utf-8")
    (services / "sibling.py").write_text("", encoding="utf-8")
    (domain / "entities.py").write_text("", encoding="utf-8")
    (services / "orders.py").write_text(
        "from . import sibling\nfrom ..domain import entities\n",
        encoding="utf-8",
    )

    graph = import_graph(package_root, package_name="sample")

    assert graph["sample.services.orders"] == {
        "sample.services",
        "sample.services.sibling",
        "sample.domain",
        "sample.domain.entities",
    }
