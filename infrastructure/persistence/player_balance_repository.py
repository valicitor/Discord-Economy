from domain import PlayerBalance
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerBalanceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS player_balances (
                    balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    currency_id INTEGER NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(currency_id) REFERENCES currencies(currency_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, balance_id: int) -> Optional[PlayerBalance]:
        row = await self.fetchrow(
            "SELECT * FROM player_balances WHERE balance_id = ?", (balance_id,)
        )
        return PlayerBalance(data=dict(row)) if row else None

    async def get_all(self, player_id: int = None) -> List[PlayerBalance]:
        if player_id is not None:
            rows = await self.fetch("SELECT * FROM player_balances WHERE player_id = ?", (player_id,))
        else:
            rows = await self.fetch("SELECT * FROM player_balances")
        return [PlayerBalance(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, player_balance: PlayerBalance) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO player_balances (
                player_id, currency_id, balance
            )
                VALUES (?, ?, ?)
            """, (
                player_balance.player_id,
                player_balance.currency_id,
                player_balance.balance
            ))

        return (last_id > 0, last_id)

    async def update(self, player_balance: PlayerBalance) -> bool:
        last_id = await self.update("""
            UPDATE player_balances
            SET balance = ?
            WHERE balance_id = ?
        """, (
            player_balance.balance,
            player_balance.balance_id
        ))

        return last_id > 0

    async def delete(self, player_balance: PlayerBalance) -> bool:
        last_id = await self.delete(
            "DELETE FROM player_balances WHERE balance_id = ?",
            (player_balance.balance_id,)
        )

        return last_id > 0
    
    async def delete_all(self, player_id: int) -> bool:
        last_id = await self.delete("DELETE FROM player_balances WHERE player_id = ?", (player_id,))
        return last_id > 0

    async def exists(self, balance_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM player_balances WHERE balance_id = ?", (balance_id,)
        )
        return row is not None