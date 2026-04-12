from domain import Bank, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class BankRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS banks (
                bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                poi_id INTEGER,
                name TEXT NOT NULL,
                interest_rate REAL NOT NULL,
                max_accounts INTEGER,
                range INTEGER,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id),
                UNIQUE(name, server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the banks table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS banks")

    async def clear_all(self) -> bool:
        """
        Clears all data from the banks table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM banks"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "banks")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, bank_id: int) -> Optional[Bank]:
        row = await super().fetchrow(
            "SELECT * FROM banks WHERE bank_id = ?",
            bank_id
        )
        return Bank(data=dict(row)) if row else None

    async def get_all(self, server_id: int = None) -> List[Bank]:
        if server_id is not None:
            rows = await super().fetch("SELECT * FROM banks WHERE server_id = ?", server_id)
        else:
            rows = await super().fetch("SELECT * FROM banks")
        return [Bank(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Bank]:
        row = await super().fetchrow(
            "SELECT * FROM banks WHERE name = ? AND server_id = ?",
            name, 
            server_id
        )
        return Bank(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, bank_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM banks WHERE bank_id = ?",
            bank_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, bank: Bank) -> int:
        return await super().insert(
            "INSERT INTO banks (server_id, poi_id, name, interest_rate, max_accounts, range) VALUES (?, ?, ?, ?, ?, ?)",
            bank.server_id,
            bank.poi_id,
            bank.name,
            bank.interest_rate,
            bank.max_accounts,
            bank.range
        )

    async def update(self, bank: Bank) -> bool:
        affected = await super().update(
            "UPDATE banks SET server_id = ?, poi_id = ?, name = ?, interest_rate = ?, max_accounts = ?, range = ? WHERE bank_id = ?",
            bank.server_id,
            bank.poi_id,
            bank.name,
            bank.interest_rate,
            bank.max_accounts,
            bank.range,
            bank.bank_id    
        )
        return affected > 0

    async def delete(self, bank: Bank) -> bool:
        affected = await super().delete(
            "DELETE FROM banks WHERE bank_id = ?",
            bank.bank_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM banks WHERE server_id = ?",
            server_id
        )
        return affected > 0