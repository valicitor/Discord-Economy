from domain import Race
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS races (
                    race_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    metadata TEXT
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, race_id: int) -> Optional[Race]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM races WHERE race_id = ?", (race_id,)
            )
            row = c.fetchone()
            return Race(data=dict(row)) if row else None
    
        
    def get_by_name(self, name: str) -> Optional[Race]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM races WHERE name = ?", (name,)
            )
            row = c.fetchone()
            return Race(data=dict(row)) if row else None

    def get_all(self) -> List[Race]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM races")
            return [Race(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, race: Race) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO races (
                    name, description, metadata
                )
                VALUES (?, ?, ?)
            """, (
                race.name,
                race.description,
                str(race.metadata)
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, race: Race) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE races
                SET name = ?, description = ?, metadata = ?
                WHERE race_id = ?
            """, (
                race.name,
                race.description,
                str(race.metadata),
                race.race_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, race: Race) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM races WHERE race_id = ?",
                (race.race_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM races")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, race_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM races WHERE race_id = ?",
                (race_id,)
            )
            return c.fetchone() is not None