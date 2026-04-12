from domain import UnitEquipment, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class UnitEquipmentRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the action_logs table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS unit_equipment (
                equip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                inventory_instance_id INTEGER NOT NULL,
                slot TEXT NOT NULL,
                FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                FOREIGN KEY(inventory_instance_id) REFERENCES inventory_instances(instance_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the unit_equipment table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS unit_equipment")

    async def clear_all(self) -> bool:
        """
        Clears all data from the unit_equipment table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM unit_equipment"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "unit_equipment")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, equip_id: int) -> Optional[UnitEquipment]:
        row = await super().fetchrow(
            "SELECT * FROM unit_equipment WHERE equip_id = ?",
            equip_id
        )
        return UnitEquipment(data=dict(row)) if row else None

    async def get_all(self) -> List[UnitEquipment]:
        rows = await super().fetch("SELECT * FROM unit_equipment")
        return [UnitEquipment(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, equip_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM unit_equipment WHERE equip_id = ?",
            equip_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, unit_equipment: UnitEquipment) -> int:
        return await super().insert(
            "INSERT INTO unit_equipment (unit_id, inventory_instance_id, slot) VALUES (?, ?, ?)",
            unit_equipment.unit_id,
            unit_equipment.inventory_instance_id,
            unit_equipment.slot
        )

    async def update(self, unit_equipment: UnitEquipment) -> bool:
        affected = await super().update(
            "UPDATE unit_equipment SET unit_id = ?, inventory_instance_id = ?, slot = ? WHERE equip_id = ?",
            unit_equipment.unit_id,
            unit_equipment.inventory_instance_id,
            unit_equipment.slot,
            unit_equipment.equip_id
        )
        return affected > 0

    async def delete(self, unit_equipment: UnitEquipment) -> bool:
        affected = await super().delete(
            "DELETE FROM unit_equipment WHERE equip_id = ?",
            unit_equipment.equip_id
        )
        return affected > 0
    
    async def delete_all(self, unit_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM unit_equipment WHERE unit_id = ?",
            unit_id
        )
        return affected > 0