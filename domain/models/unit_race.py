class UnitRace:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.race_id: int|None = kwargs.get('race_id')
        self.unit_id: int|None = kwargs.get('unit_id')
        self.inventory_instance_id: int|None = kwargs.get('inventory_instance_id')
        self.slot: str|None = kwargs.get('slot')

    def to_dict(self):
        return {
            'race_id': self.race_id,
            'unit_id': self.unit_id,
            'inventory_instance_id': self.inventory_instance_id,
            'slot': self.slot
        }