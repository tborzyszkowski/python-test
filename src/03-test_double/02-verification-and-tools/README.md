# Temat 02 - Weryfikacja i narzędzia Python

> Moduł: [03-test_double](../README.md) · Poprzedni: [01-test-double-taxonomy](../01-test-double-taxonomy/README.md) · Następny: [03-racing-car-and-html](../03-racing-car-and-html/README.md)

## Trzy kategorie asercji

### 1. Return value / Exception

Pytanie: „co metoda zwróciła albo jaki wyjątek zgłosiła?”

```python
result = service.calculate()
assert result == 42

with pytest.raises(ValueError, match="invalid"):
    service.calculate()
```

### 2. State change

Pytanie: „jak zmienił się stan obiektu?”

```python
account.deposit(100)
assert account.balance == 100
```

### 3. Method call / Interaction

Pytanie: „czy zależność dostała właściwe wywołanie?”

```python
sender.send.assert_called_once_with("alert")
```

```mermaid
flowchart TD
    Q{"Co jest kontraktem?"}
    Q -->|"wartosc lub wyjatek"| R["Return value / Exception"]
    Q -->|"stan SUT"| S["State change"]
    Q -->|"wspolpraca z zaleznoscia"| I["Method call / Interaction"]
    R --> T["Stub / Fake"]
    S --> F["Fake / real object"]
    I --> M["Spy / Mock"]
```

## `unittest.mock`

### `Mock`

```python
from unittest.mock import Mock

sender = Mock()
sender.send.return_value = "accepted"
service = AlertService(sender)

assert service.alert("hello") == "accepted"
sender.send.assert_called_once_with("hello")
```

### `MagicMock`

`MagicMock` dodatkowo przygotowuje magiczne metody, np. `__len__`, `__iter__`
i `__enter__`. Używaj go, gdy testowana zależność zachowuje się jak lista,
iterator albo context manager.

### `patch`

Patchuj miejsce, w którym kod **odwołuje się** do symbolu, niekoniecznie miejsce,
w którym symbol został pierwotnie zdefiniowany.

```python
@patch("weather_service.requests.get")
def test_weather(mock_get):
    mock_get.return_value.json.return_value = {"temp": 21}
    assert read_temperature("Warsaw") == 21
    mock_get.assert_called_once()
```

```mermaid
sequenceDiagram
    participant T as Test
    participant S as SUT
    participant M as Mock
    T->>M: ustaw return_value / side_effect
    T->>S: wywolaj metode
    S->>M: zaleznosc.method(args)
    M-->>S: odpowiedz lub wyjatek
    T->>M: assert_called_once_with(args)
```

### `side_effect`

Służy do zwracania kolejnych wartości albo rzucania wyjątku:

```python
client.get.side_effect = ["first", TimeoutError("network")]
```

## `monkeypatch` w pytest

`monkeypatch` jest fixture, która po teście przywraca poprzedni stan:

```python
def test_env(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert read_mode() == "test"
```

Można podmienić atrybut, funkcję, zmienną środowiskową albo katalog domowy.
W odróżnieniu od Mocka `monkeypatch` sam nie zapisuje oczekiwań interakcji.

## Zaawansowane techniki Mock

### `side_effect`: sekwencja wartości i wyjątków

```python
client = Mock()
client.get.side_effect = [
    ConnectionError("timeout"),
    ConnectionError("timeout"),
    {"status": "ok"}
]
# Pierwsze dwa wołania rzucą exception, trzecie zwróci slownik
result = client.get()  # ConnectionError
result = client.get()  # ConnectionError
result = client.get()  # {"status": "ok"}
```

### `PropertyMock`: mockowanie właściwości

```python
cache = Mock(spec=CacheManager)
type(cache).size = PropertyMock(return_value=256)

# Teraz cache.size zwroci 256, jak prawdziwa właściwość
assert cache.size == 256
```

### `patch.object`: mockowanie metody konkretnego obiektu

```python
logger = Logger()
processor = DataProcessor(logger)

with patch.object(logger, "log") as mock_log:
    processor.process("data")
    mock_log.assert_called()  # tylko logger.log został zamockowany
```

### `call()`: dokładne sprawdzenie wołań

```python
sender = Mock()
service.notify_users([1, 2, 3], "message")

# Sprawdzenie każdego wołania z argumentami
sender.send.assert_has_calls([
    call(1, "message"),
    call(2, "message"),
    call(3, "message"),
])
```

### `MagicMock`: wspiera magiczne metody

```python
cache = MagicMock()
cache.__len__.return_value = 5
cache.__enter__.return_value.read.return_value = "data"

# Teraz cache wspiera: len(), with, iteracja itp.
assert len(cache) == 5
with cache as ctx:
    print(ctx.read())  # "data"
```

### `reset_mock()`: wyczyszczenie historii wołań

```python
mock = Mock()
mock.method()
assert mock.method.call_count == 1

mock.reset_mock()
assert mock.method.call_count == 0  # historia wyczyszczona
```

## Przykłady zaawansowane

Pełne przykłady zaawansowanych technik znajdują się w [advanced_mocks.py](examples/advanced_mocks.py)
z testami w [test_advanced_mocks.py](examples/test_advanced_mocks.py).

Obejmują:
- Retry logic z `side_effect`
- Iterator i context manager protocol w `MagicMock`
- `spec` do ochrony przed literówkami
- `PropertyMock` dla read-only właściwości
- `patch.object` dla konkretnych instancji
- `call()` matching dla wielokrotnych wołań
- `reset_mock()` do ponownego użytku mock obiektu

## Zadania

1. Zastąp ręcznego Spy obiektem `Mock` i użyj `assert_called_once_with`.
2. Użyj `side_effect` do zasymulowania timeoutu klienta.
3. Podmień `os.environ` przez `monkeypatch` i napisz test dwóch trybów pracy.
4. Napisz test, w którym wynik jest sprawdzany jako return value, a osobno test
   tej samej klasy sprawdzający interakcję.
5. Zidentyfikuj test, w którym Mock jest zbyt szczegółowy i zaproponuj Fake.

**Podpowiedzi:**

- `Mock(spec=Notifier)` odrzuca literówki w API,
- `assert_called_once_with` sprawdza zarówno liczbę, jak i argumenty,
- po `monkeypatch.setattr` nie trzeba ręcznie przywracać oryginału,
- `patch.object(instance, "method")` jest przydatne dla pojedynczego obiektu.

## Uruchomienie i debugowanie

```bash
python -m pytest src/03-test_double/02-verification-and-tools -v
python src/03-test_double/02-verification-and-tools/examples/mock_tools.py
```

Breakpoint ustaw w metodzie SUT przed wywołaniem zależności i obejrzyj
`mock_calls`, `call_args` oraz `return_value`.

## Pytania kontrolne

1. Jaka jest różnica między asercją stanu i interakcji?
2. Kiedy `Mock` jest lepszy od Spy?
3. Dlaczego `patch` w złym miejscu może nie zadziałać?
4. Czym różni się `side_effect` od `return_value`?
5. Czy `monkeypatch` jest Mockiem? Uzasadnij.

## Literatura

- Python Docs - `Mock`: <https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock>
- Python Docs - `patch`: <https://docs.python.org/3/library/unittest.mock.html#patch>
- pytest Docs - `monkeypatch`: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>
