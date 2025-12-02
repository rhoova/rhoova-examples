
"""Controller layer for alert operations.

Provides an abstraction between UI and service layer so that UI
doesn't directly depend on database/repository details.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

# Service layer dependency
from services.repository import AlertRepository

_repo = AlertRepository()

# ------------------------------------------------------------------ #
def log_alert(*, timestamp: str, tenor: str, change1d: float,
              previous_pv: float, last_pv: float, message: str) -> None:
    """Proxy to repository log_alert."""
    _repo.log_alert(
        timestamp=timestamp,
        tenor=tenor,
        change1d=change1d,
        previous_pv=previous_pv,
        last_pv=last_pv,
        message=message,
    )

# ------------------------------------------------------------------ #
def get_alert_log_csv(limit: int = 100) -> str:
    """Return recent alerts as CSV string."""
    return _repo.get_alert_log_csv(limit=limit)

# ------------------------------------------------------------------ #
def to_dataframe(limit: int = 500) -> pd.DataFrame:
    """Return recent alerts as pandas DataFrame."""
    return _repo.to_dataframe(limit=limit)
