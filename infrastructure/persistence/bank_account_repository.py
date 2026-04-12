from domain import BankAccount, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class BankAccountRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                balance INTEGER NOT NULL,
                created_at TEXT,
                FOREIGN KEY(bank_id) REFERENCES banks(bank_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the bank_accounts table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS bank_accounts")

    async def clear_all(self) -> bool:
        """
        Clears all data from the bank_accounts table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM bank_accounts"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "bank_accounts")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, account_id: int) -> Optional[BankAccount]:
        row = await super().fetchrow(
            "SELECT * FROM bank_accounts WHERE account_id = ?",
            account_id
        )
        return BankAccount(data=dict(row)) if row else None

    async def get_all(self, player_id: int = None) -> List[BankAccount]:
        if player_id is not None:
            rows = await super().fetch("SELECT * FROM bank_accounts WHERE player_id = ?", player_id)
        else:
            rows = await super().fetch("SELECT * FROM bank_accounts")
        return [BankAccount(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, account_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM bank_accounts WHERE account_id = ?",
            account_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, bank_account: BankAccount) -> int:
        return await super().insert(
            "INSERT INTO bank_accounts (bank_id, player_id, balance, created_at) VALUES (?, ?, ?, ?)",
            bank_account.bank_id,
            bank_account.player_id,
            bank_account.balance,
            bank_account.created_at
        )

    async def update(self, bank_account: BankAccount) -> bool:
        affected = await super().update(
            "UPDATE bank_accounts SET bank_id = ?, player_id = ?, balance = ?, created_at = ? WHERE account_id = ?",
            bank_account.bank_id,
            bank_account.player_id,
            bank_account.balance,
            bank_account.created_at,
            bank_account.account_id
        )
        return affected > 0

    async def delete(self, bank_account: BankAccount) -> bool:
        affected = await super().delete(
            "DELETE FROM bank_accounts WHERE account_id = ?",
            bank_account.account_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM bank_accounts WHERE player_id = ?",
            player_id
        )
        return affected > 0