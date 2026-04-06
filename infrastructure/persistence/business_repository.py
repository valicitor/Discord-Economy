from domain import Business
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BusinessRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    business_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    owner_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    location TEXT,
                    range INTEGER,
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, business_id: int) -> Optional[Business]:
        row = await self.fetchrow(
            "SELECT * FROM businesses WHERE business_id = ?", (business_id,)
        )
        return Business(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Business]:
        row = await self.fetchrow(
            "SELECT * FROM businesses WHERE name = ? AND server_id = ?", (name, server_id)
        )
        return Business(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Business]:
        rows = await self.fetch("SELECT * FROM businesses WHERE server_id = ?", (server_id,))
        return [Business(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, business: Business) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO businesses (
                server_id, owner_id, name, description, type, location, range, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            business.server_id,
            business.owner_id,
            business.name,
            business.description,
            business.type,
            business.location,
            business.range,
            str(business.metadata)
        ))

        return (last_id > 0, last_id)
    
    async def update(self, business: Business) -> bool:
        rowcount = await self.update("""
            UPDATE businesses
            SET server_id = ?, owner_id = ?, name = ?, description = ?, type = ?, location = ?, range = ?, metadata = ?
                WHERE business_id = ?
            """, (
                business.server_id,
                business.owner_id,
                business.name,
                business.description,
                business.type,
                business.location,
                business.range,
                str(business.metadata),
                business.business_id
            ))

        return rowcount > 0

    async def delete(self, business: Business) -> bool:
        rowcount = await self.delete(
            "DELETE FROM businesses WHERE business_id = ?",
            (business.business_id,)
        )
        return rowcount > 0
    
    async def delete_all(self, server_id: int) -> bool:
        rowcount = await self.delete("DELETE FROM businesses WHERE server_id = ?", (server_id,))
        return rowcount > 0

    async def exists(self, business_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM businesses WHERE business_id = ?",
            (business_id,)
        )
        return row is not None