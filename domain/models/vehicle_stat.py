class VehicleStat:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.vehicle_stat_id: int|None = kwargs.get('vehicle_stat_id')
        self.vehicle_id: int|None = kwargs.get('vehicle_id')
        self.stat_key: str|None = kwargs.get('stat_key')
        self.stat_type: str|None = kwargs.get('stat_type')
        self.stat_value: str|None = kwargs.get('stat_value')

    def to_dict(self):
        return {
            'vehicle_stat_id': self.vehicle_stat_id,
            'vehicle_id': self.vehicle_id,
            'stat_key': self.stat_key,
            'stat_type': self.stat_type,
            'stat_value': self.stat_value
        }