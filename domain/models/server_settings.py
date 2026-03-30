class ServerSetting:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.setting_id: int|None = kwargs.get('setting_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.key: str|None = kwargs.get('key')
        self.value: str|None = kwargs.get('value')

    def to_dict(self):
        return {
            'setting_id': self.setting_id,
            'server_id': self.server_id,
            'key': self.key,
            'value': self.value
        }