from domain import Transaction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class TransactionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    currency_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    reference_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(currency_id) REFERENCES currencies(currency_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        query = "SELECT * FROM transactions WHERE transaction_id = ?"
        params = (transaction_id,)
        row = await self.fetchrow(query, params)
        return Transaction(data=dict(row)) if row else None

    async def get_all(self) -> List[Transaction]:
        query = "SELECT * FROM transactions"
        rows = await self.fetch(query)
        return [Transaction(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, transaction: Transaction) -> tuple[bool, int]:
        query = """
            INSERT INTO transactions (
                player_id, type, currency_id, amount, reference_id
            )
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            transaction.player_id,
            transaction.type,
            transaction.currency_id,
            transaction.amount,
            transaction.reference_id
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, transaction: Transaction) -> bool:
        query = """
            UPDATE transactions
            SET player_id = ?, type = ?, currency_id = ?, amount = ?, reference_id = ?
            WHERE transaction_id = ?
        """
        params = (
            transaction.player_id,
            transaction.type,
            transaction.currency_id,
            transaction.amount,
            transaction.reference_id,
            transaction.transaction_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, transaction: Transaction) -> bool:
        query = "DELETE FROM transactions WHERE transaction_id = ?"
        params = (transaction.transaction_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, transaction_id: int) -> bool:
        query = "SELECT 1 FROM transactions WHERE transaction_id = ?"
        params = (transaction_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0