from domain import IRepository

class IGuildConfigRepository(IRepository):
    async def delete_all(self, guild_id: str):
        """Delete all guild config for a specific guild."""
        raise NotImplementedError("This method should be implemented by subclasses")