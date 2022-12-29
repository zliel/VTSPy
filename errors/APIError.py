
class APIError(Exception):
    def __init__(self, message, error_id):
        super().__init__(f"API Error {error_id}: {message}")
