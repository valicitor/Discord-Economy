import json
import os
from config import BASE_DIR

from domain import PointOfInterest, Location
from infrastructure import PointOfInterestRepository, LocationRepository


class PointOfInterestSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    async def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "point_of_interest_seed.json")

        with open(seed_file, "r", encoding='utf-8') as f:
            data = json.load(f)

        poi_data = data["points_of_interest"]

        existing = await PointOfInterestRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for r in poi_data["data"]:
            poi = PointOfInterest(data=r)
            poi.server_id = self.server_id
            success, _ = await PointOfInterestRepository().add(poi)
            if not success:
                has_failures = True

        return has_failures


class LocationsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    async def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "point_of_interest_seed.json")

        with open(seed_file, "r", encoding='utf-8') as f:
            data = json.load(f)

        location_data = data["locations"]

        has_failures = False
        for r in location_data["data"]:
            poi = await PointOfInterestRepository().get_by_name(r["type"], self.server_id)
            if not poi:
                continue  # 
        
            location = Location(data=r)
            location.poi_id = poi.poi_id
            success, _ = await LocationRepository().add(location)
            if not success:
                has_failures = True

        return has_failures