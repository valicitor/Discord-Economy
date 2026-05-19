from domain import Loan, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class LoanRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                player_id INTEGER NOT NULL,
                bank_id INTEGER NOT NULL,
                principal INTEGER NOT NULL,
                interest_rate REAL NOT NULL,
                balance_remaining INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(bank_id) REFERENCES banks(bank_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS loans")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM loans")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "loans")
        return affected > 0

    async def get_by_id(self, loan_id: int) -> Optional[Loan]:
        row = await super().fetchrow("SELECT * FROM loans WHERE loan_id = ?", loan_id)
        return Loan(data=dict(row)) if row else None

    async def get_all(self) -> List[Loan]:
        rows = await super().fetch("SELECT * FROM loans")
        return [Loan(data=dict(row)) for row in rows]

    async def get_all_by_player_id(self, player_id: int, status: str | None = None) -> List[Loan]:
        if status:
            rows = await super().fetch(
                "SELECT * FROM loans WHERE player_id = ? AND status = ?", player_id, status
            )
        else:
            rows = await super().fetch("SELECT * FROM loans WHERE player_id = ?", player_id)
        return [Loan(data=dict(row)) for row in rows]

    async def get_active_by_player_bank(self, player_id: int, bank_id: int) -> Optional[Loan]:
        row = await super().fetchrow(
            "SELECT * FROM loans WHERE player_id = ? AND bank_id = ? AND status = 'active'",
            player_id, bank_id
        )
        return Loan(data=dict(row)) if row else None

    async def exists(self, loan_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM loans WHERE loan_id = ?", loan_id)
        return row is not None

    async def insert(self, loan: Loan) -> int:
        return await super().insert(
            "INSERT INTO loans (server_id, player_id, bank_id, principal, interest_rate, balance_remaining, status, last_updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            loan.server_id, loan.player_id, loan.bank_id, loan.principal, loan.interest_rate, loan.balance_remaining, loan.status
        )

    async def update(self, loan: Loan) -> bool:
        affected = await super().update(
            "UPDATE loans SET server_id = ?, player_id = ?, bank_id = ?, principal = ?, interest_rate = ?, balance_remaining = ?, status = ?, last_updated_at = CURRENT_TIMESTAMP WHERE loan_id = ?",
            loan.server_id, loan.player_id, loan.bank_id, loan.principal, loan.interest_rate, loan.balance_remaining, loan.status, loan.loan_id
        )
        return affected > 0

    async def delete(self, loan: Loan) -> bool:
        affected = await super().delete("DELETE FROM loans WHERE loan_id = ?", loan.loan_id)
        return affected > 0

    async def delete_all(self, player_id: int) -> bool:
        affected = await super().delete("DELETE FROM loans WHERE player_id = ?", player_id)
        return affected > 0
