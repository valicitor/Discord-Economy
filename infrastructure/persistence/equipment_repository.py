from domain import Equipment
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "static_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    slot TEXT DEFAULT '',
                    metadata TEXT
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, equipment_id: int) -> Optional[Equipment]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,)
            )
            row = c.fetchone()
            return Equipment(data=dict(row)) if row else None

    def get_all(self) -> List[Equipment]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM equipment")
            return [Equipment(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, equipment: Equipment) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO equipment (
                    name, description, slot, metadata
                )
                VALUES (?, ?, ?, ?)
            """, (
                equipment.name,
                equipment.description,
                equipment.slot,
                str(equipment.metadata)
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, equipment: Equipment) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE equipment
                SET name = ?, description = ?, slot = ?, metadata = ?
                WHERE equipment_id = ?
            """, (
                equipment.name,
                equipment.description,
                equipment.slot,
                str(equipment.metadata),
                equipment.equipment_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, equipment: Equipment) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM equipment WHERE equipment_id = ?",
                (equipment.equipment_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM equipment")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, equipment_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM equipment WHERE equipment_id = ?",
                (equipment_id,)
            )
            return c.fetchone() is not None