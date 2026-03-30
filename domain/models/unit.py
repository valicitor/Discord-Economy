class Unit:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.unit_id: int|None = kwargs.get('unit_id')
        self.name: str|None = kwargs.get('name')
        self.description: str|None = kwargs.get('description')
        self.metadata: dict = kwargs.get('metadata', {})  # flexible traits

    def to_dict(self):
        return {
            'unit_id': self.unit_id,
            'name': self.name,
            'description': self.description,
            'metadata': self.metadata
        }