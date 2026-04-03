from domain import Bank
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BankRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    poi_id INTEGER,
                    name TEXT NOT NULL,
                    interest_rate REAL NOT NULL,
                    max_accounts INTEGER,
                    range INTEGER,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id)
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
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Bank]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM banks WHERE name = ? AND server_id = ?", (name, server_id)
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
                    server_id, poi_id, name, interest_rate, max_accounts, range
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                bank.server_id,
                bank.poi_id,
                bank.name,
                bank.interest_rate,
                bank.max_accounts,
                bank.range
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, bank: Bank) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE banks
                SET server_id = ?, poi_id = ?, name = ?, interest_rate = ?, max_accounts = ?, range = ?
                WHERE bank_id = ?
            """, (
                bank.server_id,
                bank.poi_id,
                bank.name,
                bank.interest_rate,
                bank.max_accounts,
                bank.range,
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
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM banks WHERE server_id = ?", (server_id,))
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