#!/usr/bin/env bash
# Jednorazowa konfiguracja środowiska wirtualnego (Linux / macOS / Git Bash).
# Uruchom z katalogu głównego repozytorium:  bash scripts/setup_venv.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  echo "[1/3] Tworzę środowisko wirtualne .venv ..."
  python3 -m venv .venv
else
  echo "[1/3] Środowisko .venv już istnieje - pomijam tworzenie."
fi

echo "[2/3] Aktualizuję pip ..."
./.venv/bin/python -m pip install --upgrade pip

echo "[3/3] Instaluję zależności z requirements.txt ..."
./.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "Gotowe. Aktywacja w bieżącej sesji:"
echo "  source .venv/bin/activate"
echo ""
echo "Uruchomienie testów modułu OOP:"
echo "  python -m pytest src/01-OOP -c src/01-OOP/pytest.ini -v"
