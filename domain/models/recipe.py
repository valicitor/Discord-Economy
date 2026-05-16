class Recipe:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.recipe_id: int|None = kwargs.get('recipe_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.name: str|None = kwargs.get('name')
        self.output_type: str|None = kwargs.get('output_type')
        self.output_resource_type: str|None = kwargs.get('output_resource_type')
        self.output_catalogue_id: int|None = kwargs.get('output_catalogue_id')
        self.output_quantity: int = kwargs.get('output_quantity', 1)

    def to_dict(self):
        return {
            'recipe_id': self.recipe_id,
            'business_id': self.business_id,
            'name': self.name,
            'output_type': self.output_type,
            'output_resource_type': self.output_resource_type,
            'output_catalogue_id': self.output_catalogue_id,
            'output_quantity': self.output_quantity,
        }
