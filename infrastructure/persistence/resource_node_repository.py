from domain import ResourceNode, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ResourceNodeRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS resource_nodes (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                location_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                max_quantity INTEGER NOT NULL DEFAULT 100,
                regen_rate INTEGER NOT NULL DEFAULT 5,
                discovered INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(location_id) REFERENCES locations(location_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS resource_nodes")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM resource_nodes")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "resource_nodes")
        return affected > 0

    async def get_by_id(self, node_id: int) -> Optional[ResourceNode]:
        row = await super().fetchrow("SELECT * FROM resource_nodes WHERE node_id = ?", node_id)
        return ResourceNode(data=dict(row)) if row else None

    async def get_all(self) -> List[ResourceNode]:
        rows = await super().fetch("SELECT * FROM resource_nodes")
        return [ResourceNode(data=dict(row)) for row in rows]

    async def get_all_by_location(self, location_id: int) -> List[ResourceNode]:
        rows = await super().fetch("SELECT * FROM resource_nodes WHERE location_id = ?", location_id)
        return [ResourceNode(data=dict(row)) for row in rows]

    async def get_discovered_by_location(self, location_id: int) -> List[ResourceNode]:
        rows = await super().fetch(
            "SELECT * FROM resource_nodes WHERE location_id = ? AND discovered = 1", location_id
        )
        return [ResourceNode(data=dict(row)) for row in rows]

    async def get_undiscovered_by_location(self, location_id: int) -> List[ResourceNode]:
        rows = await super().fetch(
            "SELECT * FROM resource_nodes WHERE location_id = ? AND discovered = 0 AND quantity > 0", location_id
        )
        return [ResourceNode(data=dict(row)) for row in rows]

    async def get_by_location_type(self, location_id: int, resource_type: str) -> Optional[ResourceNode]:
        row = await super().fetchrow(
            "SELECT * FROM resource_nodes WHERE location_id = ? AND resource_type = ?",
            location_id, resource_type
        )
        return ResourceNode(data=dict(row)) if row else None

    async def exists(self, node_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM resource_nodes WHERE node_id = ?", node_id)
        return row is not None

    async def insert(self, node: ResourceNode) -> int:
        return await super().insert(
            "INSERT INTO resource_nodes (server_id, location_id, resource_type, quantity, max_quantity, regen_rate, discovered) VALUES (?, ?, ?, ?, ?, ?, ?)",
            node.server_id, node.location_id, node.resource_type, node.quantity, node.max_quantity, node.regen_rate, int(node.discovered)
        )

    async def update(self, node: ResourceNode) -> bool:
        affected = await super().update(
            "UPDATE resource_nodes SET server_id = ?, location_id = ?, resource_type = ?, quantity = ?, max_quantity = ?, regen_rate = ?, discovered = ? WHERE node_id = ?",
            node.server_id, node.location_id, node.resource_type, node.quantity, node.max_quantity, node.regen_rate, int(node.discovered), node.node_id
        )
        return affected > 0

    async def delete(self, node: ResourceNode) -> bool:
        affected = await super().delete("DELETE FROM resource_nodes WHERE node_id = ?", node.node_id)
        return affected > 0

    async def delete_all(self, location_id: int) -> bool:
        affected = await super().delete("DELETE FROM resource_nodes WHERE location_id = ?", location_id)
        return affected > 0
