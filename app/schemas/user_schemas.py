from pydantic import BaseModel, EmailStr
import re
class UserCreate(BaseModel):
    username: str
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegistrationResponse(BaseModel):
    id: str
    username: str
    message: str

class LoginResponse(BaseModel):
    message: str
    token: str

class ErrorResponse(BaseModel):
    detail: str