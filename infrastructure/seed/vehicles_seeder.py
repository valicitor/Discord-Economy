import json
import os
from config import BASE_DIR

from domain import Vehicle, VehicleStat
from infrastructure import VehicleRepository, VehicleStatRepository

def SeedVehiclesIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "vehicles_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    vehicle_data = data["vehicles"]

    existing = VehicleRepository().get_all()
    if existing:
        return False

    has_failures = False
    for v in vehicle_data["data"]:
        vehicle = Vehicle(data=v)
        success, _ = VehicleRepository().add(vehicle)
        if not success:
            has_failures = True

    return has_failures

def SeedVehicleStatsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "vehicles_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    vehicle_stat_data = data["vehicle_stats"]

    existing = VehicleStatRepository().get_all()
    if existing:
        return False

    has_failures = False
    for stat in vehicle_stat_data["data"]:
        vehicle = VehicleRepository().get_by_name(stat["vehicle_name"])
        if not vehicle:
            continue  # or raise error

        vehicle_stat = VehicleStat(
            vehicle_id=vehicle.vehicle_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        success, _ = VehicleStatRepository().add(vehicle_stat)
        if not success:
            has_failures = True

    return has_failures