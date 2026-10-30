# Rozszerzenie modułu 03-test_double

## Przegląd zmian

Moduł `src/03-test_double` został rozszerzony o zaawansowane przykłady, wytyczne anti-patterns oraz realistyczne scenariusze.

### Liczby

- **Przed**: 29 testów
- **Po**: 65 testów (+36 testów, +124%)
- **Nowe pliki**: 3
- **Zmienione pliki**: 6

---

## 1. Anti-patterns i wytyczne (README.md główny)

Dodano nową sekcję **"Anti-patterns: kiedy Double robi się zbyt skomplikowany"** z 5 typowymi pułapkami:

1. **Over-mocking**: mockowanie całego stosu aplikacji
2. **Mock brittle tests**: za szczegółowe asercje interakcji
3. **Fake zamiast Stub**: logika, której test nie wymaga
4. **Mockowanie szczegółów implementacji**: np. `_private_method`
5. **Niewystarczająca izolacja**: fałsz bezpieczeństwa z samymi mockami

Każda pułapka ma kod złej i dobrej praktyki + objaśnienia.

### Porównanie narzędzi

Dodano tabelę porównującą **Mock vs monkeypatch vs Spy** z wymiarami:
- Rola (Mock/Stub/Spy)
- Oczekiwania?
- Automatyczna weryfikacja?
- Kiedy używać?

---

## 2. Zaawansowane techniki Mock (Temat 02)

### Nowy plik: `02-verification-and-tools/examples/advanced_mocks.py`

Zawiera 8 zaawansowanych technik:

1. **side_effect**: sekwencja wartości i wyjątków (retry pattern)
2. **MagicMock**: wspiera `__iter__`, `__enter__`, `__len__`
3. **spec**: ochrona przed literówkami w API
4. **PropertyMock**: mockowanie `@property`
5. **patch.object**: mockowanie metody konkretnego obiektu
6. **patch.multiple**: kilka mocków w jednym kontekście
7. **call()**: dokładne sprawdzenie wielokrotnych wołań
8. **reset_mock()**: czyszczenie historii wołań

Każda technika ma:
- Funkcję demo z objaśnieniami
- Testy w `test_advanced_mocks.py`
- Prakticze przykłady z kodem produkcyjnym

### Statystyka testów

- 14 nowych testów dla zaawansowanych technik
- Wszystkie testy przechodzą
- Testy można uruchamiać jako demo: `python advanced_mocks.py`

### README 02 uzupełniony

Dodano sekcję "Zaawansowane techniki Mock" z przykładami kodu i odwołaniami do pełnych implementacji.

---

## 3. Realistyczny scenariusz SSO (Temat 04)

### Nowy plik: `04-sso-registry/examples/realistic_sso.py`

Zawiera zaawansowaną implementację zarządzania sesją z:
- Kilkoma operacjami: `login()`, `logout()`, `validate_session()`, `get_current_user()`, `logout_all_user_sessions()`
- Zarządzaniem wygaśnięciem tokenu (`expires_at`)
- Synchronizacją stanu lokalnego i zdalnego (SSO Registry)
- Obsługą błędów (pusty token, sesja wygasła)

**Nowości w domenie**:
- `UserSession` z czasem życia
- `TokenStatus` enum
- Operacje na wielu sesji jednego użytkownika
- Refresh activity tracking

### Nowy plik: `04-sso-registry/examples/test_realistic_sso.py`

22 nowych testów obejmujące:

**TestUserSessionLifecycle** (3 testy)
- Tworzenie sesji
- Wygaśnięcie
- Odświeżanie aktywności

**TestSessionServiceLogin** (3 testy)
- Zalogowanie z prawidłowymi kredencjałami
- Odrzucenie pustych tokenów/user_id
- Kilka loginów dla tego samego użytkownika

**TestSessionServiceLogout** (3 testy)
- Wylogowanie aktualizuje SSO i stan lokalny
- Odrzucenie pustych tokenów
- Obsługa nieistniejących tokenów

**TestSessionServiceValidation** (3 testy)
- Walidacja aktywnej sesji
- Walidacja wygasłej sesji
- Walidacja niezarejestrowanego tokenu

**TestSessionServiceGetCurrentUser** (2 testy)
- Pobranie user_id dla aktywnej sesji
- Zwrócenie None dla nieaktywnej

**TestSessionServiceLogoutAll** (2 testy)
- Wylogowanie wszystkich sesji użytkownika
- Ignorowanie sesji innych użytkowników

**TestSessionServiceWithMock** (3 testy)
- Mockowanie interactions
- Sprawdzanie kontraktu SsoRegistry
- Obsługa błędów SSO

**TestSpyVsMockComparison** (2 testy)
- Spy: elastyczność w analizie
- Mock: egzekwowanie kontraktu

### README 04 uzupełniony

Nowa sekcja "Realistyczny scenariusz: zarządzanie sesją użytkownika" z:
- Opisem domeny
- Przykładami kodu
- Wskazówkami praktycznymi

---

## 4. Uzupełnienie docstrings

Dodano/poprawiono docstrings we wszystkich plikach example:

### `01-test-double-taxonomy/examples/taxonomy_examples.py`
- Klasa `Notifier` (Protocol)
- Klasa `AlertService`
- Wszystkie klasy atrap (Dummy, Stub, Fake, Spy)
- Funkcja `demo()`

### `02-verification-and-tools/examples/mock_tools.py`
- Klasa `AlertService`
- Funkcja `read_mode()`
- Wszystkie funkcje demo

### `03-racing-car-and-html/examples/racing_and_html.py`
- Klasa `StubPressureSensor`
- Klasa `RacingCar`
- Klasa `HtmlPagesConverter`
- Funkcja `main()`

### `04-sso-registry/examples/sso_registry.py`
- Interfejsy i klasy
- Funkcja `main()`

---

## Uruchamianie

```powershell
# Wszystkie testy (65)
.venv\Scripts\python.exe -m pytest src\03-test_double -c src\03-test_double\pytest.ini -v

# Zaawansowane przykłady
.venv\Scripts\python.exe src\03-test_double\02-verification-and-tools\examples\advanced_mocks.py

# Realistyczny scenariusz
.venv\Scripts\python.exe src\03-test_double\04-sso-registry\examples\realistic_sso.py
```

---

## Wyniki walidacji

✓ 65/65 testów przechodzi
✓ Wszystkie demo uruchamiają się bez błędów
✓ Brak naruszenia istniejących testów
✓ Kod wygenerowany z pełnymi docstringami
✓ Zgodny z Python 3.13 i pytest 9.1

---

## Zawartość rozszerzenia

| Obszar | Dodane | Wynik |
|--------|--------|-------|
| Anti-patterns + porównanie narzędzi | 2 sekcje w README | Kompletne wytyczne |
| Zaawansowane Mock | 2 pliki (py + test) | 14 testów |
| Realistyczny scenariusz SSO | 2 pliki (py + test) | 22 testy |
| Docstrings | 4 pliki aktualizacji | Wszystkie klasy opisane |
| **RAZEM** | **+36 testów** | **65 testów łącznie** |

