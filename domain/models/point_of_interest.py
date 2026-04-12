class PointOfInterest:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.poi_id: int|None = kwargs.get('poi_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.name: str|None = kwargs.get('name')
        self.icon: str|None = kwargs.get('icon')
        self.size: float = kwargs.get('size', 0.0)

    def to_dict(self):
        return {
            'poi_id': self.poi_id,
            'server_id': self.server_id,
            'name': self.name,
            'icon': self.icon,
            'size': self.size
        }