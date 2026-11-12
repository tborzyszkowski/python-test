# Temat 05 - Większy przykład: `SubscriptionService`

> Moduł: [03-test_double](../README.md) · Poprzedni:
> [04-sso-registry](../04-sso-registry/README.md)

## Cel

Ten przykład pokazuje cały przepływ aktywacji rocznej subskrypcji platformy
edukacyjnej. `SubscriptionService` współpracuje z repozytorium, bramką
płatniczą, powiadomieniami i audytem. Testy izolują te zależności różnymi
test doubles, ale każde użycie odpowiada innemu pytaniu testu.

Kod produkcyjny znajduje się w
[subscription_service.py](examples/subscription_service.py), a wykonywalne
przykłady w [test_subscription_service.py](examples/test_subscription_service.py).

## Model biznesowy

1. Serwis odczytuje rabat i podatek z `os.environ`.
2. Wylicza cenę planu i obciąża `PaymentGateway`.
3. Po sukcesie tworzy subskrypcję ważną 365 dni.
4. Zapisuje ją w `DatabaseRepository`.
5. Wysyła e-mail i zapisuje zdarzenie audytowe.
6. Gdy zapis bazy się nie uda, wycofuje transakcję płatniczą.

W testach płatność, baza, e-mail i zegar nie wykonują operacji produkcyjnych.

## Mapa: który double odpowiada na jakie pytanie?

| Double | Przykład | Pytanie testu |
|---|---|---|
| **Dummy** | `DummyAuditLogger` | Czy mogę spełnić wymagany argument, gdy audyt nie jest tematem testu? |
| **Stub** | `PaymentGatewayStub` | Co zrobi serwis po odpowiedzi `success` albo `declined`? |
| **Fake** | `InMemorySubscriptionRepository` | Czy uproszczone repozytorium naprawdę zapisuje i odczytuje stan? |
| **Spy** | `EmailNotificationSpy` | Jakie wiadomości zostały wysłane i w jakiej kolejności? |
| **Mock** | `Mock(spec=...)` | Czy rollback lub e-mail zostały wywołane dokładnie z właściwymi argumentami? |
| **Monkeypatch** | czas i `os.environ` | Jak przetestować datę i konfigurację bez zmiany kodu źródłowego? |

### 1. Dummy: wymagany, ale nieinteresujący argument

`SubscriptionService` potrzebuje loggera w konstruktorze. Test `quote` bada
wyłącznie matematykę ceny, więc `DummyAuditLogger` nie zapisuje żadnych danych.
To nie jest Stub: logger nie dostarcza odpowiedzi potrzebnej do obliczenia ceny.

W testach mamy trzy różne zastosowania:

1. **Obliczenia ceny** - pozostałe zależności są nieistotne, a logger tylko
   spełnia wymagany argument konstruktora.
2. **Inny plan cenowy** - ten sam Dummy można ponownie wykorzystać, bo nie ma
   własnego stanu i nie wpływa na wynik.
3. **Pełna aktywacja** - nawet gdy przechodzimy przez zapis i e-mail, audyt
   nadal może być poza zakresem testu.

```python
service = SubscriptionService(Mock(), Mock(), Mock(), DummyAuditLogger())
assert service.quote(PLAN) == Decimal("61.50")
```

Ważne: Dummy nie powinien mieć asercji. Gdy chcemy sprawdzać treść logu,
potrzebujemy Spy albo Mock.

### 2. Stub: kontrolowana odpowiedź

`PaymentGatewayStub` zawsze zwraca przekazany `PaymentResult`. Dzięki temu
możemy osobno pokazać trzy istotne odpowiedzi API, bez HTTP, karty i pieniędzy:

1. `success` z identyfikatorem transakcji - aktywacja kończy się powodzeniem.
2. `declined` - serwis zgłasza błąd domenowy i nie zapisuje subskrypcji.
3. `success` bez `transaction_id` - odpowiedź jest niespójna i również nie
   może doprowadzić do aktywacji.

```python
gateway = PaymentGatewayStub(PaymentResult("declined"))
with pytest.raises(RuntimeError, match="declined"):
    service.activate("user-1", PLAN, "bad-card")
```

Stub odpowiada na pytanie o **wynik**. Nie sprawdzamy, ile razy wywołano
`charge`; od tego służy Mock albo Spy.

### 3. Fake: działająca implementacja

`InMemorySubscriptionRepository` ma ten sam używany kontrakt co repozytorium
bazy, ale przechowuje dane w słowniku. Testujemy jego rzeczywiste zachowanie:
zapis, odczyt i rozdzielenie danych różnych użytkowników.

```python
repository = InMemorySubscriptionRepository()
repository.save(subscription)
assert repository.get_for_user("user-1") == subscription
```

Fake jest większy niż Stub, bo posiada stan i logikę. W testach pokazujemy:

