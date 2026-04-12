from domain import Faction, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class FactionRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the factions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS factions (
                faction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                owner_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                FOREIGN KEY(owner_id) REFERENCES players(player_id),
                UNIQUE(name, server_id)
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_factions_name ON factions(name)")

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the factions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS factions")

    async def clear_all(self) -> bool:
        """
        Clears all data from the factions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM factions"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "factions")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, faction_id: int) -> Optional[Faction]:
        row = await super().fetchrow(
            "SELECT * FROM factions WHERE faction_id = ?",
            faction_id
        )
        return Faction(data=dict(row)) if row else None

    async def get_all(self, server_id: int|None = None) -> List[Faction]:
        if server_id is not None:
            rows = await super().fetch("SELECT * FROM factions WHERE server_id = ?", server_id)
        else:
            rows = await super().fetch("SELECT * FROM factions")
        return [Faction(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_owner_id(self, owner_id: int, server_id: int) -> Optional[Faction]:
        row = await super().fetchrow(
            "SELECT * FROM factions WHERE owner_id = ? AND server_id = ?", 
            owner_id,
            server_id
        )
        return Faction(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, faction_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM factions WHERE faction_id = ?",
            faction_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_owner_id(self, owner_id: int, server_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM factions WHERE owner_id = ? AND server_id = ?", 
            owner_id, 
            server_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, faction: Faction) -> int:
        return await super().insert(
            "INSERT INTO factions (server_id, owner_id, name, description, color) VALUES (?, ?, ?, ?, ?)",
            faction.server_id,
            faction.owner_id,
            faction.name,
            faction.description,
            faction.color
        )
    
    async def update(self, faction: Faction) -> bool:
        affected = await super().update(
            "UPDATE factions SET server_id = ?, owner_id = ?, name = ?, description = ?, color = ? WHERE faction_id = ?",
            faction.server_id,
            faction.owner_id,
            faction.name,
            faction.description,
            faction.color,
            faction.faction_id
        )
        return affected > 0

    async def delete(self, faction: Faction) -> bool:
        affected = await super().delete(
            "DELETE FROM factions WHERE faction_id = ?",
            faction.faction_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM factions WHERE server_id = ?",
            server_id
        )
        return affected > 0