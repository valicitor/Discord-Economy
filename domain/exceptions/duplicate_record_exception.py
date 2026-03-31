class DuplicateRecordException(Exception):
    def __init__(self, message="Duplicate record found."):
        self.message = message
        super().__init__(self.message)