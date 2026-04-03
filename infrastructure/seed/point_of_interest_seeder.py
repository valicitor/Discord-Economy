import json
import os
from config import BASE_DIR

from domain import PointOfInterest
from infrastructure import PointOfInterestRepository


class PointOfInterestSeeder:
    def __init__(self, server_id: int|None = None):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if seed_file is None:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "point_of_interest_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        poi_data = data["data"]

        has_failures = False
        for poi_data in poi_data:
            poi = PointOfInterest(data=poi_data)
            poi.server_id = self.server_id
            (success, _) = PointOfInterestRepository().add(poi)
            if not success:
                has_failures = True

        return has_failures