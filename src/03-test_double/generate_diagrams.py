"""Generator PNG dla diagramow Mermaid modulu Test Doubles."""

from __future__ import annotations

import argparse
import base64
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KROKI = "https://kroki.io/mermaid/png/"
INK = "https://mermaid.ink/img/"


def png_from_request(request: urllib.request.Request) -> bytes | None:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"blad renderowania: {exc}", file=sys.stderr)
        return None
    return data if data.startswith(b"\x89PNG") else None


def render(path: Path, force: bool) -> bool:
    target = path.with_suffix(".png")
    if target.exists() and not force and target.stat().st_mtime >= path.stat().st_mtime:
        return True
    executable = shutil.which("mmdc")
    if executable:
        result = subprocess.run(
            [executable, "-i", str(path), "-o", str(target), "-b", "white", "--quiet"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return True
    request = urllib.request.Request(
        KROKI,
        data=path.read_bytes(),
        headers={"Content-Type": "text/plain", "User-Agent": "python-test-test-double"},
        method="POST",
    )
    data = png_from_request(request)
    if data is None:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        url = INK + urllib.parse.quote(encoded, safe="") + "?type=png"
        data = png_from_request(urllib.request.Request(url))
    if data is None:
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
