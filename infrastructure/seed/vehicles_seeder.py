import json
import os
from config import BASE_DIR

from domain import Vehicle, VehicleStat
from infrastructure import VehicleRepository, VehicleStatRepository

class VehiclesSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    async def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "vehicles_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        vehicle_data = data["vehicles"]

        existing = await VehicleRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for v in vehicle_data["data"]:
            vehicle = Vehicle(data=v)
            vehicle.server_id = self.server_id
            success, _ = await VehicleRepository().add(vehicle)
            if not success:
                has_failures = True

        return has_failures

class VehicleStatsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    async def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "vehicles_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        vehicle_stat_data = data["vehicle_stats"]

        has_failures = False
        for stat in vehicle_stat_data["data"]:
            vehicle = await VehicleRepository().get_by_name(stat["vehicle_name"], self.server_id)
            if not vehicle:
                continue  # or raise error

            vehicle_stat = VehicleStat(
                vehicle_id=vehicle.vehicle_id,
                stat_key=stat["stat_key"],
                stat_value=stat["stat_value"]
            )

            success, _ = await VehicleStatRepository().add(vehicle_stat)
            if not success:
                has_failures = True

        return has_failures