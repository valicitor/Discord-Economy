from domain import UnitStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "static_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS unit_stats (
                    unit_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, unit_stat_id: int) -> Optional[UnitStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM unit_stats WHERE unit_stat_id = ?", (unit_stat_id,)
            )
            row = c.fetchone()
            return UnitStat(data=dict(row)) if row else None

    def get_all(self) -> List[UnitStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM unit_stats")
            return [UnitStat(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, unit_stat: UnitStat) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO unit_stats (
                    unit_id, stat_key, stat_value
                )
                VALUES (?, ?, ?)
            """, (
                unit_stat.unit_id,
                unit_stat.stat_key,
                unit_stat.stat_value
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, unit_stat: UnitStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE unit_stats
                SET unit_id = ?, stat_key = ?, stat_value = ?
                WHERE unit_stat_id = ?
            """, (
                unit_stat.unit_id,
                unit_stat.stat_key,
                unit_stat.stat_value,
                unit_stat.unit_stat_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, unit_stat: UnitStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM unit_stats WHERE unit_stat_id = ?",
                (unit_stat.unit_stat_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM unit_stats")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, unit_stat_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM unit_stats WHERE unit_stat_id = ?", (unit_stat_id,)
            )
            return c.fetchone() is not None