class InsertFailedException(Exception):
    def __init__(self, message="failed to insert record."):
        self.message = message
        super().__init__(self.message)