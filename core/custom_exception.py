from fastapi import HTTPException

class CustomAPIException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(status_code=status_code)
        self.code = code
        self.message = message
        self.details = details
