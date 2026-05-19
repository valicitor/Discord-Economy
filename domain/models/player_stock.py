class PlayerStock:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.player_stock_id: int|None = kwargs.get('player_stock_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.quantity: int = kwargs.get('quantity', 0)
        self.last_updated_at: str|None = kwargs.get('last_updated_at')

    def to_dict(self):
        return {
            'player_stock_id': self.player_stock_id,
            'server_id': self.server_id,
            'player_id': self.player_id,
            'business_id': self.business_id,
            'quantity': self.quantity,
            'last_updated_at': self.last_updated_at,
        }
