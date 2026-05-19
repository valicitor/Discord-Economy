from domain import PlayerStock, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerStockRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS player_stocks (
                player_stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                player_id INTEGER NOT NULL,
                business_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(business_id) REFERENCES businesses(business_id),
                UNIQUE(player_id, business_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS player_stocks")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM player_stocks")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "player_stocks")
        return affected > 0

    async def get_by_id(self, player_stock_id: int) -> Optional[PlayerStock]:
        row = await super().fetchrow("SELECT * FROM player_stocks WHERE player_stock_id = ?", player_stock_id)
        return PlayerStock(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerStock]:
        rows = await super().fetch("SELECT * FROM player_stocks")
        return [PlayerStock(data=dict(row)) for row in rows]

    async def get_by_player_business(self, player_id: int, business_id: int) -> Optional[PlayerStock]:
        row = await super().fetchrow(
            "SELECT * FROM player_stocks WHERE player_id = ? AND business_id = ?",
            player_id, business_id
        )
        return PlayerStock(data=dict(row)) if row else None

    async def get_all_by_player_id(self, player_id: int) -> List[PlayerStock]:
        rows = await super().fetch("SELECT * FROM player_stocks WHERE player_id = ?", player_id)
        return [PlayerStock(data=dict(row)) for row in rows]

    async def get_all_by_business_id(self, business_id: int) -> List[PlayerStock]:
        rows = await super().fetch("SELECT * FROM player_stocks WHERE business_id = ?", business_id)
        return [PlayerStock(data=dict(row)) for row in rows]

    async def exists(self, player_stock_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM player_stocks WHERE player_stock_id = ?", player_stock_id)
        return row is not None

    async def insert(self, stock: PlayerStock) -> int:
        return await super().insert(
            "INSERT INTO player_stocks (server_id, player_id, business_id, quantity, last_updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            stock.server_id, stock.player_id, stock.business_id, stock.quantity
        )

    async def update(self, stock: PlayerStock) -> bool:
        affected = await super().update(
            "UPDATE player_stocks SET server_id = ?, player_id = ?, business_id = ?, quantity = ?, last_updated_at = CURRENT_TIMESTAMP WHERE player_stock_id = ?",
            stock.server_id, stock.player_id, stock.business_id, stock.quantity, stock.player_stock_id
        )
        return affected > 0

    async def delete(self, stock: PlayerStock) -> bool:
        affected = await super().delete("DELETE FROM player_stocks WHERE player_stock_id = ?", stock.player_stock_id)
        return affected > 0

    async def delete_all(self, player_id: int) -> bool:
        affected = await super().delete("DELETE FROM player_stocks WHERE player_id = ?", player_id)
        return affected > 0
