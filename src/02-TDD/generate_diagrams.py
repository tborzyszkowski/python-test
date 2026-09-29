"""Renderuje pliki Mermaid do PNG.

Kolejnosc silnikow: lokalny ``mmdc``, Kroki, mermaid.ink. Pliki PNG sa
odswiezane tylko wtedy, gdy zrodlo ``.mmd`` jest nowsze; ``--force`` wymusza
renderowanie wszystkich diagramow.
"""

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

MODULE_ROOT = Path(__file__).resolve().parent
KROKI_URL = "https://kroki.io/mermaid/png/"
MERMAID_INK_URL = "https://mermaid.ink/img/"
USER_AGENT = "python-test-tdd-diagram-renderer/1.0"
PNG_MAGIC = b"\x89PNG"


def find_diagrams(only: list[str] | None) -> list[Path]:
    diagrams = sorted(MODULE_ROOT.rglob("diagrams/*.mmd"))
    if only:
        diagrams = [path for path in diagrams if any(value in str(path) for value in only)]
    return diagrams


def render_with_mmdc(source: Path, target: Path, scale: int) -> bool:
    executable = shutil.which("mmdc")
    if executable is None:
        return False
    command = [executable, "-i", str(source), "-o", str(target), "-b", "white", "-s", str(scale), "--quiet"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and target.exists()


def _download_png(request: urllib.request.Request) -> bytes | None:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  blad sieci: {exc}", file=sys.stderr)
        return None
    return payload if payload.startswith(PNG_MAGIC) else None


def render_with_kroki(source: Path, target: Path) -> bool:
    request = urllib.request.Request(
        KROKI_URL,
        data=source.read_text(encoding="utf-8").encode("utf-8"),
        headers={"Content-Type": "text/plain", "User-Agent": USER_AGENT},
        method="POST",
    )
    payload = _download_png(request)
    if payload is None:
        return False
    target.write_bytes(payload)
    return True


def render_with_mermaid_ink(source: Path, target: Path) -> bool:
    encoded = base64.b64encode(source.read_bytes()).decode("ascii")
    url = MERMAID_INK_URL + urllib.parse.quote(encoded, safe="") + "?type=png"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    payload = _download_png(request)
    if payload is None:
        return False
    target.write_bytes(payload)
    return True


def render(source: Path, engine: str, scale: int, force: bool, dry_run: bool) -> bool:
    target = source.with_suffix(".png")
    if target.exists() and not force and target.stat().st_mtime >= source.stat().st_mtime:
        print(f"pomijam (aktualny): {target.relative_to(MODULE_ROOT)}")
        return True
    if dry_run:
        print(f"dry-run: {source.relative_to(MODULE_ROOT)} -> {target.name}")
        return True
    if render_with_mmdc(source, target, scale) if engine in ("auto", "mmdc") else False:
        return True
    if engine == "mmdc":
        return False
    if engine in ("auto", "kroki") and render_with_kroki(source, target):
        return True
    if engine == "kroki":
        return False
    return render_with_mermaid_ink(source, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="fragment sciezki tematu")
    parser.add_argument("--engine", choices=("auto", "mmdc", "kroki", "ink"), default="auto")
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    diagrams = find_diagrams(args.only)
    if not diagrams:
        print("Nie znaleziono plikow .mmd.")
        return 1
    results = [render(path, args.engine, args.scale, args.force, args.dry_run) for path in diagrams]
    print(f"Gotowe: {sum(results)}/{len(results)}")
    return 0 if all(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
