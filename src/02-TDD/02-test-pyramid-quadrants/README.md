# Temat 02 - Piramida testów i kwadranty testów

> Moduł: [02-TDD](../README.md) · Poprzedni: [01-red-green-refactor](../01-red-green-refactor/README.md) · Następny: [03-technical-debt](../03-technical-debt/README.md)

## Cel

Nauczyć się dobierać poziom testu do pytania, na które chcemy odpowiedzieć.
Piramida przypomina o koszcie i szybkości testów, a kwadranty rozszerzają
perspektywę o cel testu: wsparcie zespołu albo ocena produktu oraz perspektywę
technologiczną albo biznesową.

## Piramida testów

![Piramida testów: dużo szybkich testów jednostkowych u podstawy, mniej integracyjnych pośrodku i niewiele testów E2E na szczycie. Testy manualne uzupełniają piramidę.](diagrams/test-pyramid.svg)

```mermaid
flowchart TB
    A["Akceptacyjne / E2E<br/>nieliczne, wolniejsze"]
    I["Integracyjne<br/>umiarkowany koszt"]
    U["Jednostkowe<br/>liczne, szybkie, izolowane"]
    A --> I --> U
    X["Manualne / eksploracyjne"]
    X -. "uzupełniają; nie są poziomem piramidy" .- A

    classDef expensive fill:#ffebee,stroke:#c62828
    classDef medium fill:#fff3e0,stroke:#ef6c00
    classDef cheap fill:#e8f5e9,stroke:#2e7d32
    classDef complementary fill:#e3f2fd,stroke:#1565c0
    class A expensive
    class I medium
    class U cheap
```

Piramida nie oznacza „nigdy nie pisz E2E”. Jej podstawa to wiele szybkich
testów jednostkowych, wyżej znajduje się mniejsza liczba testów integracyjnych,
a na szczycie niewiele wolniejszych testów akceptacyjnych/E2E. Proporcje są
wskazówką, nie uniwersalnym limitem ani wymaganą liczbą testów. Testy manualne
i eksploracyjne uzupełniają automatyzację, ale nie są jej kolejnym poziomem.

Poziom opisuje **zakres uruchamianego systemu**, a nie nazwę testowanej klasy:
test `CatalogService` z `StubCatalog` izoluje regułę jednostkową, natomiast
`CatalogService` z `MemoryCatalog` sprawdza współpracę dwóch komponentów.

### Antywzorce

- **Klepsydra** - dużo testów jednostkowych i E2E, mało integracyjnych.
  Zespół ma luki w sprawdzaniu połączeń między komponentami.
- **Sopel** - prawie same testy E2E/manualne, mało szybkich testów jednostkowych.
  Każda informacja zwrotna jest droga i opóźniona.

```mermaid
flowchart LR
    P["Zdrowa piramida<br/>duzo unit, mniej integration,<br/>malo E2E"]
    H["Klepsydra<br/>unit + E2E, malo integration"]
    S["Sopel<br/>malo unit, duzo kosztownych E2E"]
    P --- H --- S
    classDef healthy fill:#e8f5e9,stroke:#2e7d32
    classDef anti fill:#ffebee,stroke:#c62828
    class P healthy
    class H,S anti
```

## Kwadranty testów

| | Technologiczne | Biznesowe |
|---|---|---|
| **Wspierające zespół** | testy jednostkowe, komponentowe, narzędzia diagnostyczne | przykłady akceptacyjne, testy scenariuszy pomagające doprecyzować wymagania |
| **Sprawdzające produkt** | testy wydajności, bezpieczeństwa, kompatybilności | testy akceptacyjne, E2E, manualne eksploracyjne |

Kwadranty nie są ścisłą klasyfikacją plików. Pomagają zadać pytanie:
„Czy ten test pomaga nam budować produkt, czy przede wszystkim ocenia gotowy
produkt?” oraz „Czy patrzymy przez pryzmat technologii, czy wartości biznesowej?”.

## Jak wybrać poziom?

| Pytanie | Najlepszy pierwszy wybór |
|---|---|
| Czy rabat 10% daje poprawną kwotę? | test jednostkowy funkcji rabatowej |
| Czy koszyk zapisuje się w repozytorium? | test integracyjny serwisu i repozytorium |
| Czy klient może kupić produkt od początku do końca? | test akceptacyjny/E2E |
| Czy interfejs jest wygodny dla użytkownika? | test manualny/eksploracyjny |

Kod i testy w [examples/layered_system.py](examples/layered_system.py) oraz
[examples/test_layered_system.py](examples/test_layered_system.py) pokazują
regułę jednostkową z kontrolowanym Stubem i integrację usługi z katalogiem
w pamięci. Scenariusz akceptacyjny projektujesz w zadaniu 3; przykład celowo
nie nazywa testu w procesie tym samym co test E2E całej aplikacji.

## Zadania

Pliki: [tasks_02.py](exercises/tasks_02.py), [tdd_solutions_02.py](exercises/tdd_solutions_02.py),
[test_tdd_solutions_02.py](exercises/test_tdd_solutions_02.py).

1. Przyporządkuj dziesięć opisów testów do poziomów piramidy.
2. Napisz test integracyjny dla `CatalogService` z `MemoryCatalog`.
3. Zaprojektuj jeden test akceptacyjny dla scenariusza „kup produkt”.
4. Narysuj własną piramidę dla aplikacji webowej i wskaż antywzorzec sopla.

**Podpowiedzi:**

- test jednostkowy nie powinien wymagać pliku ani sieci,
- test integracyjny powinien sprawdzać rzeczywiste połączenie dwóch elementów,
- test akceptacyjny opisuj językiem użytkownika, nie nazwą prywatnej metody.

## Uruchomienie i debugowanie

```bash
python -m pytest src/02-TDD/02-test-pyramid-quadrants -v
python src/02-TDD/02-test-pyramid-quadrants/examples/layered_system.py
```

Ustaw breakpoint w `CatalogService.buy()` i porównaj, które obiekty widzi test
jednostkowy, a które test integracyjny.

## Pytania kontrolne

1. Dlaczego testy jednostkowe powinny stanowić podstawę piramidy?
2. Co jest ryzykiem antywzorca klepsydry?
3. Czym różni się test integracyjny od akceptacyjnego?
4. Do którego kwadrantu należy test wydajności API?
5. Czy test E2E może zastąpić test jednostkowy? Uzasadnij.

## Literatura

- Martin Fowler, *Test Pyramid*: <https://martinfowler.com/bliki/TestPyramid.html>
- Wikipedia, *Software testing*: <https://en.wikipedia.org/wiki/Software_testing>
- Lisa Crispin, Janet Gregory, *Agile Testing*, Addison-Wesley, 2009.
