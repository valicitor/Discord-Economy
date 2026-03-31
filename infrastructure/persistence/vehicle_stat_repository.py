from domain import VehicleStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class VehicleStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "static_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_stats (
                    vehicle_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, vehicle_stat_id: int) -> Optional[VehicleStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM vehicle_stats WHERE vehicle_stat_id = ?", (vehicle_stat_id,)
            )
            row = c.fetchone()
            return VehicleStat(data=dict(row)) if row else None

    def get_all(self) -> List[VehicleStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM vehicle_stats")
            return [VehicleStat(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, vehicle_stat: VehicleStat) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO vehicle_stats (
                    vehicle_id, stat_key, stat_value
                )
                VALUES (?, ?, ?)
            """, (
                vehicle_stat.vehicle_id,
                vehicle_stat.stat_key,
                vehicle_stat.stat_value
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, vehicle_stat: VehicleStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE vehicle_stats
                SET vehicle_id = ?, stat_key = ?, stat_value = ?
                WHERE vehicle_stat_id = ?
            """, (
                vehicle_stat.vehicle_id,
                vehicle_stat.stat_key,
                vehicle_stat.stat_value,
                vehicle_stat.vehicle_stat_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, vehicle_stat: VehicleStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM vehicle_stats WHERE vehicle_stat_id = ?",
                (vehicle_stat.vehicle_stat_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM vehicle_stats")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, vehicle_stat_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM vehicle_stats WHERE vehicle_stat_id = ?",
                (vehicle_stat_id,)
            )
            return c.fetchone() is not None