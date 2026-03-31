from domain import Transaction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class TransactionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
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
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
            )
            row = c.fetchone()
            return Transaction(data=dict(row)) if row else None

    def get_all(self) -> List[Transaction]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM transactions")
            return [Transaction(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, transaction: Transaction) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO transactions (
                    player_id, type, currency_id, amount, reference_id

                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                transaction.player_id,
                transaction.type,
                transaction.currency_id,
                transaction.amount,
                transaction.reference_id
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, transaction: Transaction) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE transactions
                SET player_id = ?, type = ?, currency_id = ?, amount = ?, reference_id = ?
                WHERE transaction_id = ?
            """, (
                transaction.player_id,
                transaction.type,
                transaction.currency_id,
                transaction.amount,
                transaction.reference_id,
                transaction.transaction_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, transaction: Transaction) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM transactions WHERE transaction_id = ?",
                (transaction.transaction_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, transaction_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            )
            return c.fetchone() is not None