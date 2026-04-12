from domain import Equipment, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, EquipmentRepository


class EquipmentsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.repo: EquipmentRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.repo = await EquipmentRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "equipments_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "equipments" not in data or "data" not in data["equipments"]:
            raise SeederErrorException("Invalid equipments seed structure")

        records = data["equipments"]["data"]

        inserted = 0
        failed = 0

        async with self.repo.transaction():  # assumes repo supports this
            existing = await self.repo.get_all(self.server_id)
            if existing:
                return SeederResult(
                    status="skipped",
                    reason="already seeded",
                    inserted=0,
                    failed=0,
                )

            for r in records:
                try:
                    equipment = Equipment(data=r)
                    equipment.server_id = self.server_id

                    equipment_id = await self.repo.insert(equipment)
                    if not equipment_id:
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