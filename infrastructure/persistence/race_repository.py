from domain import Race
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS races (
                    race_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, race_id: int) -> Optional[Race]:
        query = "SELECT * FROM races WHERE race_id = ?"
        params = (race_id,)
        row = await self.fetchrow(query, params)
        return Race(data=dict(row)) if row else None
    
        
    async def get_by_name(self, name: str, server_id: int) -> Optional[Race]:
        query = "SELECT * FROM races WHERE name = ? AND server_id = ?"
        params = (name, server_id)
        row = await self.fetchrow(query, params)
        return Race(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Race]:
        query = "SELECT * FROM races WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return [Race(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, race: Race) -> tuple[bool, int]:
        query = """
            INSERT INTO races (
                server_id, name, description, metadata
            )
            VALUES (?, ?, ?, ?)
        """
        params = (
            race.server_id,
            race.name,
            race.description,
            str(race.metadata)
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, race: Race) -> bool:
        query = """
            UPDATE races
            SET server_id = ?, name = ?, description = ?, metadata = ?
            WHERE race_id = ?
        """
        params = (
            race.server_id,
            race.name,
            race.description,
            str(race.metadata),
            race.race_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, race: Race) -> bool:
        query = "DELETE FROM races WHERE race_id = ?"
        params = (race.race_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> bool:
        query = "DELETE FROM races WHERE server_id = ?"
        params = (server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, race_id: int) -> bool:
        query = "SELECT 1 FROM races WHERE race_id = ?"
        params = (race_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0