1. zapis i późniejszy odczyt subskrypcji,
2. izolację danych dwóch użytkowników,
3. odczyt nieznanego użytkownika jako `None` oraz zastąpienie starszego
   rekordu tego samego użytkownika.

Nadal nie powinien udawać całego SQL ani testować szczegółów konkretnego
silnika bazy.

### 4. Spy: historia obserwowalnych wywołań

`EmailNotificationSpy` nie wysyła wiadomości. Zachowuje jednak krotki
`(user_id, subject, body)`, więc test może sprawdzić treść i kolejność bez
wiązania się z biblioteką SMTP.

```python
assert len(notifications.sent_emails) == 1
assert "Dziękujemy za subskrypcję" in notifications.sent_emails[0][2]
```

Spy jest dobry, gdy chcemy elastycznie analizować kilka wywołań lub ich stan,
a nie definiować od razu ścisłego oczekiwania. Przykłady obejmują:

1. sprawdzenie adresata, tematu i treści potwierdzenia,
2. sprawdzenie kolejności dwóch wiadomości,
3. potwierdzenie, że po odrzuconej płatności nie wysłano żadnego maila.

### 5. Mock: ścisła interakcja

W razie awarii zapisu płatność musi zostać wycofana dokładnie raz i dla
konkretnego identyfikatora transakcji. `Mock` zapisuje interakcję i udostępnia
asercję kontraktu:

```python
gateway.rollback_transaction.assert_called_once_with("tx-404")
```

`spec=DatabaseRepository` dodatkowo ogranicza literówki w nazwach metod.
W testach Mock sprawdza trzy różne kontrakty:

1. rollback dokładnie raz z właściwym identyfikatorem po błędzie bazy,
2. dokładne argumenty pojedynczego e-maila po sukcesie,
3. brak wywołania płatności i zapisu dla niepoprawnego wejścia.

Mock należy stosować do ważnych kontraktów, nie do każdej prywatnej metody.

### 6. Monkeypatching: czas i konfiguracja

Fixture `monkeypatch` przywraca stan po teście. Podmieniamy symbol `datetime`
**w module, który go używa**, oraz zmienne środowiskowe:

```python
monkeypatch.setattr(subscription_service, "datetime", FrozenDateTime)
monkeypatch.setenv("SUBSCRIPTION_DISCOUNT", "0.20")
```

Dzięki stałemu zegarowi test wygaśnięcia nie zależy od dnia uruchomienia.
Przykłady obejmują:

1. subskrypcję wygasłą,
2. subskrypcję aktywną w kontrolowanym momencie,
3. dwa warianty rabatu i podatku z `os.environ`.

Zmiana `os.environ` pozwala sprawdzić konfigurację bez edycji pliku `.env`.

## Jak uruchomić

Z katalogu repozytorium:

```powershell
.venv\Scripts\python.exe -m pytest src\03-test_double\05-bigger-sample -v
```

Można uruchomić pojedynczą grupę:

```powershell
.venv\Scripts\python.exe -m pytest src\03-test_double\05-bigger-sample\examples\test_subscription_service.py::TestMock -v
```

## Ćwiczenia do samodzielnego wykonania

1. Dodaj Stub płatności, który rzuca `TimeoutError`, i zdecyduj, jaki błąd
   domenowy powinien zobaczyć klient.
2. Rozszerz Fake o metodę `delete_for_user` i napisz test usuwania.
3. Dodaj Spy dla `AuditLogger` i sprawdź, że zdarzenie nie jest logowane po
   odrzuconej płatności.
4. Zastąp Mock powiadomień Spyem. Zastanów się, czy test nadal sprawdza
   kontrakt, czy tylko szczegół implementacji.
5. Zmień `365` dni na regułę kalendarzową i uzupełnij testy graniczne.

## Przykładowe rozwiązania ćwiczeń

Rozwiązania znajdują się w osobnym pliku
[td_solutions_05.py](exercises/td_solutions_05.py). Są zapisane jako małe,
uruchamialne funkcje i klasy, aby można było porównać podejście z własnym
rozwiązaniem bez modyfikowania kodu przykładu.

Plik pokazuje:

- Stub rzucający `TimeoutError` i tłumaczenie go na błąd domenowy,
- Fake z metodą `delete_for_user`,
- Spy audytu oraz brak logu po odrzuconej płatności,
- zastąpienie Mocka powiadomień przez `EmailNotificationSpy`,
- regułę rocznej daty kalendarzowej wraz z przypadkiem 29 lutego.

Można sprawdzić składnię i przykładowe funkcje poleceniem:

```powershell
.venv\Scripts\python.exe -c "import sys; sys.path[:0] = [r'src\03-test_double\05-bigger-sample\examples', r'src\03-test_double\05-bigger-sample\exercises']; from td_solutions_05 import calendar_expiry_examples; print(calendar_expiry_examples())"
```
