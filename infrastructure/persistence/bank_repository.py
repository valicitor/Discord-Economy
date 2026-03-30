from domain import Bank
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BankRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "dynamic_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    interest_rate REAL NOT NULL,
                    max_accounts INTEGER NOT NULL
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, bank_id: int) -> Optional[Bank]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM banks WHERE bank_id = ?", (bank_id,)
            )
            row = c.fetchone()
            return Bank(data=dict(row)) if row else None

    def get_all(self) -> List[Bank]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM banks")
            return [Bank(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, bank: Bank) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO banks (
                    server_id, name, interest_rate, max_accounts
                )
                VALUES (?, ?, ?, ?)
            """, (
                bank.server_id,
                bank.name,
                bank.interest_rate,
                bank.max_accounts
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, bank: Bank) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE banks
                SET server_id = ?, name = ?, interest_rate = ?, max_accounts = ?
                WHERE bank_id = ?
            """, (
                bank.server_id,
                bank.name,
                bank.interest_rate,
                bank.max_accounts,
                bank.bank_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, bank: Bank) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM banks WHERE bank_id = ?",
                (bank.bank_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, bank_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM banks WHERE bank_id = ?",
                (bank_id,)
            )
            return c.fetchone() is not None