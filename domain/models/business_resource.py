class BusinessResource:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.resource_id: int|None = kwargs.get('resource_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.resource_type: str|None = kwargs.get('resource_type')
        self.quantity: int = kwargs.get('quantity', 0)
        self.required_quantity: int = kwargs.get('required_quantity', 0)

    def to_dict(self):
        return {
            'resource_id': self.resource_id,
            'business_id': self.business_id,
            'resource_type': self.resource_type,
            'quantity': self.quantity,
            'required_quantity': self.required_quantity,
        }
