from domain import PlayerBalance
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerBalanceRepository(IRepository, BaseRepository):
    def __init__(self, db_path: str = None):
        super().__init__(db_path or "player_balance.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS player_balances (
                    balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    currency_id INTEGER NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(currency_id) REFERENCES currencies(currency_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, balance_id: int) -> Optional[PlayerBalance]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM player_balances WHERE balance_id = ?", (balance_id,)
            )
            row = c.fetchone()
            return PlayerBalance(data=dict(row)) if row else None

    def get_all(self) -> List[PlayerBalance]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM player_balances")
            return [PlayerBalance(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player_balance: PlayerBalance) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO player_balances (
                    player_id, currency_id, balance
                )
                VALUES (?, ?, ?)
            """, (
                player_balance.player_id,
                player_balance.currency_id,
                player_balance.balance
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player_balance: PlayerBalance) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE player_balances
                SET balance = ?
                WHERE balance_id = ?
            """, (
                player_balance.balance,
                player_balance.balance_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, player_balance: PlayerBalance) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM player_balances WHERE balance_id = ?",
                (player_balance.balance_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, balance_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM player_balances WHERE balance_id = ?", (balance_id,)
            )
            return c.fetchone() is not None