class PlayerInventory:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.inventory_id: int|None = kwargs.get('inventory_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.item_id: int|None = kwargs.get('item_id')
        self.quantity: int = kwargs.get('quantity', 1)

    def to_dict(self):
        return {
            'inventory_id': self.inventory_id,
            'player_id': self.player_id,
            'item_id': self.item_id,
            'quantity': self.quantity
        }