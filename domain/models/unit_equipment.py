class UnitEquipment:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.equipment_id: int|None = kwargs.get('equipment_id')
        self.unit_id: int|None = kwargs.get('unit_id')
        self.inventory_instance_id: int|None = kwargs.get('inventory_instance_id')
        self.slot: str|None = kwargs.get('slot')

    def to_dict(self):
        return {
            'equipment_id': self.equipment_id,
            'unit_id': self.unit_id,
            'inventory_instance_id': self.inventory_instance_id,
            'slot': self.slot
        }