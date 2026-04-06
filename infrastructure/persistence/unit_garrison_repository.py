from domain import UnitGarrison
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitGarrisonRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS unit_garrisons (
                    garrison_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    poi_id INTEGER NOT NULL,
                    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                    FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, garrison_id: int) -> Optional[UnitGarrison]:
        query = "SELECT * FROM unit_garrisons WHERE garrison_id = ?"
        params = (garrison_id,)
        row = await self.fetchrow(query, params)
        return UnitGarrison(data=dict(row)) if row else None

    async def get_all(self) -> List[UnitGarrison]:
        query = "SELECT * FROM unit_garrisons"
        rows = await self.fetch(query)
        return [UnitGarrison(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, garrison: UnitGarrison) -> tuple[bool, int]:
        query = """
            INSERT INTO unit_garrisons (
                unit_id, poi_id, assigned_at
            )
            VALUES (?, ?, ?)
        """
        params = (
            garrison.unit_id,
            garrison.poi_id,
            garrison.assigned_at
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, garrison: UnitGarrison) -> bool:
        query = """
            UPDATE unit_garrisons
            SET unit_id = ?, poi_id = ?, assigned_at = ?
            WHERE garrison_id = ?
        """
        params = (
            garrison.unit_id,
            garrison.poi_id,
            garrison.assigned_at,
            garrison.garrison_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, garrison: UnitGarrison) -> bool:
        query = "DELETE FROM unit_garrisons WHERE garrison_id = ?"
        params = (garrison.garrison_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, garrison_id: int) -> bool:
        query = "SELECT 1 FROM unit_garrisons WHERE garrison_id = ?"
        params = (garrison_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0