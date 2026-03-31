from domain import BankAccount
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BankAccountRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
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
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, account_id: int) -> Optional[BankAccount]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM bank_accounts WHERE account_id = ?", (account_id,)
            )
            row = c.fetchone()
            return BankAccount(data=dict(row)) if row else None

    def get_all(self, player_id: int = None) -> List[BankAccount]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            if player_id is not None:
                c.execute("SELECT * FROM bank_accounts WHERE player_id = ?", (player_id,))
            else:
                c.execute("SELECT * FROM bank_accounts")
            return [BankAccount(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, bank_account: BankAccount) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, bank_account: BankAccount) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, bank_account: BankAccount) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM bank_accounts WHERE account_id = ?",
                (bank_account.account_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self, player_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM bank_accounts WHERE player_id = ?", (player_id,))
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, account_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM bank_accounts WHERE account_id = ?",
                (account_id,)
            )
            return c.fetchone() is not None