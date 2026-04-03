import json
import os
from config import BASE_DIR

from domain import Equipment, EquipmentStat
from infrastructure import EquipmentRepository, EquipmentStatRepository

def SeedEquipmentsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "equipments_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    equipment_data = data["equipments"]

    existing = EquipmentRepository().get_all()
    if existing:
        return False

    has_failures = False
    for r in equipment_data["data"]:
        equipment = Equipment(data=r)
        success, _ = EquipmentRepository().add(equipment)
        if not success:
            has_failures = True

    return has_failures

def SeedEquipmentStatsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "equipments_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    equipment_stat_data = data["equipment_stats"]

    existing = EquipmentStatRepository().get_all()
    if existing:
        return False

    has_failures = False
    for stat in equipment_stat_data["data"]:
        equipment = EquipmentRepository().get_by_name(stat["equipment_name"])
        if not equipment:
            continue  # or raise error

        equipment_stat = EquipmentStat(
            equipment_id=equipment.equipment_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        success, _ = EquipmentStatRepository().add(equipment_stat)
        if not success:
            has_failures = True

    return has_failures