class Transport:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.transport_id: int|None = kwargs.get('transport_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.from_business_id: int|None = kwargs.get('from_business_id')
        self.to_business_id: int|None = kwargs.get('to_business_id')
        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.quantity: int = kwargs.get('quantity', 0)
        self.status: str = kwargs.get('status', 'in_transit')  # in_transit, arrived, cancelled
        self.created_at: str|None = kwargs.get('created_at')
        self.arrive_at: str|None = kwargs.get('arrive_at')

    def to_dict(self):
        return {
            'transport_id': self.transport_id,
            'server_id': self.server_id,
            'player_id': self.player_id,
            'from_business_id': self.from_business_id,
            'to_business_id': self.to_business_id,
            'catalogue_id': self.catalogue_id,
            'quantity': self.quantity,
            'status': self.status,
            'created_at': self.created_at,
            'arrive_at': self.arrive_at,
        }
