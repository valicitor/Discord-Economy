from domain import Currency
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class CurrencyRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS currencies (
                    currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    emoji TEXT,
                    symbol TEXT NOT NULL,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, currency_id: int) -> Optional[Currency]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM currencies WHERE currency_id = ?", (currency_id,)
            )
            row = c.fetchone()
            return Currency(data=dict(row)) if row else None
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Currency]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM currencies WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Currency(data=dict(row)) if row else None

    def get_all(self) -> List[Currency]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM currencies")
            return [Currency(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, currency: Currency) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, currency: Currency) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, currency: Currency) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM currencies WHERE currency_id = ?",
                (currency.currency_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM currencies WHERE server_id = ?", (server_id,))
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, currency_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM currencies WHERE currency_id = ?",
                (currency_id,)
            )
            return c.fetchone() is not None