from domain import Keyword
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class KeywordRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        row = await self.fetchrow(
            "SELECT * FROM keywords WHERE keyword_id = ?", (keyword_id,)
        )
        return Keyword(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Keyword]:
        row = await self.fetchrow(
            "SELECT * FROM keywords WHERE name = ? AND server_id = ?", (name, server_id)
        )
        return Keyword(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Keyword]:
        rows = await self.fetch("SELECT * FROM keywords WHERE server_id = ?", (server_id,))
        return [Keyword(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, keyword: Keyword) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO keywords (
                server_id, name, description, metadata
            )

                VALUES (?, ?, ?, ?)
            """, (
                keyword.server_id,
                keyword.name,
                keyword.description,
                str(keyword.metadata)
            ))

        return (last_id > 0, last_id)

    async def update(self, keyword: Keyword) -> bool:
        last_id = await self.update("""
            UPDATE keywords
            SET server_id = ?, name = ?, description = ?, metadata = ?
            WHERE keyword_id = ?
        """, (
            keyword.server_id,
            keyword.name,
            keyword.description,
            str(keyword.metadata),
            keyword.keyword_id
        ))
        return last_id > 0

    async def delete(self, keyword: Keyword) -> bool:
        last_id = await self.delete(
            "DELETE FROM keywords WHERE keyword_id = ?",
            (keyword.keyword_id,)
        )
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> bool:
        last_id = await self.delete(
            "DELETE FROM keywords WHERE server_id = ?", (server_id,)
        )
        return last_id > 0

    async def exists(self, keyword_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM keywords WHERE keyword_id = ?", (keyword_id,)
        )
        return row is not None