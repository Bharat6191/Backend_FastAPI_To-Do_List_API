from fastapi import HTTPException

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "GENERIC_ERROR"):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail={"error_code": error_code, "message": detail})
class TitleIsMandatory(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Title is Mandatory",
            error_code="TITLE_IS_MANDATORY"
        )
class TitleLengthExceed(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Title length should be less than 100 characters",
            error_code="TITLE_LENGTH_SHOULD_BE_LESS_THAN_100"
        )
class TaskAlreadyExists(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="A task with this title already exists.",
            error_code="TASK_ALREADY_EXISTS"
        )
class UserNotFound(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="User not found.",
            error_code="USER_NOT_FOUND"
        )
class UnauthorizedAccess(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="User ID not found in token. Unauthorized access.",
            error_code="UNAUTHORIZED_ACCESS"
        )
class DatabaseError(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="An error occurred with the database.",
            error_code="DATABASE_ERROR"
        )
class TaskNotFound(Exception):
    def __init__(self, message: str = "No tasks found"):
        self.message = message
        super().__init__(self.message)
class ValidationError(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Validation error.",
            error_code="VALIDATION_ERROR"
        )
class InternalServerError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail={"message": detail, "error_code": "INTERNAL_SERVER_ERROR"})
class InvalidToken(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=401,  # Unauthorized due to invalid token
            detail="Invalid or expired token.",
            error_code="INVALID_TOKEN"
        )
class GeneralError(BaseAPIException):
    def __init__(self, message: str = "An unexpected error occurred."):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="GENERAL_ERROR"
        )