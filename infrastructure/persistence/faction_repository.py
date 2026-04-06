from domain import Faction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class FactionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("CREATE INDEX IF NOT EXISTS idx_factions_name ON factions(name)")
        await self.execute("PRAGMA journal_mode=WAL;")
    
    # ---------- Queries ----------

    async def get_by_id(self, faction_id: int) -> Optional[Faction]:
        row = await self.fetchrow(
            "SELECT * FROM factions WHERE faction_id = ?", (faction_id,)
        )
        return Faction(data=dict(row)) if row else None
        
    async def get_by_owner_id(self, owner_id: int, server_id: int) -> Optional[Faction]:
        row = await self.fetchrow(
            "SELECT * FROM factions WHERE owner_id = ? AND server_id = ?", (owner_id, server_id)
        )
        return Faction(data=dict(row)) if row else None

    async def get_all(self, server_id: int = None) -> List[Faction]:
        if server_id is not None:
            rows = await self.fetch("SELECT * FROM factions WHERE server_id = ?", (server_id,))
        else:
            rows = await self.fetch("SELECT * FROM factions")
        return [Faction(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, faction: Faction) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO factions (
                server_id, owner_id, name, description, color
            )

                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(faction_id) DO NOTHING
            """, (
                faction.server_id,
                faction.owner_id,
                faction.name,
                faction.description,
                faction.color
            ))
        return (last_id > 0, last_id)

    async def update(self, faction: Faction) -> bool:
        last_id = await self.update("""
            UPDATE factions
            SET server_id = ?, owner_id = ?, name = ?, description = ?, color = ?
            WHERE faction_id = ?
            """, (
                faction.server_id,
                faction.owner_id,
                faction.name,
                faction.description,
                faction.color,
                faction.faction_id
            ))

        return last_id > 0

    async def delete(self, faction: Faction) -> bool:
        last_id = await self.delete(
            "DELETE FROM factions WHERE faction_id = ?",
            (faction.faction_id,)
        )
        return last_id > 0

    async def delete_all(self, server_id: int) -> int:
        last_id = await self.delete(
            "DELETE FROM factions WHERE server_id = ?",
            (server_id,)
        )
        return last_id

    async def exists(self, faction_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM factions WHERE faction_id = ?", (faction_id,)
        )
        return row is not None

    async def exists_by_owner_id(self, owner_id: int, server_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM factions WHERE owner_id = ? AND server_id = ?", (owner_id, server_id)
        )
        return row is not None