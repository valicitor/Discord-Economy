from domain import RaceStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "static_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS race_stats (
                    race_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(race_id) REFERENCES races(race_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, race_stat_id: int) -> Optional[RaceStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM race_stats WHERE race_stat_id = ?", (race_stat_id,)
            )
            row = c.fetchone()
            return RaceStat(data=dict(row)) if row else None

    def get_all(self) -> List[RaceStat]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM race_stats")
            return [RaceStat(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, race_stat: RaceStat) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO race_stats (
                    race_id, stat_key, stat_value
                )
                VALUES (?, ?, ?)
            """, (
                race_stat.race_id,
                race_stat.stat_key,
                race_stat.stat_value
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, race_stat: RaceStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE race_stats
                SET race_id = ?, stat_key = ?, stat_value = ?
                WHERE race_stat_id = ?
            """, (
                race_stat.race_id,
                race_stat.stat_key,
                race_stat.stat_value,
                race_stat.race_stat_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, race_stat: RaceStat) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM race_stats WHERE race_stat_id = ?",
                (race_stat.race_stat_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM race_stats")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, race_stat_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM race_stats WHERE race_stat_id = ?", (race_stat_id,)
            )
            return c.fetchone() is not None