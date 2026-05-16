from domain import Item, SeederErrorException
from infrastructure import BaseSeeder, SeederResult, ItemRepository, BusinessRepository, CatalogueRepository


class ShopItemsSeeder(BaseSeeder):
    def __init__(self, server_id: int|None = None):
        super().__init__(server_id=server_id)
        self.repo: ItemRepository | None = None
        self.business_repo: BusinessRepository | None = None
        self.catalogue_repo: CatalogueRepository | None = None

    @classmethod
    async def seed(cls, server_id: int, seed_file: str | None = None) -> SeederResult:
        seeder = cls(server_id=server_id)
        seeder.repo = await ItemRepository().get_instance()
        seeder.business_repo = await BusinessRepository().get_instance()
        seeder.catalogue_repo = await CatalogueRepository().get_instance()

        file_path = seeder._resolve_seed_file(seed_file, "shop_items_seed.json")
        return await seeder._seed(file_path)

    async def _seed(self, seed_file: str) -> SeederResult:
        data = self._load_json(seed_file)

        if "items" not in data or "data" not in data["items"]:
            raise SeederErrorException("Invalid shop items seed structure")

        records = data["items"]["data"]

        inserted = 0
        failed = 0

        async with self.repo.transaction():
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
                    item = Item(data=r)
                    item.server_id = self.server_id

                    if r.get("business_name"):
                        business = await self.business_repo.get_by_name(r["business_name"], self.server_id)
                        if business:
                            item.business_id = business.business_id

                    if not item.catalogue_id and r.get("catalogue_name"):
                        catalogue = await self.catalogue_repo.get_by_name(r["catalogue_name"], self.server_id)
                        if catalogue:
                            item.catalogue_id = catalogue.catalogue_id

                    item_id = await self.repo.insert(item)
                    if not item_id:
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