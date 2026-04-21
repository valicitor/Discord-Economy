class Catalogue:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.name: str|None = kwargs.get('name')
        self.type: str|None = kwargs.get('type', 'general')  # e.g., general, shop, crafting
        self.description: str|None = kwargs.get('description', '')
        self.status: str|None = kwargs.get('status', 'active')  # e.g., active, archived
        self.metadata: dict = kwargs.get('metadata', {})  # flexible traits

    def to_dict(self):
        return {
            'catalogue_id': self.catalogue_id,
            'server_id': self.server_id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'status': self.status,
            'metadata': self.metadata
        }