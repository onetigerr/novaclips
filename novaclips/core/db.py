import sqlite3
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

DB_PATH = Path("data/db/novaclips.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with schema if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())
            logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor."""
        with self.get_connection() as conn:
            return conn.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
