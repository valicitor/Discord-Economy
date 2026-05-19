class Recipe:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.recipe_id: int|None = kwargs.get('recipe_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.name: str|None = kwargs.get('name')

    def to_dict(self):
        return {
            'recipe_id': self.recipe_id,
            'server_id': self.server_id,
            'name': self.name,
        }
