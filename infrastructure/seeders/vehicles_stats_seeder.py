from domain import Vehicle, VehicleStat, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, VehicleRepository, VehicleStatRepository

class VehicleStatsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.vehicle_repo: VehicleRepository | None = None
        self.stat_repo: VehicleStatRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.vehicle_repo = await VehicleRepository().get_instance()
        seeder.stat_repo = await VehicleStatRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "vehicles_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "vehicle_stats" not in data or "data" not in data["vehicle_stats"]:
            raise SeederErrorException("Invalid vehicle_stats seed structure")

        records = data["vehicle_stats"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.stat_repo.transaction():
            for stat in records:
                try:
                    vehicle = await self.vehicle_repo.get_by_name(
                        stat["vehicle_name"], self.server_id
                    )

                    if not vehicle:
                        skipped += 1
                        continue

                    entity = VehicleStat(data=stat)
                    entity.vehicle_id=vehicle.vehicle_id

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