from domain import PlayerBalance, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class PlayerBalanceRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the player_balances table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS player_balances (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                currency_id INTEGER NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(currency_id) REFERENCES currencies(currency_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the player_balances table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS player_balances")

    async def clear_all(self) -> bool:
        """
        Clears all data from the player_balances table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM player_balances"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "player_balances")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, balance_id: int) -> Optional[PlayerBalance]:
        row = await super().fetchrow(
            "SELECT * FROM player_balances WHERE balance_id = ?",
            balance_id
        )
        return PlayerBalance(data=dict(row)) if row else None

    async def get_all(self, player_id: int = None) -> List[PlayerBalance]:
        if player_id is not None:
            rows = await super().fetch("SELECT * FROM player_balances WHERE player_id = ?", player_id)
        else:
            rows = await super().fetch("SELECT * FROM player_balances")
        return [PlayerBalance(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    # ---------- Existence Checks ----------

    async def exists(self, player_balance_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_balances WHERE balance_id = ?",
            player_balance_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, player_balance: PlayerBalance) -> int:
        return await super().insert(
            "INSERT INTO player_balances (player_id, currency_id, balance) VALUES (?, ?, ?)",
            player_balance.player_id,
            player_balance.currency_id,
            player_balance.balance
        )
    
    async def update(self, player_balance: PlayerBalance) -> bool:
        affected = await super().update(
            "UPDATE player_balances SET player_id = ?, currency_id = ?, balance = ? WHERE balance_id = ?",
            player_balance.player_id,
            player_balance.currency_id,
            player_balance.balance,
            player_balance.balance_id
        )
        return affected > 0

    async def delete(self, player_balance: PlayerBalance) -> bool:
        affected = await super().delete(
            "DELETE FROM player_balances WHERE balance_id = ?",
            player_balance.balance_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM player_balances WHERE player_id = ?",
            player_id
        )
        return affected > 0