from domain import VehicleStat, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class VehicleStatRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_stats (
                vehicle_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value TEXT NOT NULL,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the vehicle_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS vehicle_stats")

    async def clear_all(self) -> bool:
        """
        Clears all data from the vehicle_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM vehicle_stats"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "vehicle_stats")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, vehicle_stat_id: int) -> Optional[VehicleStat]:
        row = await super().fetchrow(
            "SELECT * FROM vehicle_stats WHERE vehicle_stat_id = ?",
            vehicle_stat_id
        )
        return VehicleStat(data=dict(row)) if row else None

    async def get_all(self, vehicle_id: int|None = None) -> List[VehicleStat]:
        if vehicle_id is not None:
            rows = await super().fetch("SELECT * FROM vehicle_stats WHERE vehicle_id = ?", vehicle_id)
        else:
            rows = await super().fetch("SELECT * FROM vehicle_stats")
        return [VehicleStat(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_key(self, stat_key: str, vehicle_id: int) -> Optional[VehicleStat]:
        row = await super().fetchrow(
            "SELECT * FROM vehicle_stats WHERE stat_key = ? AND vehicle_id = ?", 
            stat_key, 
            vehicle_id
        )
        return VehicleStat(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, vehicle_stat_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM vehicle_stats WHERE vehicle_stat_id = ?",
            vehicle_stat_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, vehicle_stat: VehicleStat) -> int:
        return await super().insert(
            "INSERT INTO vehicle_stats (vehicle_id, stat_key, stat_value) VALUES (?, ?, ?)",
            vehicle_stat.vehicle_id,
            vehicle_stat.stat_key,
            vehicle_stat.stat_value
        )
    
    async def update(self, vehicle_stat: VehicleStat) -> bool:
        affected = await super().update(
            "UPDATE vehicle_stats SET vehicle_id = ?, stat_key = ?, stat_value = ? WHERE vehicle_stat_id = ?",
            vehicle_stat.vehicle_id,
            vehicle_stat.stat_key,
            vehicle_stat.stat_value,
            vehicle_stat.vehicle_stat_id
        )
        return affected > 0

    async def delete(self, vehicle_stat: VehicleStat) -> bool:
        affected = await super().delete(
            "DELETE FROM vehicle_stats WHERE vehicle_stat_id = ?",
            vehicle_stat.vehicle_stat_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM vehicle_stats"
        )
        return affected > 0