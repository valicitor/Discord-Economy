from domain import Unit
from domain import IRepository
from domain.models import vehicle
from infrastructure import BaseRepository
from typing import List, Optional


class UnitRepository(IRepository, BaseRepository):
    def __init__(self, db_path: str = None):
        super().__init__(db_path or "unit.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    metadata TEXT
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, unit_id: int) -> Optional[Unit]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM units WHERE unit_id = ?", (unit_id,)
            )
            row = c.fetchone()
            return Unit(data=dict(row)) if row else None

    def get_all(self) -> List[Unit]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM units")
            return [Unit(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, unit: Unit) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO units (
                    name, description, metadata
                )
                VALUES (?, ?, ?)
            """, (
                unit.name,
                unit.description,
                str(unit.metadata),
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, unit: Unit) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE units
                SET name = ?, description = ?, metadata = ?
                WHERE unit_id = ?
            """, (
                unit.name,
                unit.description,
                str(unit.metadata),
                unit.unit_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, unit: Unit) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM units WHERE unit_id = ?",
                (unit.unit_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM units")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, unit_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM units WHERE unit_id = ?",
                (unit_id,)
            )
            return c.fetchone() is not None