class RaceStat:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.race_stat_id: int|None = kwargs.get('race_stat_id')
        self.race_id: int|None = kwargs.get('race_id')
        self.stat_key: str|None = kwargs.get('stat_key')
        self.stat_value: str|None = kwargs.get('stat_value', "0")

    def to_dict(self):
        return {
            'race_stat_id': self.race_stat_id,
            'race_id': self.race_id,
            'stat_key': self.stat_key,
            'stat_value': self.stat_value
        }