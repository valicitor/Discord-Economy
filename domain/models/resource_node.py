class ResourceNode:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.node_id: int|None = kwargs.get('node_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.location_id: int|None = kwargs.get('location_id')
        self.resource_type: str|None = kwargs.get('resource_type')
        self.quantity: int = kwargs.get('quantity', 0)
        self.max_quantity: int = kwargs.get('max_quantity', 100)
        self.regen_rate: int = kwargs.get('regen_rate', 5)
        self.discovered: bool = bool(kwargs.get('discovered', False))
        self.last_updated_at: str|None = kwargs.get('last_updated_at')

    def to_dict(self):
        return {
            'node_id': self.node_id,
            'server_id': self.server_id,
            'location_id': self.location_id,
            'resource_type': self.resource_type,
            'quantity': self.quantity,
            'max_quantity': self.max_quantity,
            'regen_rate': self.regen_rate,
            'discovered': self.discovered,
            'last_updated_at': self.last_updated_at,
        }
