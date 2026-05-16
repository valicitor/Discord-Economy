from domain import ExchangeRate, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ExchangeRateRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS exchange_rates (
                rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                from_currency_id INTEGER NOT NULL,
                to_currency_id INTEGER NOT NULL,
                rate REAL NOT NULL DEFAULT 1.0,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                FOREIGN KEY(from_currency_id) REFERENCES currencies(currency_id),
                FOREIGN KEY(to_currency_id) REFERENCES currencies(currency_id),
                UNIQUE(server_id, from_currency_id, to_currency_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS exchange_rates")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM exchange_rates")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "exchange_rates")
        return affected > 0

    async def get_by_id(self, rate_id: int) -> Optional[ExchangeRate]:
        row = await super().fetchrow("SELECT * FROM exchange_rates WHERE rate_id = ?", rate_id)
        return ExchangeRate(data=dict(row)) if row else None

    async def get_all(self) -> List[ExchangeRate]:
        rows = await super().fetch("SELECT * FROM exchange_rates")
        return [ExchangeRate(data=dict(row)) for row in rows]

    async def get_all_by_server(self, server_id: int) -> List[ExchangeRate]:
        rows = await super().fetch("SELECT * FROM exchange_rates WHERE server_id = ?", server_id)
        return [ExchangeRate(data=dict(row)) for row in rows]

    async def get_by_pair(self, server_id: int, from_currency_id: int, to_currency_id: int) -> Optional[ExchangeRate]:
        row = await super().fetchrow(
            "SELECT * FROM exchange_rates WHERE server_id = ? AND from_currency_id = ? AND to_currency_id = ?",
            server_id, from_currency_id, to_currency_id
        )
        return ExchangeRate(data=dict(row)) if row else None

    async def exists(self, rate_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM exchange_rates WHERE rate_id = ?", rate_id)
        return row is not None

    async def insert(self, rate: ExchangeRate) -> int:
        return await super().insert(
            "INSERT INTO exchange_rates (server_id, from_currency_id, to_currency_id, rate) VALUES (?, ?, ?, ?)",
            rate.server_id, rate.from_currency_id, rate.to_currency_id, rate.rate
        )

    async def update(self, rate: ExchangeRate) -> bool:
        affected = await super().update(
            "UPDATE exchange_rates SET server_id = ?, from_currency_id = ?, to_currency_id = ?, rate = ? WHERE rate_id = ?",
            rate.server_id, rate.from_currency_id, rate.to_currency_id, rate.rate, rate.rate_id
        )
        return affected > 0

    async def delete(self, rate: ExchangeRate) -> bool:
        affected = await super().delete("DELETE FROM exchange_rates WHERE rate_id = ?", rate.rate_id)
        return affected > 0

    async def delete_all(self, server_id: int) -> bool:
        affected = await super().delete("DELETE FROM exchange_rates WHERE server_id = ?", server_id)
        return affected > 0
