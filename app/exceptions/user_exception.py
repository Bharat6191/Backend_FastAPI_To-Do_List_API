from fastapi import HTTPException

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExistsException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="A user with the provided username already exists. Please choose a different username.",
            error_code="USER_ALREADY_EXISTS"
        )

class InvalidUsernameException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="The username contains invalid characters. It must only contain letters, numbers, and underscores.",
            error_code="INVALID_USERNAME"
        )

class InvalidRoleException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="The provided role is not valid. User role must be either 'admin' or 'user'.",
            error_code="INVALID_ROLE"
        )

class WeakPasswordException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Password is too weak. Must contain at least 8 characters, including digits, letters, and special characters.",
            error_code="WEAK_PASSWORD"
        )

class UserNotFoundException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="The specified user could not be found. Please check the username and try again.",
            error_code="USER_NOT_FOUND"
        )

class InvalidCredentialsException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="The username or password provided is incorrect. Please verify the credentials and try again.",
            error_code="INVALID_CREDENTIALS"
        )

class UsernameAndPasswordRequired(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Both username and password are required for this operation. Please provide both to proceed.",
            error_code="USERNAME_AND_PASSWORD_REQUIRED"
        )
