"""Central place for alert-threshold management.

This module abstracts reading & writing tenor‑specific
thresholds to a JSON file (``thresholds.json`` at project root).
Other modules should import :data:`DEFAULT_THRESHOLDS` for
read‑only access or use :func:`save_thresholds` to persist
updates coming from the UI (e.g. Streamlit sidebar sliders).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

_JSON_PATH = Path(__file__).resolve().parents[1] / "thresholds.json"

# ---------------------------------------------------------------------------
# Default fallback values (bp) in case JSON file does not yet exist.
# ---------------------------------------------------------------------------
_FALLBACK: Dict[str, int] = {
    "1W": 0,
    "2W": 0,
    "3W": 0,
    "1M": 0,
    "2M": 0,
    "3M": 0,
    "6M": 0,
    "9M": 0,
    "1Y": 0,
    "18M": 0,
    "2Y": 0,
    "3Y": 0,
    "4Y": 0,
    "5Y": 0,
    "6Y": 0,
    "7Y": 0,
    "8Y": 0,
    "9Y": 0,
    "10Y": 0,
}

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def load_thresholds() -> Dict[str, int]:
    """Return thresholds dict, falling back to :data:`_FALLBACK`."""
    try:
        with _JSON_PATH.open("r", encoding="utf‑8") as fp:
            data: Dict[str, int] = json.load(fp)
            return {k: int(v) for k, v in data.items()}
    except FileNotFoundError:
        # Persist fallback so file exists next time.
        save_thresholds(_FALLBACK)
        return _FALLBACK.copy()
    except Exception:  # malformed or permission error
        return _FALLBACK.copy()


def save_thresholds(thresholds: Dict[str, int]) -> None:
    """Write *thresholds* mapping to JSON file."""
    try:
        with _JSON_PATH.open("w", encoding="utf‑8") as fp:
            json.dump(thresholds, fp, indent=2)
    except Exception:
        # Silently ignore write errors; UI can warn separately if needed.
        pass


# Materialize singleton for import convenience.
DEFAULT_THRESHOLDS: Dict[str, int] = load_thresholds()
