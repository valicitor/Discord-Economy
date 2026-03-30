import json
import os
from config import BASE_DIR
from domain import Equipment, EquipmentStat

def SeedEquipmentsAndEquipmentStatsIfEmpty(equipment_repo, stat_repo, seed_file=os.path.join(BASE_DIR, "infrastructure", "seed", "data", "equipments_seed.json")):
    with open(seed_file, "r") as f:
        data = json.load(f)

    name_to_id = _SeedEquipmentsIfEmpty(equipment_repo, data["equipments"])
    _SeedEquipmentStatsIfEmpty(stat_repo, data["equipment_stats"], name_to_id)

def _SeedEquipmentsIfEmpty(repo, equipment_data):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    name_to_id = {}
    for r in equipment_data["data"]:
        equipment = Equipment(data=r)
        success, new_id = repo.add(equipment)
        if success:
            name_to_id[r["name"]] = new_id

    return name_to_id

def _SeedEquipmentStatsIfEmpty(repo, stat_data, name_to_id):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    for stat in stat_data["data"]:
        equipment_id = name_to_id.get(stat["equipment_name"])
        if not equipment_id:
            continue  # or raise error

        key = (equipment_id, stat["stat_key"])
        if key in existing:
            continue

        equipment_stat = EquipmentStat(
            equipment_id=equipment_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        repo.add(equipment_stat)