from domain import BankAccount
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BankAccountRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, account_id: int) -> Optional[BankAccount]:
        row = await self.fetchrow(
            "SELECT * FROM bank_accounts WHERE account_id = ?", (account_id,)
        )
        return BankAccount(data=dict(row)) if row else None

    async def get_all(self, player_id: int = None) -> List[BankAccount]:
        if player_id is not None:
            rows = await self.fetch("SELECT * FROM bank_accounts WHERE player_id = ?", (player_id,))
        else:
            rows = await self.fetch("SELECT * FROM bank_accounts")
        return [BankAccount(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, bank_account: BankAccount) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO bank_accounts (
                bank_id, player_id, balance, created_at
            )
                VALUES (?, ?, ?, ?)
            """, (
                bank_account.bank_id,
                bank_account.player_id,
                bank_account.balance,
                bank_account.created_at
            ))

        return (last_id > 0, last_id)

    async def update(self, bank_account: BankAccount) -> bool:
        rowcount = await self.update("""
            UPDATE bank_accounts
            SET bank_id = ?, player_id = ?, balance = ?, created_at = ?
            WHERE account_id = ?
        """, (
                bank_account.bank_id,
                bank_account.player_id,
                bank_account.balance,
                bank_account.created_at,
                bank_account.account_id
            ))

        return rowcount > 0

    async def delete(self, bank_account: BankAccount) -> bool:
        rowcount = await self.delete(
            "DELETE FROM bank_accounts WHERE account_id = ?",
            (bank_account.account_id,)
        )
        return rowcount > 0
    
    async def delete_all(self, player_id: int) -> bool:
        rowcount = await self.delete("DELETE FROM bank_accounts WHERE player_id = ?", (player_id,))
        return rowcount > 0

    async def exists(self, account_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM bank_accounts WHERE account_id = ?",
            (account_id,)
        )
        return row is not None