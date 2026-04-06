from domain import Currency
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class CurrencyRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS currencies (
                    currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    emoji TEXT,
                    symbol TEXT NOT NULL,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, currency_id: int) -> Optional[Currency]:
        row = await self.fetchrow(
            "SELECT * FROM currencies WHERE currency_id = ?", (currency_id,)
        )
        return Currency(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Currency]:
        row = await self.fetchrow(
            "SELECT * FROM currencies WHERE name = ? AND server_id = ?", (name, server_id)
        )
        return Currency(data=dict(row)) if row else None

    async def get_all(self) -> List[Currency]:
        rows = await self.fetch("SELECT * FROM currencies")
        return [Currency(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, currency: Currency) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO currencies (
                server_id, name, emoji, symbol
            )
                VALUES (?, ?, ?, ?)
            """, (
                currency.server_id,
                currency.name,
                currency.emoji,
                currency.symbol
            ))

        return (last_id > 0, last_id)

    async def update(self, currency: Currency) -> bool:
        rowcount = await self.update("""
            UPDATE currencies
            SET server_id = ?, name = ?, emoji = ?, symbol = ?
            WHERE currency_id = ?
        """, (
            currency.server_id,
                currency.name,
                currency.emoji,
                currency.symbol,
                currency.currency_id
            ))

        return rowcount > 0

    async def delete(self, currency: Currency) -> bool:
        rowcount = await self.delete(
            "DELETE FROM currencies WHERE currency_id = ?",
            (currency.currency_id,)
        )
        return rowcount > 0
    
    async def delete_all(self, server_id: int) -> bool:
        rowcount = await self.delete("DELETE FROM currencies WHERE server_id = ?", (server_id,))
        return rowcount > 0

    async def exists(self, currency_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM currencies WHERE currency_id = ?",
            (currency_id,)
        )
        return row is not None