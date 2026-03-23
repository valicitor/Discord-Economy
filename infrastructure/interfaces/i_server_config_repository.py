from domain import IRepository

class IServerConfigRepository(IRepository):
    async def delete_all(self, guild_id: str):
        """Delete all server config for a specific guild."""
        raise NotImplementedError("This method should be implemented by subclasses")