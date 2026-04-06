class Location:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.location_id: int|None = kwargs.get('location_id')
        self.poi_id: int|None = kwargs.get('poi_id')
        self.name: str|None = kwargs.get('name')
        self.type: str|None = kwargs.get('type')
        self.x: float = kwargs.get('x', 0.0)
        self.y: float = kwargs.get('y', 0.0)
        self.owner_player_id: int|None = kwargs.get('owner_player_id')

    def to_dict(self):
        return {
            'location_id': self.location_id,
            'poi_id': self.poi_id,
            'name': self.name,
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'owner_player_id': self.owner_player_id
        }