"""User Memory — SQLite-based persistent storage for user preferences."""

from __future__ import annotations

import os
import sqlite3
from typing import Optional


class UserMemory:
    """Long-term memory store using SQLite for user preferences.

    Remembers settings across sessions such as default GitHub repo,
    preferred standup format, working hours, etc.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(__file__))
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "user_prefs.db")

        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        """Store or update a preference."""
        self.conn.execute(
            "INSERT OR REPLACE INTO preferences (key, value, updated_at) "
            "VALUES (?, ?, CURRENT_TIMESTAMP)",
            (key, value),
        )
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        """Retrieve a preference by key."""
        row = self.conn.execute(
            "SELECT value FROM preferences WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def delete(self, key: str) -> bool:
        """Delete a preference. Returns True if it existed."""
        cursor = self.conn.execute(
            "DELETE FROM preferences WHERE key = ?", (key,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_all(self) -> dict[str, str]:
        """Get all stored preferences."""
        rows = self.conn.execute("SELECT key, value FROM preferences").fetchall()
        return dict(rows)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
