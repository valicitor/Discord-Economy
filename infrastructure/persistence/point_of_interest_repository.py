from domain import PointOfInterest
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PointOfInterestRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS points_of_interest (
                    poi_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    owner_player_id INTEGER,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    FOREIGN KEY(owner_player_id) REFERENCES players(player_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, poi_id: int) -> Optional[PointOfInterest]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM points_of_interest WHERE poi_id = ?", (poi_id,)
            )
            row = c.fetchone()
            return PointOfInterest(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[PointOfInterest]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM points_of_interest WHERE server_id = ?", (server_id,))
            return [PointOfInterest(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, poi: PointOfInterest) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO points_of_interest (
                    server_id, name, type, x, y, owner_player_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                poi.server_id,
                poi.name,
                poi.type,
                poi.x,
                poi.y,
                poi.owner_player_id
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, poi: PointOfInterest) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE points_of_interest
                SET server_id = ?, name = ?, type = ?, x = ?, y = ?, owner_player_id = ?
                WHERE poi_id = ?
            """, (
                poi.server_id,
                poi.name,
                poi.type,
                poi.x,
                poi.y,
                poi.owner_player_id,
                poi.poi_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, poi: PointOfInterest) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM points_of_interest WHERE poi_id = ?",
                (poi.poi_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM points_of_interest WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, poi_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM points_of_interest WHERE poi_id = ?",
                (poi_id,)
            )
            return c.fetchone() is not None