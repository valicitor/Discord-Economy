class RecipeInput:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.input_id: int|None = kwargs.get('input_id')
        self.recipe_id: int|None = kwargs.get('recipe_id')
        self.catalogue_id: int|None = kwargs.get('catalogue_id')
        self.quantity: int = kwargs.get('quantity', 1)

    def to_dict(self):
        return {
            'input_id': self.input_id,
            'recipe_id': self.recipe_id,
            'catalogue_id': self.catalogue_id,
            'quantity': self.quantity,
        }
