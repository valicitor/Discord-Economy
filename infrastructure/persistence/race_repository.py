from domain import Race
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS races (
                    race_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, race_id: int) -> Optional[Race]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM races WHERE race_id = ?", (race_id,)
            )
            row = c.fetchone()
            return Race(data=dict(row)) if row else None
    
        
    def get_by_name(self, name: str, server_id: int) -> Optional[Race]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM races WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Race(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Race]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM races WHERE server_id = ?", (server_id,))
            return [Race(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, race: Race) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO races (
                    server_id, name, description, metadata
                )
                VALUES (?, ?, ?, ?)
            """, (
                race.server_id,
                race.name,
                race.description,
                str(race.metadata)
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, race: Race) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE races
                SET server_id = ?, name = ?, description = ?, metadata = ?
                WHERE race_id = ?
            """, (
                race.server_id,
                race.name,
                race.description,
                str(race.metadata),
                race.race_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, race: Race) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM races WHERE race_id = ?",
                (race.race_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM races WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, race_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM races WHERE race_id = ?",
                (race_id,)
            )
            return c.fetchone() is not None