# Jednorazowa konfiguracja środowiska wirtualnego (Windows PowerShell).
# Uruchom z katalogu głównego repozytorium:  .\scripts\setup_venv.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv")) {
    Write-Host "[1/3] Tworzę środowisko wirtualne .venv ..." -ForegroundColor Cyan
    python -m venv .venv
} else {
    Write-Host "[1/3] Środowisko .venv już istnieje - pomijam tworzenie." -ForegroundColor Yellow
}

Write-Host "[2/3] Aktualizuję pip ..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip

Write-Host "[3/3] Instaluję zależności z requirements.txt ..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host ""
Write-Host "Gotowe. Aktywacja w bieżącej sesji:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Uruchomienie testów modułu OOP:" -ForegroundColor Green
Write-Host "  .venv\Scripts\python.exe -m pytest src\01-OOP -c src\01-OOP\pytest.ini -v"
