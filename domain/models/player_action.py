class PlayerAction:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.player_action_id: int|None = kwargs.get('player_action_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.action_id: int|None = kwargs.get('action_id')
        self.last_used_at: str|None = kwargs.get('last_used_at')

    def to_dict(self):
        return {
            'player_action_id': self.player_action_id,
            'player_id': self.player_id,
            'action_id': self.action_id,
            'last_used_at': self.last_used_at
        }