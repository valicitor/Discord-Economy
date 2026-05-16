from domain import Transport, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class TransportRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transports (
                transport_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                from_business_id INTEGER NOT NULL,
                to_business_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'in_transit',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                arrive_at DATETIME,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(from_business_id) REFERENCES businesses(business_id),
                FOREIGN KEY(to_business_id) REFERENCES businesses(business_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS transports")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM transports")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "transports")
        return affected > 0

    async def get_by_id(self, transport_id: int) -> Optional[Transport]:
        row = await super().fetchrow("SELECT * FROM transports WHERE transport_id = ?", transport_id)
        return Transport(data=dict(row)) if row else None

    async def get_all(self) -> List[Transport]:
        rows = await super().fetch("SELECT * FROM transports")
        return [Transport(data=dict(row)) for row in rows]

    async def get_all_by_player(self, player_id: int, status: str | None = None) -> List[Transport]:
        if status:
            rows = await super().fetch(
                "SELECT * FROM transports WHERE player_id = ? AND status = ?", player_id, status
            )
        else:
            rows = await super().fetch("SELECT * FROM transports WHERE player_id = ?", player_id)
        return [Transport(data=dict(row)) for row in rows]

    async def get_arrived(self, player_id: int) -> List[Transport]:
        """Returns in_transit transports whose arrive_at has passed."""
        rows = await super().fetch(
            "SELECT * FROM transports WHERE player_id = ? AND status = 'in_transit' AND arrive_at <= datetime('now')",
            player_id
        )
        return [Transport(data=dict(row)) for row in rows]

    async def exists(self, transport_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM transports WHERE transport_id = ?", transport_id)
        return row is not None

    async def insert(self, transport: Transport) -> int:
        return await super().insert(
            "INSERT INTO transports (player_id, from_business_id, to_business_id, resource_type, quantity, status, arrive_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            transport.player_id, transport.from_business_id, transport.to_business_id,
            transport.resource_type, transport.quantity, transport.status, transport.arrive_at
        )

    async def update(self, transport: Transport) -> bool:
        affected = await super().update(
            "UPDATE transports SET player_id = ?, from_business_id = ?, to_business_id = ?, resource_type = ?, quantity = ?, status = ?, arrive_at = ? WHERE transport_id = ?",
            transport.player_id, transport.from_business_id, transport.to_business_id,
            transport.resource_type, transport.quantity, transport.status, transport.arrive_at, transport.transport_id
        )
        return affected > 0

    async def delete(self, transport: Transport) -> bool:
        affected = await super().delete("DELETE FROM transports WHERE transport_id = ?", transport.transport_id)
        return affected > 0

    async def delete_all(self, player_id: int) -> bool:
        affected = await super().delete("DELETE FROM transports WHERE player_id = ?", player_id)
        return affected > 0
