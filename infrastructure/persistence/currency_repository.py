from domain import Currency, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class CurrencyRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS currencies (
                currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                emoji TEXT,
                symbol TEXT NOT NULL,
                FOREIGN KEY(server_id) REFERENCES servers(server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the currencies table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS currencies")

    async def clear_all(self) -> bool:
        """
        Clears all data from the currencies table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM currencies"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "currencies")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, currency_id: int) -> Optional[Currency]:
        row = await super().fetchrow(
            "SELECT * FROM currencies WHERE currency_id = ?",
            currency_id
        )
        return Currency(data=dict(row)) if row else None

    async def get_all(self) -> List[Currency]:
        rows = await super().fetch("SELECT * FROM currencies")
        return [Currency(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Currency]:
        row = await super().fetchrow(
            "SELECT * FROM currencies WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Currency(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, currency_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM currencies WHERE currency_id = ?",
            currency_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, currency: Currency) -> int:
        return await super().insert(
            "INSERT INTO currencies (server_id, name, emoji, symbol) VALUES (?, ?, ?, ?)",
            currency.server_id,
            currency.name,
            currency.emoji,
            currency.symbol
        )
    
    async def update(self, currency: Currency) -> bool:
        affected = await super().update(
            "UPDATE currencies SET server_id = ?, name = ?, emoji = ?, symbol = ? WHERE currency_id = ?",
            currency.server_id,
            currency.name,
            currency.emoji,
            currency.symbol,
            currency.currency_id
        )
        return affected > 0

    async def delete(self, currency: Currency) -> bool:
        affected = await super().delete(
            "DELETE FROM currencies WHERE currency_id = ?",
            currency.currency_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM currencies WHERE server_id = ?",
            server_id
        )
        return affected > 0