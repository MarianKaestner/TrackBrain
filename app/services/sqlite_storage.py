import sqlite3
from pathlib import Path
from typing import List, Tuple

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db.sqlite3"


class Storage:
    """Single sqlite3-backed store mirroring the activity log plus the
    current tracking state (status + elapsed seconds)."""

    def __init__(self, db_path: Path = DB_PATH):
        self._conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                activity TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tracking_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # ---- log -------------------------------------------------------

    def add_log_entry(self, time: str, activity: str) -> None:
        self._conn.execute(
            "INSERT INTO log (time, activity) VALUES (?, ?)", (time, activity)
        )
        self._conn.commit()

    def clear_log(self) -> None:
        self._conn.execute("DELETE FROM log")
        self._conn.commit()

    def get_log_entries(self) -> List[Tuple[str, str]]:
        cursor = self._conn.execute("SELECT time, activity FROM log ORDER BY id ASC")
        return cursor.fetchall()

    # ---- tracking state ---------------------------------------------

    def save_state(self, status: str, elapsed_seconds: float) -> None:
        self._conn.executemany(
            """
            INSERT INTO tracking_state (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            [("status", status), ("elapsed_seconds", str(elapsed_seconds))],
        )
        self._conn.commit()

    def load_state(self) -> Tuple[str, float]:
        cursor = self._conn.execute("SELECT key, value FROM tracking_state")
        data = dict(cursor.fetchall())
        status = data.get("status", "idle")
        elapsed_seconds = float(data.get("elapsed_seconds", 0.0))
        return status, elapsed_seconds

    def close(self) -> None:
        self._conn.close()
