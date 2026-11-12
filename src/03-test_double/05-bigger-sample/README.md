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

```python
service = SubscriptionService(Mock(), Mock(), Mock(), DummyAuditLogger())
assert service.quote(PLAN) == Decimal("61.50")
```

### 2. Stub: kontrolowana odpowiedź

`PaymentGatewayStub` zawsze zwraca przekazany `PaymentResult`. Dzięki temu
możemy osobno pokazać ścieżkę zaakceptowanej i odrzuconej płatności, bez HTTP,
karty i pieniędzy.

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

Fake jest większy niż Stub, bo posiada stan i logikę. Nadal nie powinien
udawać całego SQL ani testować szczegółów konkretnego silnika bazy.

### 4. Spy: historia obserwowalnych wywołań

`EmailNotificationSpy` nie wysyła wiadomości. Zachowuje jednak krotki
`(user_id, subject, body)`, więc test może sprawdzić treść i kolejność bez
wiązania się z biblioteką SMTP.

```python
assert len(notifications.sent_emails) == 1
assert "Dziękujemy za subskrypcję" in notifications.sent_emails[0][2]
```

Spy jest dobry, gdy chcemy elastycznie analizować kilka wywołań lub ich stan,
a nie definiować od razu ścisłego oczekiwania.

### 5. Mock: ścisła interakcja

W razie awarii zapisu płatność musi zostać wycofana dokładnie raz i dla
konkretnego identyfikatora transakcji. `Mock` zapisuje interakcję i udostępnia
asercję kontraktu:

```python
gateway.rollback_transaction.assert_called_once_with("tx-404")
```

`spec=DatabaseRepository` dodatkowo ogranicza literówki w nazwach metod.
Mock należy stosować do ważnych kontraktów, nie do każdej prywatnej metody.

### 6. Monkeypatching: czas i konfiguracja

Fixture `monkeypatch` przywraca stan po teście. Podmieniamy symbol `datetime`
**w module, który go używa**, oraz zmienne środowiskowe:

```python
monkeypatch.setattr(subscription_service, "datetime", FrozenDateTime)
monkeypatch.setenv("SUBSCRIPTION_DISCOUNT", "0.20")
```

Dzięki stałemu zegarowi test wygaśnięcia nie zależy od dnia uruchomienia.
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
