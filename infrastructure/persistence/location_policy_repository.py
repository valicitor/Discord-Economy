from domain import LocationPolicy, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class LocationPolicyRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS location_policies (
                policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL UNIQUE,
                tax_rate REAL NOT NULL DEFAULT 0.0,
                trade_tariff REAL NOT NULL DEFAULT 0.0,
                import_restricted INTEGER NOT NULL DEFAULT 0,
                export_restricted INTEGER NOT NULL DEFAULT 0,
                interest_rate_modifier REAL NOT NULL DEFAULT 1.0,
                smuggling_risk_modifier REAL NOT NULL DEFAULT 1.0,
                FOREIGN KEY(location_id) REFERENCES locations(location_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS location_policies")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM location_policies")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "location_policies")
        return affected > 0

    async def get_by_id(self, policy_id: int) -> Optional[LocationPolicy]:
        row = await super().fetchrow("SELECT * FROM location_policies WHERE policy_id = ?", policy_id)
        return LocationPolicy(data=dict(row)) if row else None

    async def get_by_location(self, location_id: int) -> Optional[LocationPolicy]:
        row = await super().fetchrow("SELECT * FROM location_policies WHERE location_id = ?", location_id)
        return LocationPolicy(data=dict(row)) if row else None

    async def exists(self, location_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM location_policies WHERE location_id = ?", location_id)
        return row is not None

    async def insert(self, policy: LocationPolicy) -> int:
        return await super().insert(
            "INSERT INTO location_policies (location_id, tax_rate, trade_tariff, import_restricted, export_restricted, interest_rate_modifier, smuggling_risk_modifier) VALUES (?, ?, ?, ?, ?, ?, ?)",
            policy.location_id, policy.tax_rate, policy.trade_tariff,
            int(policy.import_restricted), int(policy.export_restricted),
            policy.interest_rate_modifier, policy.smuggling_risk_modifier
        )

    async def update(self, policy: LocationPolicy) -> bool:
        affected = await super().update(
            "UPDATE location_policies SET tax_rate = ?, trade_tariff = ?, import_restricted = ?, export_restricted = ?, interest_rate_modifier = ?, smuggling_risk_modifier = ? WHERE policy_id = ?",
            policy.tax_rate, policy.trade_tariff,
            int(policy.import_restricted), int(policy.export_restricted),
            policy.interest_rate_modifier, policy.smuggling_risk_modifier,
            policy.policy_id
        )
        return affected > 0

    async def get_all(self) -> List[LocationPolicy]:
        rows = await super().fetch("SELECT * FROM location_policies")
        return [LocationPolicy(data=dict(row)) for row in rows]

    async def delete(self, policy: LocationPolicy) -> bool:
        affected = await super().delete("DELETE FROM location_policies WHERE policy_id = ?", policy.policy_id)
        return affected > 0

    async def delete_all(self) -> bool:
        affected = await super().delete("DELETE FROM location_policies")
        return affected > 0
