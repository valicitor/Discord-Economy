class EquipmentStat:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.equipment_stat_id: int|None = kwargs.get('equipment_stat_id')
        self.equipment_id: int|None = kwargs.get('equipment_id')
        self.stat_key: str|None = kwargs.get('stat_key')
        self.stat_type: str|None = kwargs.get('stat_type')
        self.stat_value: str|None = kwargs.get('stat_value')

    def to_dict(self):
        return {
            'equipment_stat_id': self.equipment_stat_id,
            'equipment_id': self.equipment_id,
            'stat_key': self.stat_key,
            'stat_type': self.stat_type,
            'stat_value': self.stat_value
        }