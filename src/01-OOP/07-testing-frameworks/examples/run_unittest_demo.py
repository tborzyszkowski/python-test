"""Jak uruchamiać testy: cztery sposoby na tym samym zestawie testów.

Uruchomienie::

    python src/01-OOP/07-testing-frameworks/examples/run_unittest_demo.py

Skrypt pokazuje, że:

1. ``unittest`` jest **wbudowany** - nie wymaga instalacji i ma własny runner,
2. ``unittest`` potrafi uruchamiać testy z pojedynczej klasy/metody,
3. ``unittest`` umie **odkrywać** testy w katalogu (``discover``),
4. ``pytest`` potrafi uruchamiać **te same** testy ``unittest`` (i odwrotnie:
   ``python -m unittest`` uruchomi funkcje ``test_*``? Nie - to działa tylko
   w jedną stronę, co też zobaczymy na wydruku).

Wszystkie komendy można skopiować do terminala - skrypt wypisuje je w formie
gotowej do wklejenia.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNITTEST_MODULE = "test_unittest_calculator"
PYTEST_MODULE = "test_pytest_calculator"


def header(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def demo_in_process_runner() -> None:
    """Sposób 1: uruchomienie wybranej klasy w tym samym procesie."""
    header("1. Runner w procesie: tylko jedna klasa testowa")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f"{UNITTEST_MODULE}.TestCalculatorArithmetic")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(f"-> uruchomiono {result.testsRun}, błędów: {len(result.errors)}, "
          f"porażek: {len(result.failures)}")


def demo_single_test_method() -> None:
    """Sposób 2: pojedyncza metoda testowa (najszybsza pętla pracy)."""
    header("2. Runner w procesie: pojedynczy test")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(
        f"{UNITTEST_MODULE}.TestCalculatorArithmetic.test_divide_by_zero_message_explains_the_reason"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"-> testsRun = {result.testsRun}")


def demo_discovery() -> None:
    """Sposób 3: automatyczne odkrycie wszystkich testów w katalogu."""
    header("3. Discovery: znajdź wszystkie testy 'test_unittest_*.py' w katalogu")
    loader = unittest.TestLoader()
    pattern = f"{UNITTEST_MODULE}.py"        # wzorzec wskazuje JEDEN plik
    suite = loader.discover(start_dir=str(HERE), pattern=pattern)
    print(f"znalezione moduły wg wzorca {pattern!r}: {suite.countTestCases()} testów")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(f"-> uruchomiono {result.testsRun}, porażek: {len(result.failures)}")


def demo_pytest_on_unittest() -> None:
    """Sposób 4: pytest uruchamia klasy ``unittest.TestCase`` bez zmian."""
    header("4. pytest na tych samych testach unittest (podproces)")
    command = [
        sys.executable, "-m", "pytest", str(HERE / f"{UNITTEST_MODULE}.py"), "-q",
    ]
    print("komenda:", " ".join(command))
    completed = subprocess.run(command, capture_output=True, text=True, cwd=HERE)
    print(completed.stdout.strip() or completed.stderr.strip())
    print("exit code:", completed.returncode)


def demo_reverse_direction() -> None:
    """Kierunek odwrotny: unittest NIE znajdzie testów w stylu pytest."""
    header("5. Kierunek odwrotny: python -m unittest a plik w stylu pytest")
    command = [
        sys.executable, "-m", "unittest", PYTEST_MODULE, "-v",
    ]
    print("komenda:", " ".join(command))
    completed = subprocess.run(command, capture_output=True, text=True, cwd=HERE)
    output = (completed.stderr or completed.stdout).strip().splitlines()
    print("ostatnia linia:", output[-1] if output else "(brak wyjścia)")
    print()
    print("Wniosek: klasy ``unittest.TestCase`` są zrozumiałe dla obu frameworków,")
    print("a zwykłe funkcje ``test_*`` rozumie tylko pytest. Dlatego migracja")
    print("z unittest do pytest jest stopniowa i bezpieczna: można mieć jedno i drugie.")


def print_cheatsheet() -> None:
    header("Ściągawka: jak uruchamiać testy")
    print("""  # unittest, jeden plik
  python -m unittest src/01-OOP/07-testing-frameworks/examples/test_unittest_calculator.py -v

  # unittest, cały katalog (discover)
  python -m unittest discover -s src/01-OOP/07-testing-frameworks/examples -v

  # unittest, pojedynczy test
  python -m unittest test_unittest_calculator.TestCalculatorArithmetic.test_add_returns_sum

  # pytest, wybrany plik
  python -m pytest src/01-OOP/07-testing-frameworks/examples/test_pytest_calculator.py -v

  # pytest, filtr po nazwie (bez podawania klasy)
  python -m pytest src/01-OOP/07-testing-frameworks -k "divide" -v

  # pytest, oba pliki naraz (unittest + pytest w jednym przebiegu!)
  python -m pytest src/01-OOP/07-testing-frameworks/examples -v""")
    print()
    print("Konwencja nazw plików:")
    print("  unittest: 'test*.py'  (np. test_unittest_calculator.py)")
    print("  pytest  : 'test_*.py' lub '*_test.py'")
    print("Oba wzorce pokrywają się dla 'test_*.py' - dlatego taka nazwa jest najbezpieczniejsza.")


def main() -> None:
    demo_in_process_runner()
    demo_single_test_method()
    demo_discovery()
    demo_pytest_on_unittest()
    demo_reverse_direction()
    print_cheatsheet()


if __name__ == "__main__":
    main()
