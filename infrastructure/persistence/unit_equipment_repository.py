from domain import UnitEquipment
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitEquipmentRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS unit_equipment (
                    equip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    inventory_instance_id INTEGER NOT NULL,
                    slot TEXT NOT NULL,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                    FOREIGN KEY(inventory_instance_id) REFERENCES inventory_instances(instance_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, equip_id: int) -> Optional[UnitEquipment]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM unit_equipment WHERE equip_id = ?", (equip_id,)
            )
            row = c.fetchone()
            return UnitEquipment(data=dict(row)) if row else None

    def get_all(self) -> List[UnitEquipment]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM unit_equipment")
            return [UnitEquipment(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, unit_equipment: UnitEquipment) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO unit_equipment (
                    unit_id, inventory_instance_id, slot
                )
                VALUES (?, ?, ?)
            """, (
                unit_equipment.unit_id,
                unit_equipment.inventory_instance_id,
                unit_equipment.slot,
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, unit_equipment: UnitEquipment) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE unit_equipment
                SET unit_id = ?, inventory_instance_id = ?, slot = ?
                WHERE equip_id = ?
            """, (
                unit_equipment.unit_id,
                unit_equipment.inventory_instance_id,
                unit_equipment.slot,
                unit_equipment.equip_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, unit_equipment: UnitEquipment) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM unit_equipment WHERE equip_id = ?",
                (unit_equipment.equip_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, equip_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM unit_equipment WHERE equip_id = ?",
                (equip_id,)
            )
            return c.fetchone() is not None