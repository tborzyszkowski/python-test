"""Generator obrazów PNG z diagramów Mermaid (``.mmd``).

Diagramy w tym module utrzymujemy w postaci tekstowej (Mermaid), bo:

* są czytelne w ``git diff`` (w przeciwieństwie do PNG),
* łatwo je poprawić bez grafiki,
* renderują się w VS Code (rozszerzenie *Markdown Preview Mermaid Support*).

Ten skrypt tworzy obok każdego pliku ``.mmd`` plik ``.png`` (np. do slajdów
wykładowych). Kolejność działania:

1. jeżeli w systemie jest ``mmdc`` (Mermaid CLI), użyjemy go (najwyższa jakość),
2. w przeciwnym razie użyjemy usługi <https://kroki.io> (wymaga Internetu),
3. jeżeli Kroki zawiedzie, spróbujemy <https://mermaid.ink> (też wymaga Internetu),
4. jeżeli wszystko zawiedzie - pomijamy plik z ostrzeżeniem.

Użycie::

    python src/01-OOP/generate_diagrams.py                  # wszystkie diagramy
    python src/01-OOP/generate_diagrams.py --force          # nadpisz istniejące PNG
    python src/01-OOP/generate_diagrams.py --only 05-aaa    # tylko wybrane tematy
    python src/01-OOP/generate_diagrams.py --engine kroki   # wymuś konkretny silnik
    python src/01-OOP/generate_diagrams.py --dry-run        # pokaż plan

Uwaga dydaktyczna: brak wygenerowanego PNG **nie jest błędem** - diagramy
w ``README.md`` i tak się wyświetlą w podglądzie Markdown VS Code.
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
HTTP_TIMEOUT_SECONDS = 30
USER_AGENT = "python-test-diagram-renderer/1.0 (+educational materials)"
PNG_MAGIC = b"\x89PNG"


def find_diagrams(root: Path, only: list[str] | None = None) -> list[Path]:
    """Zwraca wszystkie pliki ``.mmd`` w katalogach ``diagrams/`` pod ``root``."""
    diagrams = sorted(p for p in root.rglob("diagrams/*.mmd"))
    if only:
        prefixes = tuple(only)
        diagrams = [p for p in diagrams if any(pref in str(p) for pref in prefixes)]
    return diagrams


def render_with_mmdc(source: Path, target: Path, scale: int) -> bool:
    """Renderuje przez lokalne ``mmdc`` (Mermaid CLI). Zwraca ``True`` przy sukcesie."""
    mmdc = shutil.which("mmdc")
    if mmdc is None:
        return False

    command = [
        mmdc,
        "-i",
        str(source),
        "-o",
        str(target),
        "-b",
        "white",
        "-s",
        str(scale),
        "--quiet",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:  # pragma: no cover - środowiskowe
        print(f"    [mmdc] błąd wykonania: {exc}", file=sys.stderr)
        return False

    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip().splitlines()
        detail = message[-1] if message else "nieznany błąd"
        print(f"    [mmdc] porażka: {detail}", file=sys.stderr)
        return False
    return True


def render_with_kroki(source: Path, target: Path) -> bool:
    """Renderuje przez usługę <https://kroki.io> (POST, zwraca PNG)."""
    code = source.read_text(encoding="utf-8")
    request = urllib.request.Request(
        KROKI_URL,
        data=code.encode("utf-8"),
        headers={"Content-Type": "text/plain", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"    [kroki.io] błąd sieci: {exc}", file=sys.stderr)
        return False

    if not payload.startswith(PNG_MAGIC):
        print("    [kroki.io] odpowiedź nie jest obrazem PNG "
              "(najprawdopodobniej błąd składni diagramu)", file=sys.stderr)
        return False

    target.write_bytes(payload)
    return True


def render_with_mermaid_ink(source: Path, target: Path) -> bool:
    """Renderuje przez usługę <https://mermaid.ink> (GET, base64 z kodu)."""
    code = source.read_text(encoding="utf-8")
    encoded = base64.b64encode(code.encode("utf-8")).decode("ascii")
    url = MERMAID_INK_URL + urllib.parse.quote(encoded, safe="") + "?type=png"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"    [mermaid.ink] błąd sieci: {exc}", file=sys.stderr)
        return False

    if not payload.startswith(PNG_MAGIC):
        print("    [mermaid.ink] odpowiedź nie jest obrazem PNG "
              "(najprawdopodobniej błąd składni diagramu)", file=sys.stderr)
        return False

    target.write_bytes(payload)
    return True


def render(source: Path, engine: str, scale: int, force: bool, dry_run: bool) -> bool:
    target = source.with_suffix(".png")
    if target.exists() and not force:
        print(f"  pomijam (PNG istnieje): {target.relative_to(MODULE_ROOT)}")
        return True
    if dry_run:
        print(f"  [dry-run] {source.relative_to(MODULE_ROOT)} -> {target.name}")
        return True

    print(f"  renderuję {source.relative_to(MODULE_ROOT)} ...")
    if engine in ("auto", "mmdc") and render_with_mmdc(source, target, scale):
        print(f"    -> {target.relative_to(MODULE_ROOT)} (mmdc)")
        return True
    if engine == "mmdc":
        return False
    if engine in ("auto", "kroki") and render_with_kroki(source, target):
        print(f"    -> {target.relative_to(MODULE_ROOT)} (kroki.io)")
        return True
    if engine == "kroki":
        return False
    if render_with_mermaid_ink(source, target):
        print(f"    -> {target.relative_to(MODULE_ROOT)} (mermaid.ink)")
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generuje PNG z plików .mmd (Mermaid) w katalogach diagrams/."
    )
    parser.add_argument("--only", nargs="*", metavar="PREFIX",
                        help="ogranicz do tematów zawierających dany fragment ścieżki")
    parser.add_argument("--engine", choices=("auto", "mmdc", "kroki", "ink"), default="auto",
                        help="silnik renderowania (domyślnie: auto)")
    parser.add_argument("--scale", type=int, default=2, help="skala obrazu dla mmdc")
    parser.add_argument("--force", action="store_true", help="nadpisz istniejące PNG")
    parser.add_argument("--dry-run", action="store_true", help="tylko pokaż plan")
    args = parser.parse_args(argv)

    diagrams = find_diagrams(MODULE_ROOT, args.only)
    if not diagrams:
        print("Nie znaleziono żadnych plików .mmd - sprawdź ścieżkę/--only.")
        return 1

    print(f"Znaleziono {len(diagrams)} diagram(ów) w {MODULE_ROOT}.")
    ok, failed = 0, []
    for diagram in diagrams:
        if render(diagram, args.engine, args.scale, args.force, args.dry_run):
            ok += 1
        else:
            failed.append(diagram)

    print(f"\nGotowe: {ok}/{len(diagrams)}.")
    if failed:
        print("Nie udało się wyrenderować:")
        for path in failed:
            print(f"  - {path.relative_to(MODULE_ROOT)}")
        print("\nWskazówka: zainstaluj Mermaid CLI (npm install -g @mermaid-js/mermaid-cli)")
        print("lub sprawdź składnię diagramu na https://mermaid.live")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
