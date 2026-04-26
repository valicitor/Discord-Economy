class Business:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.business_id: int|None = kwargs.get('business_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.owner_id: int|None = kwargs.get('owner_id')
        self.name: str|None = kwargs.get('name')
        self.description: str|None = kwargs.get('description')
        self.type: str|None = kwargs.get('type')
        self.x: int|None = kwargs.get('x')
        self.y: int|None = kwargs.get('y')
        self.range: int|None = kwargs.get('range')
        self.metadata: dict = kwargs.get('metadata', {})  # flexible traits

    def to_dict(self):
        return {
            'business_id': self.business_id,
            'server_id': self.server_id,
            'owner_id': self.owner_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'range': self.range,
            'metadata': self.metadata
        }