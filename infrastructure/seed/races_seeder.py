import json
import os
from config import BASE_DIR
from domain import Race, RaceStat


def SeedRacesAndRaceStatsIfEmpty(race_repo, stat_repo, seed_file=os.path.join(BASE_DIR, "infrastructure", "seed", "data", "races_seed.json")):
    with open(seed_file, "r") as f:
        data = json.load(f)

    name_to_id = _SeedRacesIfEmpty(race_repo, data["races"])
    _SeedRaceStatsIfEmpty(stat_repo, data["race_stats"], name_to_id)

def _SeedRacesIfEmpty(repo, race_data):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    name_to_id = {}
    for r in race_data["data"]:
        race = Race(data=r)
        success, new_id = repo.add(race)
        if success:
            name_to_id[r["name"]] = new_id

    return name_to_id

def _SeedRaceStatsIfEmpty(repo, stat_data, name_to_id):
    existing = repo.get_all()
    if existing:
        return  # already seeded

    for stat in stat_data["data"]:
        race_id = name_to_id.get(stat["race_name"])
        if not race_id:
            continue  # or raise error

        key = (race_id, stat["stat_key"])
        if key in existing:
            continue

        race_stat = RaceStat(
            race_id=race_id,
            stat_key=stat["stat_key"],
            stat_value=stat["stat_value"]
        )

        repo.add(race_stat)