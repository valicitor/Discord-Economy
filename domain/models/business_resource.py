class BusinessInventory:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.inventory_id: int|None = kwargs.get('inventory_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.quantity: int = kwargs.get('quantity', 0)
        self.last_updated_at: str|None = kwargs.get('last_updated_at')

    def to_dict(self):
        return {
            'inventory_id': self.inventory_id,
            'server_id': self.server_id,
            'business_id': self.business_id,
            'catalogue_id': self.catalogue_id,
            'quantity': self.quantity,
            'last_updated_at': self.last_updated_at,
        }
