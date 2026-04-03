import json
import os
from config import BASE_DIR

from domain import Unit, UnitStat
from infrastructure import UnitRepository, UnitStatRepository

def SeedUnitsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "units_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    unit_data = data["units"]

    existing = UnitRepository().get_all()
    if existing:
        return False

    has_failures = False
    for u in unit_data["data"]:
        unit = Unit(data=u)
        success, _ = UnitRepository().add(unit)
        if not success:
            has_failures = True

    return has_failures

def SeedUnitStatsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "units_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    unit_stat_data = data["unit_stats"]

    existing = UnitStatRepository().get_all()
    if existing:
        return False

    has_failures = False
    for stat in unit_stat_data["data"]:
        unit = UnitRepository().get_by_name(stat["unit_name"])
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