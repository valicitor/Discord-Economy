import json
import os
from config import BASE_DIR

from domain import Race, RaceStat
from infrastructure import RaceRepository, RaceStatRepository

def SeedRacesIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "races_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    race_data = data["races"]

    existing = RaceRepository().get_all()
    if existing:
        return False

    has_failures = False
    for r in race_data["data"]:
        race = Race(data=r)
        success, _ = RaceRepository().add(race)
        if not success:
            has_failures = True

    return has_failures

def SeedRaceStatsIfEmpty(seed_file=None) -> bool:
    if not seed_file:
        seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "races_seed.json")

    with open(seed_file, "r") as f:
        data = json.load(f)

    race_stat_data = data["race_stats"]

    existing = RaceStatRepository().get_all()
    if existing:
        return False

    has_failures = False
    for stat in race_stat_data["data"]:
        race = RaceRepository().get_by_name(stat["race_name"])
        if not race:
            continue  # or raise error

        race_stat = RaceStat(
            race_id=race.race_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        success, _ = RaceStatRepository().add(race_stat)
        if not success:
            has_failures = True

    return has_failures