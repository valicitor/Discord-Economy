class UnitGarrison:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.garrison_id: int|None = kwargs.get('garrison_id')
        self.unit_id: int|None = kwargs.get('unit_id')
        self.poi_id: int|None = kwargs.get('poi_id')
        self.assigned_at: str|None = kwargs.get('assigned_at')

    def to_dict(self):
        return {
            'garrison_id': self.garrison_id,
            'unit_id': self.unit_id,
            'poi_id': self.poi_id,
            'assigned_at': self.assigned_at
        }