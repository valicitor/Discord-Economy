from domain import Equipment, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                slot TEXT DEFAULT '',
                metadata TEXT,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                UNIQUE(name, server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the equipment table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS equipment")

    async def clear_all(self) -> bool:
        """
        Clears all data from the equipment table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM equipment"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "equipment")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, equipment_id: int) -> Optional[Equipment]:
        row = await super().fetchrow(
            "SELECT * FROM equipment WHERE equipment_id = ?",
            equipment_id
        )
        return Equipment(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Equipment]:
        rows = await super().fetch("SELECT * FROM equipment WHERE server_id = ?", server_id)
        return [Equipment(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Equipment]:
        row = await super().fetchrow(
            "SELECT * FROM equipment WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Equipment(data=dict(row)) if row else None
    
    async def search_by_name(self, name_query: str, server_id: int, limit: int) -> List[Equipment]:
        rows = await super().fetch(
            "SELECT * FROM equipment WHERE name LIKE ? AND server_id = ? LIMIT ?",
            f"%{name_query}%",
            server_id,
            limit
        )
        return [Equipment(data=dict(row)) for row in rows]
    
    # ---------- Existence Checks ----------

    async def exists(self, equipment_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM equipment WHERE equipment_id = ?",
            equipment_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, equipment: Equipment) -> int:
        return await super().insert(
            "INSERT INTO equipment (server_id, name, description, slot, metadata) VALUES (?, ?, ?, ?, ?)",
            equipment.server_id,
            equipment.name,
            equipment.description,
            equipment.slot,
            str(equipment.metadata)
        )
    
    async def update(self, equipment: Equipment) -> bool:
        affected = await super().update(
            "UPDATE equipment SET server_id = ?, name = ?, description = ?, slot = ?, metadata = ? WHERE equipment_id = ?",
            equipment.server_id,
            equipment.name,
            equipment.description,
            equipment.slot,
            str(equipment.metadata),
            equipment.equipment_id
        )
        return affected > 0

    async def delete(self, equipment: Equipment) -> bool:
        affected = await super().delete(
            "DELETE FROM equipment WHERE equipment_id = ?",
            equipment.equipment_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM equipment WHERE server_id = ?",
            server_id
        )
        return affected > 0