class Faction:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.faction_id: int|None = kwargs.get('faction_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.owner_id: int|None = kwargs.get('owner_id')
        self.name: str|None = kwargs.get('name')
        self.color: str|None = kwargs.get('color')

    def to_dict(self):
        return {
            'faction_id': self.faction_id,
            'server_id': self.server_id,
            'owner_id': self.owner_id,
            'name': self.name,
            'color': self.color
        }