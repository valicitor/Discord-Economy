from domain import EquipmentStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentStatRepository(IRepository, BaseRepository):
    def __init__(self, db_path: str = None):
        super().__init__(db_path or "equipment_stats.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS equipment_stats (
                    equipment_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(equipment_id) REFERENCES equipment(equipment_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, equipment_stat_id: int) -> Optional[EquipmentStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM equipment_stats WHERE equipment_stat_id = ?", (equipment_stat_id,)
            )
            row = c.fetchone()
            return EquipmentStat(data=dict(row)) if row else None

    def get_all(self) -> List[EquipmentStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM equipment_stats")
            return [EquipmentStat(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, equipment_stat: EquipmentStat) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO equipment_stats (
                    equipment_id, stat_key, stat_value
                )
                VALUES (?, ?, ?)
            """, (
                equipment_stat.equipment_id,
                equipment_stat.stat_key,
                equipment_stat.stat_value
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, equipment_stat: EquipmentStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE equipment_stats
                SET equipment_id = ?, stat_key = ?, stat_value = ?
                WHERE equipment_stat_id = ?
            """, (
                equipment_stat.equipment_id,
                equipment_stat.stat_key,
                equipment_stat.stat_value,
                equipment_stat.equipment_stat_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, equipment_stat: EquipmentStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM equipment_stats WHERE equipment_stat_id = ?",
                (equipment_stat.equipment_stat_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM equipment_stats")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, equipment_stat_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM equipment_stats WHERE equipment_stat_id = ?",
                (equipment_stat_id,)
            )
            return c.fetchone() is not None