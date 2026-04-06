from domain import Unit
from domain import IRepository
from domain.models import vehicle
from infrastructure import BaseRepository
from typing import List, Optional


class UnitRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    async def get_by_id(self, unit_id: int) -> Optional[Unit]:
        query = "SELECT * FROM units WHERE unit_id = ?"
        params = (unit_id,)
        row = await self.fetchrow(query, params)
        return Unit(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Unit]:
        query = "SELECT * FROM units WHERE name = ? AND server_id = ?"
        params = (name, server_id)
        row = await self.fetchrow(query, params)
        return Unit(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Unit]:
        query = "SELECT * FROM units WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return [Unit(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, unit: Unit) -> tuple[bool, int]:
        query = """
            INSERT INTO units (
                server_id, name, description, metadata
            )
            VALUES (?, ?, ?, ?)
        """
        params = (
            unit.server_id,
            unit.name,
            unit.description,
            str(unit.metadata),
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, unit: Unit) -> bool:
        query = """
            UPDATE units
            SET server_id = ?, name = ?, description = ?, metadata = ?
            WHERE unit_id = ?
        """
        params = (
            unit.server_id,
            unit.name,
            unit.description,
            str(unit.metadata),
            unit.unit_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, unit: Unit) -> bool:
        query = "DELETE FROM units WHERE unit_id = ?"
        params = (unit.unit_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> bool:
        query = "DELETE FROM units WHERE server_id = ?"
        params = (server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, unit_id: int) -> bool:
        query = "SELECT 1 FROM units WHERE unit_id = ?"
        params = (unit_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0