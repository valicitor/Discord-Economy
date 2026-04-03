from domain import Unit
from domain import IRepository
from domain.models import vehicle
from infrastructure import BaseRepository
from typing import List, Optional


class UnitRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, unit_id: int) -> Optional[Unit]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM units WHERE unit_id = ?", (unit_id,)
            )
            row = c.fetchone()
            return Unit(data=dict(row)) if row else None
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Unit]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM units WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Unit(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Unit]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM units WHERE server_id = ?", (server_id,))
            return [Unit(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, unit: Unit) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO units (
                    server_id, name, description, metadata
                )
                VALUES (?, ?, ?, ?)
            """, (
                unit.server_id,
                unit.name,
                unit.description,
                str(unit.metadata),
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, unit: Unit) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE units
                SET server_id = ?, name = ?, description = ?, metadata = ?
                WHERE unit_id = ?
            """, (
                unit.server_id,
                unit.name,
                unit.description,
                str(unit.metadata),
                unit.unit_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, unit: Unit) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM units WHERE unit_id = ?",
                (unit.unit_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM units WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, unit_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM units WHERE unit_id = ?",
                (unit_id,)
            )
            return c.fetchone() is not None