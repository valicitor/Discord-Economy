from domain import Location, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, PointOfInterestRepository, LocationRepository

class LocationsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.point_of_interest_repo: PointOfInterestRepository | None = None
        self.location_repo: LocationRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.point_of_interest_repo = await PointOfInterestRepository().get_instance()
        seeder.location_repo = await LocationRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "point_of_interest_seed.json")
        return await seeder._seed(file_path)
 
    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "locations" not in data or "data" not in data["locations"]:
            raise SeederErrorException("Invalid locations seed structure")

        records = data["locations"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.location_repo.transaction():
            for location in records:
                try:
                    poi = await self.point_of_interest_repo.get_by_name(location["type"], self.server_id)

                    if not poi:
                        skipped += 1
                        continue

                    entity = Location(data=location)
                    entity.poi_id=poi.poi_id

                    location_id = await self.location_repo.insert(entity)
                    if not location_id:
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