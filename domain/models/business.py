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
        self.location: str|None = kwargs.get('location')
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
            'location': self.location,
            'range': self.range,
            'metadata': self.metadata
        }