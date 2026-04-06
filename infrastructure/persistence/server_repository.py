from domain import Server
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ServerRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    server_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, server_id: int) -> Optional[Server]:
        query = "SELECT * FROM servers WHERE server_id = ?"
        params = (server_id,)
        row = await self.fetchrow(query, params)
        return Server(data=dict(row)) if row else None
    
    async def get_by_guild_id(self, guild_id: int) -> Optional[Server]:
        query = "SELECT * FROM servers WHERE guild_id = ?"
        params = (guild_id,)
        row = await self.fetchrow(query, params)
        return Server(data=dict(row)) if row else None

    async def get_all(self) -> List[Server]:
        query = "SELECT * FROM servers"
        rows = await self.fetch(query)
        return [Server(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, server: Server) -> tuple[bool, int]:
        query = """
            INSERT INTO servers (
                guild_id, name
            )
            VALUES (?, ?)
        """
        params = (
            server.guild_id,
            server.name
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, server: Server) -> bool:
        query = """
            UPDATE servers
            SET name = ?
            WHERE server_id = ?
        """
        params = (
            server.name,
            server.server_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, server: Server) -> bool:
        query = "DELETE FROM servers WHERE server_id = ?"
        params = (server.server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, server_id: int) -> bool:
        query = "SELECT 1 FROM servers WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0
    
    async def exists_by_guild_id(self, guild_id: int) -> bool:
        query = "SELECT 1 FROM servers WHERE guild_id = ?"
        params = (guild_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0