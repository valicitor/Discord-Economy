from domain import Unit, UnitStat, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, UnitRepository, UnitStatRepository


class UnitStatsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.unit_repo: UnitRepository | None = None
        self.stat_repo: UnitStatRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.unit_repo = await UnitRepository().get_instance()
        seeder.stat_repo = await UnitStatRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "units_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "unit_stats" not in data or "data" not in data["unit_stats"]:
            raise SeederErrorException("Invalid unit_stats seed structure")

        records = data["unit_stats"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.stat_repo.transaction():
            for stat in records:
                try:
                    unit = await self.unit_repo.get_by_name(
                        stat["unit_name"], self.server_id
                    )

                    if not unit:
                        skipped += 1
                        continue

                    entity = UnitStat(data=stat)
                    entity.unit_id=unit.unit_id

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