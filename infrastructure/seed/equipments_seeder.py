import json
import os
from config import BASE_DIR

from domain import Equipment, EquipmentStat
from infrastructure import EquipmentRepository, EquipmentStatRepository

class EquipmentsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "equipments_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        equipment_data = data["equipments"]

        existing = EquipmentRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for r in equipment_data["data"]:
            equipment = Equipment(data=r)
            equipment.server_id = self.server_id
            success, _ = EquipmentRepository().add(equipment)
            if not success:
                has_failures = True

        return has_failures


class EquipmentStatsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "equipments_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        equipment_stat_data = data["equipment_stats"]

        has_failures = False
        for stat in equipment_stat_data["data"]:
            equipment = EquipmentRepository().get_by_name(stat["equipment_name"], self.server_id)
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