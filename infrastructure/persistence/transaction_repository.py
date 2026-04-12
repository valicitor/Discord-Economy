from domain import Transaction, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class TransactionRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the action_logs table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
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

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the transactions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS transactions")

    async def clear_all(self) -> bool:
        """
        Clears all data from the transactions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM transactions"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "transactions")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        row = await super().fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = ?",
            transaction_id
        )
        return Transaction(data=dict(row)) if row else None

    async def get_all(self) -> List[Transaction]:
        rows = await super().fetch("SELECT * FROM transactions")
        return [Transaction(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, transaction_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM transactions WHERE transaction_id = ?",
            transaction_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, transaction: Transaction) -> int:
        return await super().insert(
            "INSERT INTO transactions (player_id, type, currency_id, amount, reference_id) VALUES (?, ?, ?, ?, ?)",
            transaction.player_id,
            transaction.type,
            transaction.currency_id,
            transaction.amount,
            transaction.reference_id
        )

    async def update(self, transaction: Transaction) -> bool:
        affected = await super().update(
            "UPDATE transactions SET player_id = ?, type = ?, currency_id = ?, amount = ?, reference_id = ? WHERE transaction_id = ?",
            transaction.player_id,
            transaction.type,
            transaction.currency_id,
            transaction.amount,
            transaction.reference_id,
            transaction.transaction_id
        )
        return affected > 0

    async def delete(self, transaction: Transaction) -> bool:
        affected = await super().delete(
            "DELETE FROM transactions WHERE transaction_id = ?",
            transaction.transaction_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM transactions WHERE player_id = ?",
            player_id
        )
        return affected > 0