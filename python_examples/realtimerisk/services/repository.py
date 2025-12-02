from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Tuple
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "alert_log.db"


class AlertRepository:
    """Lightweight wrapper around SQLite for alert CRUD operations."""

    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                tenor TEXT,
                change1d REAL,
                previous_pv REAL,
                last_pv REAL,
                message TEXT
            )
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    def add(self, ts: str, tenor: str, change1d: float, previous_pv: float, last_pv: float, message: str) -> None:
        """Insert a new alert row."""
        self.conn.execute(
            """INSERT INTO alerts (ts, tenor, change1d, previous_pv, last_pv, message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (ts, tenor, change1d, previous_pv, last_pv, message),
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    def fetch_recent(self, limit: int = 100) -> List[Tuple]:
        cur = self.conn.execute(
            "SELECT ts, tenor, change1d, previous_pv, last_pv, message "
            "FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    # ------------------------------------------------------------------ #
    def to_dataframe(self, limit: int = 100):
        rows = self.fetch_recent(limit)
        return pd.DataFrame(
            rows,
            columns=["timestamp", "tenor", "change1d", "previous_pv", "last_pv", "message"],
        )

    # ------------------------------------------------------------------ #
    def log_alert(self, timestamp: str, tenor: str, change1d: float, previous_pv: float, last_pv: float, message: str) -> None:
        self.add(timestamp, tenor, change1d, previous_pv, last_pv, message)

    # ------------------------------------------------------------------ #
    def get_alert_log_csv(self, limit: int = 100) -> str:
        df = self.to_dataframe(limit)
        return df.to_csv(index=False)
