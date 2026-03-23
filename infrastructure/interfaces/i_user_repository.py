from domain import IRepository

class IUserRepository(IRepository):
    async def delete_all(self, guild_id: str):
        """Delete all users for a specific guild."""
        raise NotImplementedError("This method should be implemented by subclasses")