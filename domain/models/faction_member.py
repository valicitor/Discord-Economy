class FactionMember:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.member_id: int|None = kwargs.get('member_id')
        self.faction_id: int|None = kwargs.get('faction_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.role: str|None = kwargs.get('role')
        self.joined_at: str|None = kwargs.get('joined_at')

    def to_dict(self):
        return {
            'member_id': self.member_id,
            'faction_id': self.faction_id,
            'player_id': self.player_id,
            'role': self.role,
            'joined_at': self.joined_at
        }