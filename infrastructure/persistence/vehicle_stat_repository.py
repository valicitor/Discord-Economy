from domain import VehicleStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class VehicleStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_stats (
                    vehicle_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, vehicle_stat_id: int) -> Optional[VehicleStat]:
        query = "SELECT * FROM vehicle_stats WHERE vehicle_stat_id = ?"
        params = (vehicle_stat_id,)
        row = await self.fetchrow(query, params)
        return VehicleStat(data=dict(row)) if row else None

    async def get_by_key(self, stat_key: str, vehicle_id: int) -> Optional[VehicleStat]:
        query = "SELECT * FROM vehicle_stats WHERE stat_key = ? AND vehicle_id = ?"
        params = (stat_key, vehicle_id)
        row = await self.fetchrow(query, params)
        return VehicleStat(data=dict(row)) if row else None

    async def get_all(self) -> List[VehicleStat]:
        query = "SELECT * FROM vehicle_stats"
        rows = await self.fetch(query)
        return [VehicleStat(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, vehicle_stat: VehicleStat) -> tuple[bool, int]:
        query = """
            INSERT INTO vehicle_stats (
                vehicle_id, stat_key, stat_value
            )
            VALUES (?, ?, ?)
        """
        params = (
            vehicle_stat.vehicle_id,
            vehicle_stat.stat_key,
            vehicle_stat.stat_value
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, vehicle_stat: VehicleStat) -> bool:
        query = """
            UPDATE vehicle_stats
            SET vehicle_id = ?, stat_key = ?, stat_value = ?
            WHERE vehicle_stat_id = ?
        """
        params = (
            vehicle_stat.vehicle_id,
            vehicle_stat.stat_key,
            vehicle_stat.stat_value,
            vehicle_stat.vehicle_stat_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, vehicle_stat: VehicleStat) -> bool:
        query = "DELETE FROM vehicle_stats WHERE vehicle_stat_id = ?"
        params = (vehicle_stat.vehicle_stat_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def delete_all(self) -> bool:
        query = "DELETE FROM vehicle_stats"
        last_id = await self.delete(query)
        return last_id > 0

    async def exists(self, vehicle_stat_id: int) -> bool:
        query = "SELECT 1 FROM vehicle_stats WHERE vehicle_stat_id = ?"
        params = (vehicle_stat_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0