import json

from domain import Vehicle
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class VehicleRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    async def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        query = "SELECT * FROM vehicles WHERE vehicle_id = ?"
        params = (vehicle_id,)
        row = await self.fetchrow(query, params)
        return Vehicle(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Vehicle]:
        query = "SELECT * FROM vehicles WHERE name = ? AND server_id = ?"
        params = (name, server_id)
        row = await self.fetchrow(query, params)
        return Vehicle(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Vehicle]:
        query = "SELECT * FROM vehicles WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return [Vehicle(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, vehicle: Vehicle) -> tuple[bool, int]:
        query = """
            INSERT INTO vehicles (
                server_id, name, description, metadata
            )
            VALUES (?, ?, ?, ?)
        """
        params = (
            vehicle.server_id,
            vehicle.name,
            vehicle.description,
            str(vehicle.metadata),
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, vehicle: Vehicle) -> bool:
        query = """
            UPDATE vehicles
            SET server_id = ?, name = ?, description = ?, metadata = ?
            WHERE vehicle_id = ?
        """
        params = (
            vehicle.server_id,
            vehicle.name,
            vehicle.description,
            str(vehicle.metadata),
            vehicle.vehicle_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, vehicle: Vehicle) -> bool:
        query = "DELETE FROM vehicles WHERE vehicle_id = ?"
        params = (vehicle.vehicle_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def delete_all(self, server_id: int) -> bool:
        query = "DELETE FROM vehicles WHERE server_id = ?"
        params = (server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, vehicle_id: int) -> bool:
        query = "SELECT 1 FROM vehicles WHERE vehicle_id = ?"
        params = (vehicle_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0