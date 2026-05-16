from domain import BusinessResource, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BusinessResourceRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_resources (
                resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                required_quantity INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(business_id) REFERENCES businesses(business_id),
                UNIQUE(business_id, resource_type)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS business_resources")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM business_resources")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "business_resources")
        return affected > 0

    async def get_by_id(self, resource_id: int) -> Optional[BusinessResource]:
        row = await super().fetchrow("SELECT * FROM business_resources WHERE resource_id = ?", resource_id)
        return BusinessResource(data=dict(row)) if row else None

    async def get_all(self) -> List[BusinessResource]:
        rows = await super().fetch("SELECT * FROM business_resources")
        return [BusinessResource(data=dict(row)) for row in rows]

    async def get_all_by_business(self, business_id: int) -> List[BusinessResource]:
        rows = await super().fetch("SELECT * FROM business_resources WHERE business_id = ?", business_id)
        return [BusinessResource(data=dict(row)) for row in rows]

    async def get_by_business_type(self, business_id: int, resource_type: str) -> Optional[BusinessResource]:
        row = await super().fetchrow(
            "SELECT * FROM business_resources WHERE business_id = ? AND resource_type = ?",
            business_id, resource_type
        )
        return BusinessResource(data=dict(row)) if row else None

    async def get_demanded_by_server(self, server_id: int, exclude_business_id: int) -> List[BusinessResource]:
        rows = await super().fetch(
            """
            SELECT br.* FROM business_resources br
            JOIN businesses b ON br.business_id = b.business_id
            WHERE b.server_id = ? AND br.required_quantity > br.quantity AND br.business_id != ?
            """,
            server_id, exclude_business_id
        )
        return [BusinessResource(data=dict(row)) for row in rows]

    async def get_requirements(self, business_id: int) -> List[BusinessResource]:
        rows = await super().fetch(
            "SELECT * FROM business_resources WHERE business_id = ? AND required_quantity > 0",
            business_id
        )
        return [BusinessResource(data=dict(row)) for row in rows]

    async def exists(self, resource_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM business_resources WHERE resource_id = ?", resource_id)
        return row is not None

    async def insert(self, resource: BusinessResource) -> int:
        return await super().insert(
            "INSERT INTO business_resources (business_id, resource_type, quantity, required_quantity) VALUES (?, ?, ?, ?)",
            resource.business_id, resource.resource_type, resource.quantity, resource.required_quantity
        )

    async def update(self, resource: BusinessResource) -> bool:
        affected = await super().update(
            "UPDATE business_resources SET business_id = ?, resource_type = ?, quantity = ?, required_quantity = ? WHERE resource_id = ?",
            resource.business_id, resource.resource_type, resource.quantity, resource.required_quantity, resource.resource_id
        )
        return affected > 0

    async def delete(self, resource: BusinessResource) -> bool:
        affected = await super().delete("DELETE FROM business_resources WHERE resource_id = ?", resource.resource_id)
        return affected > 0

    async def delete_all(self, business_id: int) -> bool:
        affected = await super().delete("DELETE FROM business_resources WHERE business_id = ?", business_id)
        return affected > 0
