import json
import os
from config import BASE_DIR

from domain import Unit, UnitStat
from infrastructure import UnitRepository, UnitStatRepository

class UnitsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "units_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        unit_data = data["units"]

        existing = UnitRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for u in unit_data["data"]:
            unit = Unit(data=u)
            unit.server_id = self.server_id
            success, _ = UnitRepository().add(unit)
            if not success:
                has_failures = True

        return has_failures

class UnitStatsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "units_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        unit_stat_data = data["unit_stats"]

        has_failures = False
        for stat in unit_stat_data["data"]:
            unit = UnitRepository().get_by_name(stat["unit_name"], self.server_id)
            if not unit:
                continue  # or raise error

            unit_stat = UnitStat(
                unit_id=unit.unit_id,
                stat_key=stat["stat_key"],
                stat_value=stat["stat_value"]
            )

            success, _ = UnitStatRepository().add(unit_stat)
            if not success:
                has_failures = True

        return has_failures