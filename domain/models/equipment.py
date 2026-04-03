class Equipment:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.equipment_id: int|None = kwargs.get('equipment_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.item_id: int|None = kwargs.get('item_id')
        self.name: str|None = kwargs.get('name')
        self.description: str|None = kwargs.get('description')
        self.slot: str|None = kwargs.get('slot')
        self.metadata: dict = kwargs.get('metadata', {})  # flexible traits
        
    def to_dict(self):
        return {
            'equipment_id': self.equipment_id,
            'server_id': self.server_id,
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'slot': self.slot,
            'metadata': self.metadata
        }