"""Renderowanie diagramow Selenium do PNG przez Kroki lub Mermaid Ink."""

from __future__ import annotations

import argparse
import base64
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KROKI_URL = "https://kroki.io/mermaid/png/"


def render(path: Path, force: bool) -> bool:
    target = path.with_suffix(".png")
    if target.exists() and not force and target.stat().st_mtime >= path.stat().st_mtime:
        return True
    try:
        request = urllib.request.Request(
            KROKI_URL,
            data=path.read_bytes(),
            headers={"Content-Type": "text/plain", "User-Agent": "python-test-selenium"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        url = "https://mermaid.ink/img/" + urllib.parse.quote(encoded, safe="") + "?type=png"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "python-test-selenium"})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            return False
    if not data.startswith(b"\x89PNG"):
        return False
    target.write_bytes(data)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    diagrams = sorted(ROOT.rglob("diagrams/*.mmd"))
    results = [render(path, args.force) for path in diagrams]
    print(f"Gotowe: {sum(results)}/{len(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
