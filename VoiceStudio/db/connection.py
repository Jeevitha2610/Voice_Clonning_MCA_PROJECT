"""Thread-safe SQLite database connection manager with WAL mode."""

from pathlib import Path
import sqlite3
from typing import Optional

from VoiceStudio.exceptions import DatabaseError


class DatabaseManager:
    """Manages SQLite database connections with Write-Ahead Logging (WAL) enabled."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_pragmas()

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a new SQLite connection with foreign keys and dict rows."""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to connect to database at {self.db_path}: {exc}") from exc

    def _init_pragmas(self) -> None:
        """Initialize Write-Ahead Logging (WAL) and synchronous pragmas."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
                conn.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to configure database pragmas: {exc}") from exc
