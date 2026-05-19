from domain import LocationPolicy, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, LocationPolicyRepository, LocationRepository, PointOfInterestRepository


class LocationPoliciesSeeder(BaseSeeder):
    def __init__(self, server_id: int | None = None):
        super().__init__(server_id=server_id)
        self.policy_repo: LocationPolicyRepository | None = None
        self.location_repo: LocationRepository | None = None
        self.poi_repo: PointOfInterestRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.policy_repo = await LocationPolicyRepository().get_instance()
        seeder.location_repo = await LocationRepository().get_instance()
        seeder.poi_repo = await PointOfInterestRepository().get_instance()
        return await seeder._seed()

    async def _seed(self) -> SeederResult:
        pois = await self.poi_repo.get_all(self.server_id)
        if not pois:
            return SeederResult(status="completed", inserted=0, failed=0)

        locations = []
        for poi in pois:
            locations.extend(await self.location_repo.get_all(poi_id=poi.poi_id))

        if not locations:
            return SeederResult(status="completed", inserted=0, failed=0)

        if await self.policy_repo.exists(locations[0].location_id):
            return SeederResult(status="skipped", reason="already seeded", inserted=0, failed=0)

        inserted = 0
        failed = 0

        async with self.policy_repo.transaction():
            for location in locations:
                try:
                    if await self.policy_repo.exists(location.location_id):
                        continue
                    policy = LocationPolicy(location_id=location.location_id)
                    policy_id = await self.policy_repo.insert(policy)
                    if not policy_id:
                        failed += 1
                    else:
                        inserted += 1
                except Exception:
                    failed += 1

        return SeederResult(status="completed", inserted=inserted, failed=failed)
