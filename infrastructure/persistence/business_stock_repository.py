from domain import BusinessStock, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BusinessStockRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_stocks (
                stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER NOT NULL UNIQUE,
                market_points INTEGER NOT NULL DEFAULT 100,
                base_price INTEGER NOT NULL DEFAULT 100,
                dividend_rate REAL NOT NULL DEFAULT 0.05,
                FOREIGN KEY(business_id) REFERENCES businesses(business_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS business_stocks")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM business_stocks")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "business_stocks")
        return affected > 0

    async def get_by_id(self, stock_id: int) -> Optional[BusinessStock]:
        row = await super().fetchrow("SELECT * FROM business_stocks WHERE stock_id = ?", stock_id)
        return BusinessStock(data=dict(row)) if row else None

    async def get_all(self) -> List[BusinessStock]:
        rows = await super().fetch("SELECT * FROM business_stocks")
        return [BusinessStock(data=dict(row)) for row in rows]

    async def get_by_business_id(self, business_id: int) -> Optional[BusinessStock]:
        row = await super().fetchrow("SELECT * FROM business_stocks WHERE business_id = ?", business_id)
        return BusinessStock(data=dict(row)) if row else None

    async def get_all_by_server(self, server_id: int) -> List[BusinessStock]:
        rows = await super().fetch("""
            SELECT bs.* FROM business_stocks bs
            JOIN businesses b ON bs.business_id = b.business_id
            WHERE b.server_id = ?
        """, server_id)
        return [BusinessStock(data=dict(row)) for row in rows]

    async def exists(self, stock_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM business_stocks WHERE stock_id = ?", stock_id)
        return row is not None

    async def exists_by_business_id(self, business_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM business_stocks WHERE business_id = ?", business_id)
        return row is not None

    async def insert(self, stock: BusinessStock) -> int:
        return await super().insert(
            "INSERT INTO business_stocks (business_id, market_points, base_price, dividend_rate) VALUES (?, ?, ?, ?)",
            stock.business_id, stock.market_points, stock.base_price, stock.dividend_rate
        )

    async def update(self, stock: BusinessStock) -> bool:
        affected = await super().update(
            "UPDATE business_stocks SET business_id = ?, market_points = ?, base_price = ?, dividend_rate = ? WHERE stock_id = ?",
            stock.business_id, stock.market_points, stock.base_price, stock.dividend_rate, stock.stock_id
        )
        return affected > 0

    async def delete(self, stock: BusinessStock) -> bool:
        affected = await super().delete("DELETE FROM business_stocks WHERE stock_id = ?", stock.stock_id)
        return affected > 0

    async def delete_all(self, business_id: int) -> bool:
        affected = await super().delete("DELETE FROM business_stocks WHERE business_id = ?", business_id)
        return affected > 0
