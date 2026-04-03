from domain import Equipment
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    slot TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, equipment_id: int) -> Optional[Equipment]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,)
            )
            row = c.fetchone()
            return Equipment(data=dict(row)) if row else None
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Equipment]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM equipment WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Equipment(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Equipment]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM equipment WHERE server_id = ?", (server_id,))
            return [Equipment(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, equipment: Equipment) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO equipment (
                    server_id, name, description, slot, metadata
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                equipment.server_id,
                equipment.name,
                equipment.description,
                equipment.slot,
                str(equipment.metadata)
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, equipment: Equipment) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE equipment
                SET server_id = ?, name = ?, description = ?, slot = ?, metadata = ?
                WHERE equipment_id = ?
            """, (
                equipment.server_id,
                equipment.name,
                equipment.description,
                equipment.slot,
                str(equipment.metadata),
                equipment.equipment_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, equipment: Equipment) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM equipment WHERE equipment_id = ?",
                (equipment.equipment_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM equipment WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, equipment_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM equipment WHERE equipment_id = ?",
                (equipment_id,)
            )
            return c.fetchone() is not None