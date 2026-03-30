import json
import os
from config import BASE_DIR

from domain import PointOfInterest


def SeedPointOfInterestsIfEmpty(repo, seed_file=os.path.join(BASE_DIR, "infrastructure", "seed", "data", "point_of_interest_seed.json")):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    with open(seed_file, "r") as f:
        data = json.load(f)

    for poi_data in data["data"]:
        poi = PointOfInterest(data=poi_data)
        repo.add(poi)