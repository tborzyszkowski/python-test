<p align="left">
  <a href="#wykorzystanie-ai-w-materiałach">
    <kbd style="background-color: #0056b3; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; border: none; font-family: sans-serif; font-size: 13px;">🤖 AI-Assisted</kbd>
    <kbd style="background-color: #6c757d; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; border: none; font-family: sans-serif; font-size: 13px;">Edukacja</kbd>
  </a>
</p>

# python-test

Materiały dydaktyczne do kursu **testowania programów w Pythonie 3**.

Repozytorium zawiera moduły wykładowe dotyczące budowania testowalnego kodu:
od konstrukcji programowania obiektowego, przez wzorce projektowe ułatwiające
testowanie, aż do frameworków testów jednostkowych (`unittest`, `pytest`).

## Wymagania

- Python **3.11** lub nowszy (zalecany 3.13) — [python.org](https://www.python.org/downloads/)
- Wymagany jest Python **3.11+** oraz pakiety z `requirements.txt`; skrypt
  `scripts/setup_venv.*` instaluje pytest, coverage i Ruff. Typowanie można
  dodatkowo sprawdzać przez Pylance w Visual Studio Code.
- Repozytorium jest celowo **Python-only**. Nie zawiera projektu `.NET 9`; zapis
  o uruchamianiu przez .NET należy traktować jako niepasujący do tego kursu.

## Szybki start

### 1. Sklonuj repozytorium

```bash
git clone https://github.com/<user>/python-test.git
cd python-test
```

### 2. Utwórz i aktywuj środowisko wirtualne

**Windows (PowerShell):**

```powershell
# Jednorazowa konfiguracja (tworzy .venv i instaluje zależności)
.\scripts\setup_venv.ps1

# Aktywacja w bieżącej sesji
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS / Git Bash:**

```bash
bash scripts/setup_venv.sh
source .venv/bin/activate
```

**Ręcznie (każdy system):**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\pip install -r requirements.txt
# Linux/macOS:
.venv/bin/pip install -r requirements.txt
```

### 3. Uruchom testy

```powershell
# Z katalogu głównego projektu (Windows):
.venv\Scripts\python.exe -m pytest src\01-OOP -c src\01-OOP\pytest.ini -v
.venv\Scripts\python.exe -m pytest src\02-TDD -c src\02-TDD\pytest.ini -v
.venv\Scripts\python.exe -m pytest src\03-test_double -c src\03-test_double\pytest.ini -v
.venv\Scripts\python.exe -m behave src\04-BDD\04-passenger-flights\features
.venv\Scripts\python.exe -m pytest src\06-ArchTest -c src\06-ArchTest\pytest.ini -v
.venv\Scripts\python.exe -m pytest src\05-Selenium -c src\05-Selenium\pytest.ini -v

# Z pokryciem kodu (coverage):
.venv\Scripts\python.exe -m pytest src\01-OOP -c src\01-OOP\pytest.ini --cov=src --cov-report=term-missing
.venv\Scripts\python.exe -m pytest src\02-TDD -c src\02-TDD\pytest.ini --cov=src --cov-report=term-missing
```

```bash
# Po aktywacji venv (każdy system):
python -m pytest src/01-OOP -c src/01-OOP/pytest.ini -v
python -m pytest src/02-TDD -c src/02-TDD/pytest.ini -v
python -m pytest src/03-test_double -c src/03-test_double/pytest.ini -v
```

### 4. Wygeneruj diagramy PNG z plików Mermaid

Diagramy w repozytorium są przechowywane jako pliki tekstowe `.mmd` (Mermaid)
w katalogach `diagrams/` każdego tematu. Renderowanie do PNG:

```powershell
# Użyje lokalnego mmdc (jeśli jest zainstalowany), a w przeciwnym razie
# usługi online (kroki.io, potem mermaid.ink) - wymaga połączenia z Internetem
.venv\Scripts\python.exe src\01-OOP\generate_diagrams.py
.venv\Scripts\python.exe src\02-TDD\generate_diagrams.py
.venv\Scripts\python.exe src\04-BDD\generate_diagrams.py

# Tylko wybrane tematy / nadpisanie istniejących plików PNG:
.venv\Scripts\python.exe src\01-OOP\generate_diagrams.py --only 05-aaa-pattern --force
```

> **Wskazówka:** pliki `.mmd` (oraz bloki ```mermaid``` w plikach `README.md`)
> można podglądać bez generowania PNG — wystarczy rozszerzenie
> *Markdown Preview Mermaid Support* w Visual Studio Code.

### 5. Praca w Visual Studio Code

Repozytorium zawiera gotową konfigurację katalogu `.vscode/`, więc po otwarciu
folderu wystarczy:

1. Wskazać interpreter z `.venv` (`Ctrl+Shift+P` → *Python: Select Interpreter*).
2. Otworzyć panel **Testing** (ikona kolby) — pytest wykryje wszystkie testy
  (ponad 440 przypadków) i pozwoli uruchamiać oraz debugować pojedyncze
   pozycje bez wpisywania komend.
3. Nacisnąć `F5`, aby uruchomić jedną z gotowych konfiguracji:
   `Python: bieżący plik`, `Python: pytest (moduł 01-OOP)`,
   `Python: pytest (bieżący plik)`, `Python: pytest (zatrzymaj się przy porażce)`
   oraz `Python: unittest (przykłady tematu 07)`.
4. Zainstalować zalecane rozszerzenia (VS Code zaproponuje je automatycznie) —
   w szczególności *Markdown Preview Mermaid Support*, żeby diagramy w plikach
   `README.md` renderowały się w podglądzie.

## Moduły kursu

- [`src/01-OOP/README.md`](src/01-OOP/README.md) - programowanie obiektowe w kontekście testowalności
  (klasa vs obiekt, hermetyzacja i `@property`, kompozycja, dziedziczenie i polimorfizm)
  oraz wprowadzenie do testów jednostkowych (AAA, `unittest`, `pytest`)
- [`src/02-TDD/README.md`](src/02-TDD/README.md) - teoria i praktyka TDD:
  Red-Green-Refactor, piramida i kwadranty testów, dług technologiczny,
  F.I.R.S.T. oraz trzy projekty rozwijane iteracyjnie.
- [`src/03-test_double/README.md`](src/03-test_double/README.md) - taksonomia
  Dummy, Stub, Fake, Spy i Mock, asercje wartości/stanu/interakcji,
  `unittest.mock`, `monkeypatch` oraz izolowanie I/O i SSO.
- [`src/04-BDD/README.md`](src/04-BDD/README.md) - BDD, Outside-In, Gherkin,
  Behave oraz domena lotów ekonomicznych i premium.
- [`src/06-ArchTest/README.md`](src/06-ArchTest/README.md) - testowanie granic
  architektury przez `pytest-archon` i `import-linter`.
- [`src/05-Selenium/README.md`](src/05-Selenium/README.md) - Selenium WebDriver,
  lokalizatory, waits, Page Object Model i pytest-html.

## Jak wybrać temat na start?

Dla studentów, którzy znają już podstawy Pythona, polecana kolejność pracy:

1. **`01-OOP/01-class-vs-object`** - klasa a obiekt/instancja, pola i metody instancyjne, statyczne i klasowe.
2. **`01-OOP/02-encapsulation-property`** - hermetyzacja i `@property` na przykładzie klas `Point` i `Segment`.
3. **`01-OOP/03-composition`** - kompozycja i wstrzykiwanie zależności - fundament testowalności.
4. **`01-OOP/04-inheritance-polymorphism`** - dziedziczenie i polimorfizm (`Tool`, `Broom`, `Driller`, `Knife`).
5. **`01-OOP/05-aaa-pattern`** - struktura Arrange - Act - Assert.
6. **`01-OOP/06-unit-test-anatomy`** - jak sformułować test jednostkowy jednej własności.
7. **`01-OOP/07-testing-frameworks`** - porównanie `unittest` i `pytest` na tym samym kodzie.
8. **`02-TDD/01-red-green-refactor`** - cykl TDD i różnica względem Test-First.
9. **`02-TDD/05-tdd-string-calculator`** - pierwszy pełny projekt TDD.
10. **`02-TDD/06-tdd-shopping-cart`** - stan i reguły rabatowe.
11. **`02-TDD/07-tdd-bank-account`** - wyjątki, historia i opłaty.
12. **`03-test_double/01-test-double-taxonomy`** - role atrap testowych.
13. **`03-test_double/03-racing-car-and-html`** - Stub czujnika i Fake `StringIO`.
14. **`03-test_double/04-sso-registry`** - Spy i Mock w interakcji z rejestrem.
15. **`04-BDD/04-passenger-flights`** - scenariusze Gherkin i Behave dla lotów.
16. **`06-ArchTest/03-architecture-rules`** - izolacja domeny, warstwy, cykle i konwencje.
17. **`05-Selenium/03-page-object-model`** - POM i testy browserowe E2E.

Sugerowany rytm nauki:

- najpierw przeczytaj `README.md` wybranego tematu,
- uruchom przykłady z `examples/`,
- na końcu rozwiąż zadania z `exercises/` i sprawdź je testami `pytest`.

## Struktura projektu

```
python-test/
├── .github/workflows/            # automatyczne testy i lintowanie
│   └── quality.yml
├── .vscode/                      # konfiguracja VS Code (testy, debugowanie, Mermaid)
│   ├── launch.json               # gotowe konfiguracje F5 (plik, pytest, unittest)
│   ├── settings.json             # Test Explorer, ścieżki importów, kodowanie UTF-8
│   └── extensions.json           # zalecane rozszerzenia (Python, Pylance, Mermaid)
├── .venv/                        # środowisko wirtualne (ignorowane przez git)
├── requirements.txt              # zależności projektu
├── pyproject.toml                # konfiguracja narzędzi (pytest, coverage, ruff)
├── scripts/
│   ├── setup_venv.ps1            # skrypt konfiguracyjny (Windows PowerShell)
│   └── setup_venv.sh             # skrypt konfiguracyjny (Linux/macOS)
└── src/
  ├── 01-OOP/
        ├── README.md             # przegląd modułu i scenariusz wykładu
        ├── pytest.ini            # konfiguracja pytest dla modułu
        ├── conftest.py           # wspólne fixture'y i ścieżki importów
        ├── generate_diagrams.py  # generator PNG z plików .mmd
        ├── 01-class-vs-object/
        │   ├── README.md         # teoria + mini-lab + literatura
        │   ├── diagrams/         # diagramy Mermaid (.mmd) + wygenerowane .png
        │   ├── examples/         # uruchamialny kod demonstrujący koncepcje
        │   └── exercises/        # zadania, rozwiązania i testy zadań
        ├── 02-encapsulation-property/
        ├── 03-composition/
        ├── 04-inheritance-polymorphism/
        ├── 05-aaa-pattern/
        ├── 06-unit-test-anatomy/
        └── 07-testing-frameworks/
      └── 02-TDD/
        ├── README.md             # teoria TDD i scenariusz wykładu
        ├── pytest.ini            # konfiguracja pytest dla modułu
        ├── conftest.py           # wspólne ścieżki importów
        ├── generate_diagrams.py  # generator PNG z plików .mmd
        ├── 01-red-green-refactor/
        ├── 02-test-pyramid-quadrants/
        ├── 03-technical-debt/
        ├── 04-first-and-test-scope/
        ├── 05-tdd-string-calculator/
        ├── 06-tdd-shopping-cart/
        ├── 07-tdd-bank-account/
        └── 08-tdd-review-and-practice/
      └── 03-test_double/
        ├── README.md             # taksonomia i scenariusz wykładu
        ├── pytest.ini            # konfiguracja pytest dla modułu
        ├── conftest.py           # wspólne ścieżki importów
        ├── generate_diagrams.py  # generator PNG z plików .mmd
        ├── 01-test-double-taxonomy/
        ├── 02-verification-and-tools/
        ├── 03-racing-car-and-html/
        └── 04-sso-registry/
      └── 04-BDD/
        ├── README.md
        ├── pytest.ini
        ├── conftest.py
        ├── generate_diagrams.py
        ├── 01-bdd-outside-in/
        ├── 02-gherkin-language/
        ├── 03-behave-structure/
        └── 04-passenger-flights/
      └── 06-ArchTest/
        ├── README.md
        ├── pytest.ini
        ├── conftest.py
        ├── generate_diagrams.py
        ├── 01-why-architecture-tests/
        ├── 02-tools-and-contracts/
        ├── 03-architecture-rules/
        └── 04-architecture-lab/
      └── 05-Selenium/
        ├── README.md
        ├── pytest.ini
        ├── conftest.py
        ├── generate_diagrams.py
        ├── web/
        ├── 01-webdriver-and-locators/
        ├── 02-waits-and-flaky-tests/
        ├── 03-page-object-model/
        └── 04-pytest-integration/
```

Każdy katalog tematyczny zawiera:

- `README.md` - teoria, przykłady kodu, diagramy Mermaid, zadania i literatura,
- `diagrams/` - pliki `.mmd` (Mermaid) z diagramami objaśniającymi kod i pojęcia,
- `examples/` - uruchamialny kod demonstrujący koncepcje (część plików to gotowe testy),
- `exercises/` - treści zadań (`tasks_XX.py`), rozwiązania (`solutions_XX.py`) i testy rozwiązań.

> W tematach 05-07 (`05-aaa-pattern`, `06-unit-test-anatomy`,
> `07-testing-frameworks`) zadaniem studenta jest **napisanie testów**, dlatego
> rozwiązaniem jest tam plik `exercises/test_solutions_XX.py`, a kod produkcyjny
> dostarczany jest w gotowej postaci (`shopping_cart.py`, `string_utils.py`).

> W module `02-TDD` projekty 05-07 pokazują pełny cykl TDD; pliki
> `test_*.py` są punktami obserwacji kolejnych iteracji, a `tdd_solutions_XX.py`
> zawierają rozwiązania ćwiczeń bez kolizji nazw z modułem `01-OOP`.

## Zależności

| Pakiet      | Wersja  | Opis                                     |
|-------------|---------|------------------------------------------|
| pytest      | ≥ 7.4   | framework do testów jednostkowych        |
| pytest-cov  | ≥ 4.1   | pokrycie kodu testami (`coverage`)       |
| ruff        | ≥ 0.8   | lintowanie i kontrola stylu              |
| behave      | ≥ 1.2.6 | automatyzacja scenariuszy Gherkin        |
| pytest-archon | ≥ 0.0.7 | reguły architektury jako testy pytest     |
| import-linter | ≥ 2.15  | kontrakty importów i warstw               |

## Konwencje w repozytorium

- Każdy temat w osobnym katalogu o nazwie `NN-nazwa-tematu`.
- Skrypty demonstracyjne uruchamia się przez `python examples/nazwa.py`,
  a pliki `test_*.py` przez `pytest examples/test_*.py -v`.
- Wszystkie testy to pliki `test_*.py` z unikalnymi nazwami; moduły mają własne
  `conftest.py`, które dodają katalogi przykładów i ćwiczeń do `sys.path`.
- Diagramy trzymamy w Mermaid (`.mmd`), bo są czytelne w diffach Git.

## Licencja

Materiały objęte licencją **CC BY-NC 4.0** — szczegóły w pliku [LICENSE.md](LICENSE.md).

## Wykorzystanie AI w materiałach

Materiały dydaktyczne zawarte w tym repozytorium są przygotowywane przy wsparciu
narzędzi sztucznej inteligencji (Generative AI), które pełnią rolę asystenta twórcy.

Sztuczna inteligencja jest wykorzystywana w celach pomocniczych, w szczególności do:

- Współtworzenia i optymalizacji bazowych przykładów kodu oraz konfiguracji.
- Formatowania, strukturyzacji oraz automatyzacji generowania dokumentacji.
- Wsparcia procesu redakcyjnego, korekty językowej oraz generowania alternatywnych
  wyjaśnień pojęć technicznych.

Wszystkie materiały, schematy oraz kody źródłowe podlegają **weryfikacji
merytorycznej i edycji przez człowieka**. Ostateczna treść oraz układ dydaktyczny
są wynikiem autorskiego nadzoru, co zapewnia ich poprawność oraz zgodność ze
standardami akademickimi.
