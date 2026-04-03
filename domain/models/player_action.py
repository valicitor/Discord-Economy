class PlayerAction:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.player_action_id: int|None = kwargs.get('player_action_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.type: int|None = kwargs.get('type')
        self.last_used_at: str|None = kwargs.get('last_used_at')

    def to_dict(self):
        return {
            'player_action_id': self.player_action_id,
            'player_id': self.player_id,
            'type': self.type,
            'last_used_at': self.last_used_at
        }