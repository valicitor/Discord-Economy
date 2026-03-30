from dataclasses import dataclass

from domain import GuildConfig, Item
from domain import ItemNotFoundException, ItemCreationFailedException
from infrastructure import ItemRepository
from application.helpers.ensure_user import ensure_guild

@dataclass
class CreateItemCommandRequest:
    guild_id: int
    item: Item

@dataclass
class CreateItemCommandResponse:
    success: bool
    guild_config: GuildConfig
    item: Item

class CreateItemCommand:

    def __init__(self, request: CreateItemCommandRequest):
        self.request = request
        return
    
    def execute(self) -> CreateItemCommandResponse:

        guild_config = ensure_guild(self.request.guild_id)
        
        success, item_id = ItemRepository().add(self.request.item)
        if not success or item_id is None:
            raise ItemCreationFailedException("Failed to create item. Please try again.")

        item_record = ItemRepository().get_by_id(guild_config.guild_id, item_id)
        if item_record is None:
            raise ItemNotFoundException(f"Item with name {self.request.item.name} not found in guild {guild_config.guild_id}.")
        
        return CreateItemCommandResponse(success=success, guild_config=guild_config, item=item_record)
