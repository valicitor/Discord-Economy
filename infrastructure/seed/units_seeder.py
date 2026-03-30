import json
import os
from config import BASE_DIR
from domain import Unit, UnitStat

def SeedUnitsAndUnitStatsIfEmpty(unit_repo, stat_repo, seed_file=os.path.join(BASE_DIR, "infrastructure", "seed", "data", "units_seed.json")):
    with open(seed_file, "r") as f:
        data = json.load(f)

    name_to_id = _SeedUnitsIfEmpty(unit_repo, data["units"])
    _SeedUnitStatsIfEmpty(stat_repo, data["unit_stats"], name_to_id)

def _SeedUnitsIfEmpty(repo, unit_data):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    name_to_id = {}
    for r in unit_data["data"]:
        unit = Unit(data=r)
        success, new_id = repo.add(unit)
        if success:
            name_to_id[r["name"]] = new_id

    return name_to_id

def _SeedUnitStatsIfEmpty(repo, stat_data, name_to_id):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    for stat in stat_data["data"]:
        unit_id = name_to_id.get(stat["unit_name"])
        if not unit_id:
            continue  # or raise error

        key = (unit_id, stat["stat_key"])
        if key in existing:
            continue

        unit_stat = UnitStat(
            unit_id=unit_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        repo.add(unit_stat)