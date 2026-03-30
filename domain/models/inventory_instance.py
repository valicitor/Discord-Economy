class InventoryInstance:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.instance_id: int|None = kwargs.get('instance_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.item_id: int|None = kwargs.get('item_id')
        self.metadata: dict = kwargs.get('metadata', {})

    def to_dict(self):
        return {
            'instance_id': self.instance_id,
            'player_id': self.player_id,
            'item_id': self.item_id,
            'metadata': self.metadata
        }