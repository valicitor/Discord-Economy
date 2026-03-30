class ActionLog:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.log_id: int|None = kwargs.get('log_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.action_id: int|None = kwargs.get('action_id')
        self.target_player_id: int|None = kwargs.get('target_player_id')
        self.success: bool = kwargs.get('success', True)
        self.reward_amount: int = kwargs.get('reward_amount', 0)
        self.penalty_amount: int = kwargs.get('penalty_amount', 0)
        self.result_data: dict = kwargs.get('result_data', {})
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'player_id': self.player_id,
            'action_id': self.action_id,
            'target_player_id': self.target_player_id,
            'success': self.success,
            'reward_amount': self.reward_amount,
            'penalty_amount': self.penalty_amount,
            'result_data': self.result_data,
            'created_at': self.created_at
        }