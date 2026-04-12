class SeederErrorException(Exception):
    def __init__(self, message="failed to seed data."):
        self.message = message
        super().__init__(self.message)