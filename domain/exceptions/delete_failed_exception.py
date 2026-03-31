class DeleteFailedException(Exception):
    def __init__(self, message="failed to delete record."):
        self.message = message
        super().__init__(self.message)