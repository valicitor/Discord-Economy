from domain import GuildConfig, Item
from domain import ItemNotFoundException
from infrastructure import ItemRepository
from application.helpers.ensure_user import ensure_guild

class CreateItemCommandRequest:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id: int = kwargs.get('guild_id')
        self.item: Item = kwargs.get('item')

class CreateItemCommandResponse:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.success: bool = kwargs.get('success')
        self.guild_config: GuildConfig = kwargs.get('guild_config')
        self.item: Item = kwargs.get('item')

class CreateItemCommand:

    def __init__(self, request: CreateItemCommandRequest):
        self.request = request
        return
    
    def execute(self) -> CreateItemCommandResponse:

        guild_config = ensure_guild(self.request.guild_id)
        
        success, item_id = ItemRepository().add(self.request.item)

        item_record = ItemRepository().get_by_id(self.request.item.guild_id, item_id)
        if item_record is None:
            raise ItemNotFoundException(f"Item with name {self.request.item.name} not found in guild {self.request.item.guild_id}.")
        
        return CreateItemCommandResponse(success=success, guild_config=guild_config, item=item_record)
