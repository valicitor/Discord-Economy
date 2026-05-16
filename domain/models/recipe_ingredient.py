class RecipeIngredient:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.ingredient_id: int|None = kwargs.get('ingredient_id')
        self.recipe_id: int|None = kwargs.get('recipe_id')
        self.resource_type: str|None = kwargs.get('resource_type')
        self.quantity: int = kwargs.get('quantity', 1)

    def to_dict(self):
        return {
            'ingredient_id': self.ingredient_id,
            'recipe_id': self.recipe_id,
            'resource_type': self.resource_type,
            'quantity': self.quantity,
        }
