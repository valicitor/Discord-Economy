from domain import Unit, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        Drops the units table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS units")

    async def clear_all(self) -> bool:
        """
        Clears all data from the units table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM units"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "units")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, unit_id: int) -> Optional[Unit]:
        row = await super().fetchrow(
            "SELECT * FROM units WHERE unit_id = ?",
            unit_id
        )
        return Unit(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Unit]:
        rows = await super().fetch("SELECT * FROM units WHERE server_id = ?", server_id)
        return [Unit(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Unit]:
        row = await super().fetchrow(
            "SELECT * FROM units WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Unit(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, unit_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM units WHERE unit_id = ?",
            unit_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, unit: Unit) -> int:
        return await super().insert(
            "INSERT INTO units (server_id, name, description, metadata) VALUES (?, ?, ?, ?)",
            unit.server_id,
            unit.name,
            unit.description,
            str(unit.metadata)
        )
    
    async def update(self, unit: Unit) -> bool:
        affected = await super().update(
            "UPDATE units SET server_id = ?, name = ?, description = ?, metadata = ? WHERE unit_id = ?",
            unit.server_id,
            unit.name,
            unit.description,
            str(unit.metadata),
            unit.unit_id
        )
        return affected > 0

    async def delete(self, unit: Unit) -> bool:
        affected = await super().delete(
            "DELETE FROM units WHERE unit_id = ?",
            unit.unit_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM units WHERE server_id = ?",
            server_id
        )
        return affected > 0