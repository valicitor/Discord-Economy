from domain import EquipmentStat, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, EquipmentRepository, EquipmentStatRepository


class EquipmentStatsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.equipment_repo: EquipmentRepository | None = None
        self.stat_repo: EquipmentStatRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.equipment_repo = await EquipmentRepository().get_instance()
        seeder.stat_repo = await EquipmentStatRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "equipments_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "equipment_stats" not in data or "data" not in data["equipment_stats"]:
            raise SeederErrorException("Invalid equipment_stats seed structure")

        records = data["equipment_stats"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.stat_repo.transaction():
            for stat in records:
                try:
                    equipment = await self.equipment_repo.get_by_name(
                        stat["equipment_name"], self.server_id
                    )

                    if not equipment:
                        skipped += 1
                        continue

                    entity = EquipmentStat(data=stat)
                    entity.equipment_id=equipment.equipment_id

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