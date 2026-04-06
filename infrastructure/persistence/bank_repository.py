from domain import Bank
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BankRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, bank_id: int) -> Optional[Bank]:
        row = await self.fetchrow(
            "SELECT * FROM banks WHERE bank_id = ?", (bank_id,)
        )
        return Bank(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Bank]:
        row = await self.fetchrow(
            "SELECT * FROM banks WHERE name = ? AND server_id = ?", (name, server_id)
        )
        return Bank(data=dict(row)) if row else None

    async def get_all(self) -> List[Bank]:
        rows = await self.fetch("SELECT * FROM banks")
        return [Bank(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, bank: Bank) -> tuple[bool, int]:
        last_id = await self.insert("""
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

        return (last_id > 0, last_id)

    async def update(self, bank: Bank) -> bool:
        rowcount = await self.update("""
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

        return rowcount > 0

    async def delete(self, bank: Bank) -> bool:
        rowcount = await self.delete(
            "DELETE FROM banks WHERE bank_id = ?",
            (bank.bank_id,)
        )
        return rowcount > 0
    
    async def delete_all(self, server_id: int) -> bool:
        rowcount = await self.delete("DELETE FROM banks WHERE server_id = ?", (server_id,))
        return rowcount > 0

    async def exists(self, bank_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM banks WHERE bank_id = ?",
            (bank_id,)
        )
        return row is not None