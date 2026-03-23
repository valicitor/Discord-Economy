from domain import IRepository

class IShopItemsRepository(IRepository):
    async def delete_all(self, guild_id: str):
        """Delete all shop items for a specific guild."""
        raise NotImplementedError("This method should be implemented by subclasses")