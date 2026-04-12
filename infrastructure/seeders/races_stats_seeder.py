from domain import RaceStat, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, RaceRepository, RaceStatRepository


class RaceStatsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.race_repo: RaceRepository | None = None
        self.stat_repo: RaceStatRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.race_repo = await RaceRepository().get_instance()
        seeder.stat_repo = await RaceStatRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "races_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "race_stats" not in data or "data" not in data["race_stats"]:
            raise SeederErrorException("Invalid race_stats seed structure")

        records = data["race_stats"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.stat_repo.transaction():
            for stat in records:
                try:
                    race = await self.race_repo.get_by_name(
                        stat["race_name"], self.server_id
                    )

                    if not race:
                        skipped += 1
                        continue

                    entity = RaceStat(data=stat)
                    entity.race_id=race.race_id

                    stat_id = await self.stat_repo.insert(entity)
                    if not stat_id:
                        failed += 1
                    else:
                        inserted += 1

                except Exception:
                    failed += 1

        return SeederResult(
            status="completed",
            inserted=inserted,
            reason=None,
            failed=failed,
        )