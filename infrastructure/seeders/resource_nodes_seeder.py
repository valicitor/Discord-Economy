from domain import ResourceNode, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, ResourceNodeRepository, LocationRepository


class ResourceNodesSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.node_repo: ResourceNodeRepository | None = None
        self.location_repo: LocationRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.node_repo = await ResourceNodeRepository().get_instance()
        seeder.location_repo = await LocationRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "resource_nodes_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "resource_nodes" not in data or "data" not in data["resource_nodes"]:
            raise SeederErrorException("Invalid resource nodes seed structure")

        records = data["resource_nodes"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.node_repo.transaction():
            existing = await self.node_repo.get_all()
            if existing:
                return SeederResult(
                    status="skipped",
                    reason="already seeded",
                    inserted=0,
                    failed=0,
                )

            for r in records:
                try:
                    location = await self.location_repo.get_by_name(r["location_name"], self.server_id)
                    if not location:
                        skipped += 1
                        continue

                    node = ResourceNode(data=r)
                    node.server_id = self.server_id
                    node.location_id = location.location_id

                    node_id = await self.node_repo.insert(node)
                    if not node_id:
                        failed += 1
                    else:
                        inserted += 1
                except Exception:
                    failed += 1

        return SeederResult(
            status="completed",
            inserted=inserted,
            failed=failed,
        )
