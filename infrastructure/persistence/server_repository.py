from typing import List, Optional
from domain import Server, IRepository
from infrastructure import BaseRepository

class ServerRepository(BaseRepository, IRepository):

    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the servers table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                server_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the servers table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS servers")

    async def clear_all(self) -> bool:
        """
        Clears all data from the servers table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM servers"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "servers")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, server_id: int) -> Optional[Server]:
        row = await super().fetchrow(
            "SELECT * FROM servers WHERE server_id = ?",
            server_id
        )
        return Server(data=dict(row)) if row else None

    async def get_all(self) -> List[Server]:
        rows = await super().fetch("SELECT * FROM servers")
        return [Server(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_guild_id(self, guild_id: int) -> Optional[Server]:
        row = await super().fetchrow(
            "SELECT * FROM servers WHERE guild_id = ?",
            guild_id
        )
        return Server(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, server_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM servers WHERE server_id = ?",
            server_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_guild_id(self, guild_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM servers WHERE guild_id = ?",
            guild_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, server: Server) -> int:
        return await super().insert(
            "INSERT INTO servers (guild_id, name) VALUES (?, ?)",
            server.guild_id,
            server.name
        )

    async def update(self, server: Server) -> bool:
        affected = await super().update(
            "UPDATE servers SET name = ? WHERE server_id = ?",
            server.name,
            server.server_id
        )
        return affected > 0

    async def delete(self, server: Server) -> bool:
        affected = await super().delete(
            "DELETE FROM servers WHERE server_id = ?",
            server.server_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM servers"
        )
        return affected > 0