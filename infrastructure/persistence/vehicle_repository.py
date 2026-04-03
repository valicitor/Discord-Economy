import json

from domain import Vehicle
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class VehicleRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    metadata TEXT
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,)
            )
            row = c.fetchone()
            return Vehicle(data=dict(row)) if row else None
    
    def get_by_name(self, name: str) -> Optional[Vehicle]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM vehicles WHERE name = ?", (name,)
            )
            row = c.fetchone()
            return Vehicle(data=dict(row)) if row else None

    def get_all(self) -> List[Vehicle]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM vehicles")
            return [Vehicle(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, vehicle: Vehicle) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO vehicles (
                    name, description, metadata
                )
                VALUES (?, ?, ?)
            """, (
                vehicle.name,
                vehicle.description,
                str(vehicle.metadata),
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, vehicle: Vehicle) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE vehicles
                SET name = ?, description = ?, metadata = ?
                WHERE vehicle_id = ?
            """, (
                vehicle.name,
                vehicle.description,
                str(vehicle.metadata),
                vehicle.vehicle_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, vehicle: Vehicle) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM vehicles WHERE vehicle_id = ?",
                (vehicle.vehicle_id,)
            )

            self.commit()
            return c.rowcount > 0

    def delete_all(self) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM vehicles")
            self.commit()
            return c.rowcount > 0
        
    def exists(self, vehicle_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM vehicles WHERE vehicle_id = ?",
                (vehicle_id,)
            )
            return c.fetchone() is not None