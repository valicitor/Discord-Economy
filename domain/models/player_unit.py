class PlayerUnit:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.unit_id: int|None = kwargs.get('unit_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.name: str|None = kwargs.get('name')
        self.quantity: int|None = kwargs.get('quantity')
        self.custom: bool|None = kwargs.get('custom')
        self.metadata: dict = kwargs.get('metadata', {})
        self.last_updated_at: str|None = kwargs.get('last_updated_at')

    def to_dict(self):
        return {
            'unit_id': self.unit_id,
            'server_id': self.server_id,
            'player_id': self.player_id,
            'name': self.name,
            'quantity': self.quantity,
            'custom': self.custom,
            'metadata': self.metadata,
            'last_updated_at': self.last_updated_at,
        }