class Item:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.item_id: int|None = kwargs.get('item_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.name: str|None = kwargs.get('name')
        self.category: str|None = kwargs.get('category', 'default')
        self.reference_id: str|None = kwargs.get('reference_id')
        self.icon: str|None = kwargs.get('icon', '')
        self.price: int|None = kwargs.get('price', 0)
        self.description: str|None = kwargs.get('description', '')
        self.stock: int|None = kwargs.get('stock', -1)
        self.inventory: bool|None = kwargs.get('inventory', True)
        self.usable: bool|None = kwargs.get('usable', True)
        self.sellable: bool|None = kwargs.get('sellable', True)

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'server_id': self.server_id,
            'name': self.name,
            'category': self.category,
            'reference_id': self.reference_id,
            'icon': self.icon,
            'price': self.price,
            'description': self.description,
            'stock': self.stock,
            'inventory': self.inventory,
            'usable': self.usable,
            'sellable': self.sellable
        }