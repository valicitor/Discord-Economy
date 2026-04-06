from domain import PointOfInterest
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PointOfInterestRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS points_of_interest (
                    poi_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, poi_id: int) -> Optional[PointOfInterest]:
        query = "SELECT * FROM points_of_interest WHERE poi_id = ?"
        params = (poi_id,)
        row = await self.fetchrow(query, params)
        return PointOfInterest(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[PointOfInterest]:
        query = "SELECT * FROM points_of_interest WHERE name = ? AND server_id = ?"
        params = (name, server_id)
        row = await self.fetchrow(query, params)
        return PointOfInterest(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[PointOfInterest]:
        query = "SELECT * FROM points_of_interest WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return [PointOfInterest(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, poi: PointOfInterest) -> tuple[bool, int]:
        query = """
            INSERT INTO points_of_interest (
                server_id, name, icon, size
            )
            VALUES (?, ?, ?, ?)
        """
        params = (
            poi.server_id,
            poi.name,
            poi.icon,
            poi.size
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, poi: PointOfInterest) -> bool:
        query = """
            UPDATE points_of_interest
            SET server_id = ?, name = ?, icon = ?, size = ?
            WHERE poi_id = ?
        """
        params = (
            poi.server_id,
            poi.name,
            poi.icon,
            poi.size,
            poi.poi_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, poi: PointOfInterest) -> bool:
        query = "DELETE FROM points_of_interest WHERE poi_id = ?"
        params = (poi.poi_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> bool:
        query = "DELETE FROM points_of_interest WHERE server_id = ?"
        params = (server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, poi_id: int) -> bool:
        query = "SELECT 1 FROM points_of_interest WHERE poi_id = ?"
        params = (poi_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0