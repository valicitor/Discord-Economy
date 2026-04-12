from domain import Action, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, BusinessRepository, ActionRepository


class ActionsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.business_repo: BusinessRepository | None = None
        self.action_repo: ActionRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.business_repo = await BusinessRepository().get_instance()
        seeder.action_repo = await ActionRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "businesses_seed.json")
        return await seeder._seed(file_path)
 
    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "actions" not in data or "data" not in data["actions"]:
            raise SeederErrorException("Invalid actions seed structure")

        records = data["actions"]["data"]

        inserted = 0
        skipped = 0
        failed = 0

        async with self.action_repo.transaction():
            for action in records:
                try:
                    business = await self.business_repo.get_by_name(
                        action["business_name"], self.server_id
                    )

                    if not business:
                        skipped += 1
                        continue

                    entity = Action(data=action)
                    entity.business_id=business.business_id

                    action_id = await self.action_repo.insert(entity)
                    if not action_id:
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