class RecipeOutput:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.output_id: int|None = kwargs.get('output_id')
        self.recipe_id: int|None = kwargs.get('recipe_id')
        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.quantity: int = kwargs.get('quantity', 1)

    def to_dict(self):
        return {
            'output_id': self.output_id,
            'recipe_id': self.recipe_id,
            'catalogue_id': self.catalogue_id,
            'quantity': self.quantity,
        }
