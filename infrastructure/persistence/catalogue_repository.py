import json

from domain import Catalogue, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class CatalogueRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS catalogue (
                catalogue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                metadata TEXT,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                UNIQUE(name, server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the catalogue table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS catalogue")

    async def clear_all(self) -> bool:
        """
        Clears all data from the catalogue table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM catalogue"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "catalogue")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, catalogue_id: int) -> Optional[Catalogue]:
        row = await super().fetchrow(
            "SELECT * FROM catalogue WHERE catalogue_id = ?",
            catalogue_id
        )
        return Catalogue(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Catalogue]:
        rows = await super().fetch("SELECT * FROM catalogue WHERE server_id = ?", server_id)
        return [Catalogue(data=dict(row)) for row in rows]

    # ---------- Additional Queries ----------

    async def get_by_catalogue_id(self, catalogue_id: int, server_id: int) -> Optional[Catalogue]:
        row = await super().fetchrow(
            "SELECT * FROM catalogue WHERE catalogue_id = ? AND server_id = ?",
            catalogue_id,
            server_id
        )
        return Catalogue(data=dict(row)) if row else None

    async def get_by_name(self, name: str, server_id: int) -> Optional[Catalogue]:
        row = await super().fetchrow(
            "SELECT * FROM catalogue WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Catalogue(data=dict(row)) if row else None
    
    async def search_by_name(
        self,
        name_query: str,
        server_id: int,
        status: list[str],
        limit: int
    ) -> List[Catalogue]:

        placeholders = ",".join("?" for _ in status)

        query = f"""
            SELECT *
            FROM catalogue
            WHERE name LIKE ?
            AND server_id = ?
            AND status IN ({placeholders})
            LIMIT ?
        """

        params = [f"%{name_query}%", server_id, *status, limit]

        rows = await super().fetch(query, *params)

        return [Catalogue(data=dict(row)) for row in rows]

    # ---------- Existence Checks ----------

    async def exists(self, catalogue_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM catalogue WHERE catalogue_id = ?",
            catalogue_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_name(self, name: str, server_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM catalogue WHERE name = ? AND server_id = ?",
            name,
            server_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, catalogue: Catalogue) -> int:
        return await super().insert(
            "INSERT INTO catalogue (server_id, name, type, description, status, metadata) VALUES (?, ?, ?, ?, ?, ?)",
            catalogue.server_id,
            catalogue.name,
            catalogue.type,
            catalogue.description,
            catalogue.status,
            json.dumps(catalogue.metadata)
        )
    
    async def update(self, catalogue: Catalogue) -> bool:
        affected = await super().update(
            "UPDATE catalogue SET server_id = ?, name = ?, type = ?, description = ?, status = ?, metadata = ? WHERE catalogue_id = ?",
            catalogue.server_id,
            catalogue.name,
            catalogue.type,
            catalogue.description,
            catalogue.status,
            json.dumps(catalogue.metadata),
            catalogue.catalogue_id
        )
        return affected > 0

    async def delete(self, catalogue: Catalogue) -> bool:
        affected = await super().delete(
            "DELETE FROM catalogue WHERE catalogue_id = ?",
            catalogue.catalogue_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM catalogue WHERE server_id = ?",
            server_id
        )
        return affected > 0