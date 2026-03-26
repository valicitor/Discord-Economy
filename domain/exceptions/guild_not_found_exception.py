class GuildNotFoundException(Exception):
    def __init__(self, message="Guild not found."):
        self.message = message
        super().__init__(self.message)