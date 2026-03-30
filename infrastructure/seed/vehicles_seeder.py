import json
import os
from config import BASE_DIR
from domain import Vehicle, VehicleStat

def SeedVehiclesAndVehicleStatsIfEmpty(vehicle_repo, stat_repo, seed_file=os.path.join(BASE_DIR, "infrastructure", "seed", "data", "vehicles_seed.json")):
    with open(seed_file, "r") as f:
        data = json.load(f)

    name_to_id = _SeedVehiclesIfEmpty(vehicle_repo, data["vehicles"])
    _SeedVehicleStatsIfEmpty(stat_repo, data["vehicle_stats"], name_to_id)

def _SeedVehiclesIfEmpty(repo, vehicle_data):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    name_to_id = {}
    for r in vehicle_data["data"]:
        vehicle = Vehicle(data=r)
        success, new_id = repo.add(vehicle)
        if success:
            name_to_id[r["name"]] = new_id

    return name_to_id

def _SeedVehicleStatsIfEmpty(repo, stat_data, name_to_id):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    for stat in stat_data["data"]:
        vehicle_id = name_to_id.get(stat["vehicle_name"])
        if not vehicle_id:
            continue  # or raise error

        key = (vehicle_id, stat["stat_key"])
        if key in existing:
            continue

        vehicle_stat = VehicleStat(
            vehicle_id=vehicle_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        repo.add(vehicle_stat)