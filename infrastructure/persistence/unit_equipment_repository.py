from domain import UnitEquipment
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitEquipmentRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS unit_equipment (
                    equip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    inventory_instance_id INTEGER NOT NULL,
                    slot TEXT NOT NULL,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                    FOREIGN KEY(inventory_instance_id) REFERENCES inventory_instances(instance_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, equip_id: int) -> Optional[UnitEquipment]:
        query = "SELECT * FROM unit_equipment WHERE equip_id = ?"
        params = (equip_id,)
        row = await self.fetchrow(query, params)
        return UnitEquipment(data=dict(row)) if row else None

    async def get_all(self) -> List[UnitEquipment]:
        query = "SELECT * FROM unit_equipment"
        rows = await self.fetch(query)
        return [UnitEquipment(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, unit_equipment: UnitEquipment) -> tuple[bool, int]:
        query = """
            INSERT INTO unit_equipment (
                unit_id, inventory_instance_id, slot
            )
            VALUES (?, ?, ?)
        """
        params = (
            unit_equipment.unit_id,
            unit_equipment.inventory_instance_id,
            unit_equipment.slot,
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, unit_equipment: UnitEquipment) -> bool:
        query = """
            UPDATE unit_equipment
            SET unit_id = ?, inventory_instance_id = ?, slot = ?
            WHERE equip_id = ?
        """
        params = (
            unit_equipment.unit_id,
            unit_equipment.inventory_instance_id,
            unit_equipment.slot,
            unit_equipment.equip_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, unit_equipment: UnitEquipment) -> bool:
        query = "DELETE FROM unit_equipment WHERE equip_id = ?"
        params = (unit_equipment.equip_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, equip_id: int) -> bool:
        query = "SELECT 1 FROM unit_equipment WHERE equip_id = ?"
        params = (equip_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0