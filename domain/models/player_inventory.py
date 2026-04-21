class PlayerInventory:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.inventory_id: int|None = kwargs.get('inventory_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.status: str|None = kwargs.get('status', 'active')  # e.g., active, equipped, stored, etc.
        self.quantity: int = kwargs.get('quantity', 1)

    def to_dict(self):
        return {
            'inventory_id': self.inventory_id,
            'player_id': self.player_id,
            'catalogue_id': self.catalogue_id,
            'status': self.status,
            'quantity': self.quantity
        }