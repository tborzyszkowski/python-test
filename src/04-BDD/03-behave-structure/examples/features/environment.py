"""Hooki i konfiguracja przykładowego projektu Behave."""

import sys
from pathlib import Path

EXAMPLES_ROOT = Path(__file__).resolve().parents[1]
if str(EXAMPLES_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_ROOT))


def before_scenario(context, scenario):
    """Tworzy pusty kontekst izolowany dla każdego scenariusza."""
    context.flight = None
    context.passengers = {}
    context.error = None
    context.hook_events = ["before_scenario"]


def after_scenario(context, scenario):
    """Rejestruje zakończenie scenariusza; tutaj można sprzątać zasoby."""
    context.hook_events.append(f"after_scenario:{scenario.status}")
