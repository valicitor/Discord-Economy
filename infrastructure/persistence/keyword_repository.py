from domain import Keyword, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class KeywordRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the action_logs table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                metadata TEXT,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                UNIQUE(name, server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the keywords table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS keywords")

    async def clear_all(self) -> bool:
        """
        Clears all data from the keywords table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM keywords"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "keywords")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        row = await super().fetchrow(
            "SELECT * FROM keywords WHERE keyword_id = ?",
            keyword_id
        )
        return Keyword(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Keyword]:
        rows = await super().fetch("SELECT * FROM keywords WHERE server_id = ?", server_id)
        return [Keyword(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Keyword]:
        row = await super().fetchrow(
            "SELECT * FROM keywords WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Keyword(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, keyword_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM keywords WHERE keyword_id = ?",
            keyword_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, keyword: Keyword) -> int:
        return await super().insert(
            "INSERT INTO keywords (server_id, name, description, metadata) VALUES (?, ?, ?, ?)",
            keyword.server_id,
            keyword.name,
            keyword.description,
            str(keyword.metadata)
        )

    async def update(self, keyword: Keyword) -> bool:
        affected = await super().update(
            "UPDATE keywords SET server_id = ?, name = ?, description = ?, metadata = ? WHERE keyword_id = ?",
            keyword.server_id,
            keyword.name,
            keyword.description,
            str(keyword.metadata),
            keyword.keyword_id
        )
        return affected > 0

    async def delete(self, keyword: Keyword) -> bool:
        affected = await super().delete(
            "DELETE FROM keywords WHERE keyword_id = ?",
            keyword.keyword_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM keywords WHERE server_id = ?",
            server_id
        )
        return affected > 0