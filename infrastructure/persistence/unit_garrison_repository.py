from domain import UnitGarrison
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitGarrisonRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS unit_garrisons (
                    garrison_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    poi_id INTEGER NOT NULL,
                    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                    FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, garrison_id: int) -> Optional[UnitGarrison]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM unit_garrisons WHERE garrison_id = ?", (garrison_id,)
            )
            row = c.fetchone()
            return UnitGarrison(data=dict(row)) if row else None

    def get_all(self) -> List[UnitGarrison]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM unit_garrisons")
            return [UnitGarrison(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, garrison: UnitGarrison) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO unit_garrisons (
                    unit_id, poi_id, assigned_at
                )
                VALUES (?, ?, ?)
            """, (
                garrison.unit_id,
                garrison.poi_id,
                garrison.assigned_at
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, garrison: UnitGarrison) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE unit_garrisons
                SET unit_id = ?, poi_id = ?, assigned_at = ?
                WHERE garrison_id = ?
            """, (
                garrison.unit_id,
                garrison.poi_id,
                garrison.assigned_at,
                garrison.garrison_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, garrison: UnitGarrison) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM unit_garrisons WHERE garrison_id = ?",
                (garrison.garrison_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, garrison_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM unit_garrisons WHERE garrison_id = ?",
                (garrison_id,)
            )
            return c.fetchone() is not None