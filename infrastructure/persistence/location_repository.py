from domain import Location
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class LocationRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    poi_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    owner_player_id INTEGER,
                    FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id),
                    FOREIGN KEY(owner_player_id) REFERENCES players(player_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, location_id: int) -> Optional[Location]:
        row = await self.fetchrow(
            "SELECT * FROM locations WHERE location_id = ?", (location_id,)
        )
        return Location(data=dict(row)) if row else None

    async def get_all(self, poi_id: int|None = None) -> List[Location]:
        if poi_id is not None:
            rows = await self.fetch("SELECT * FROM locations WHERE poi_id = ?", (poi_id,))
        else:
            rows = await self.fetch("SELECT * FROM locations")

        return [Location(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, location: Location) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO locations (
                poi_id, name, type, x, y, owner_player_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                location.poi_id,
                location.name,
                location.type,
                location.x,
                location.y,
                location.owner_player_id
            ))

        return (last_id > 0, last_id)

    async def update(self, location: Location) -> bool:
        last_id = await self.update("""
            UPDATE locations
            SET poi_id = ?, name = ?, type = ?, x = ?, y = ?, owner_player_id = ?
            WHERE location_id = ?
            """, (
                location.poi_id,
                location.name,
                location.type,
                location.x,
                location.y,
                location.owner_player_id,
                location.location_id
            ))

        return last_id > 0

    async def delete(self, location: Location) -> bool:
        last_id = await self.delete(
            "DELETE FROM locations WHERE location_id = ?",
            (location.location_id,)
        )
        return last_id > 0
    
    async def delete_all(self) -> bool:
        last_id = await self.delete("DELETE FROM locations")
        return last_id > 0

    async def exists(self, location_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM locations WHERE location_id = ?", (location_id,)
        )
        return row is not None