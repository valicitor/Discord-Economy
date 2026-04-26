class PlayerUnit:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.unit_id: int|None = kwargs.get('unit_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.name: str|None = kwargs.get('name')
        self.quantity: int|None = kwargs.get('quantity')
        self.metadata: dict = kwargs.get('metadata', {})

    def to_dict(self):
        return {
            'unit_id': self.unit_id,
            'player_id': self.player_id,
            'name': self.name,
            'quantity': self.quantity,
            'metadata': self.metadata
        }