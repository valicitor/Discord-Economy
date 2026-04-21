import json

from domain import Business, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class BusinessRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
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

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the businesses table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS businesses")

    async def clear_all(self) -> bool:
        """
        Clears all data from the businesses table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM businesses"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "businesses")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, business_id: int) -> Optional[Business]:
        row = await super().fetchrow(
            "SELECT * FROM businesses WHERE business_id = ?",
            business_id
        )
        return Business(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Business]:
        rows = await super().fetch("SELECT * FROM businesses WHERE server_id = ?", server_id)
        return [Business(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Business]:
        row = await super().fetchrow(
            "SELECT * FROM businesses WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Business(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, business_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM businesses WHERE business_id = ?",
            business_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, business: Business) -> int:
        return await super().insert(
            "INSERT INTO businesses (server_id, owner_id, name, description, type, location, range, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            business.server_id,
            business.owner_id,
            business.name,
            business.description,
            business.type,
            business.location,
            business.range,
            json.dumps(business.metadata)
        )
    
    async def update(self, business: Business) -> bool:
        affected = await super().update(
            "UPDATE businesses SET server_id = ?, owner_id = ?, name = ?, description = ?, type = ?, location = ?, range = ?, metadata = ? WHERE business_id = ?",
            business.server_id,
            business.owner_id,
            business.name,
            business.description,
            business.type,
            business.location,
            business.range,
            json.dumps(business.metadata),
            business.business_id
        )
        return affected > 0

    async def delete(self, business: Business) -> bool:
        affected = await super().delete(
            "DELETE FROM businesses WHERE business_id = ?",
            business.business_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM businesses WHERE server_id = ?",
            server_id
        )
        return affected > 0