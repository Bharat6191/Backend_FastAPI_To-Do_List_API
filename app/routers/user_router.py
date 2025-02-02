import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..schemas.user_schemas import UserCreate, UserLogin
from ..schemas.user_schemas import UserRegistrationResponse, LoginResponse, ErrorResponse
from ..exceptions.user_exception import *
from ..jwt_auth.token_security import sign_jwt
from sqlmodel import Session, select
from ..models.user_model import User
from ..jwt_auth.token_validation import JWTBearer
from ..database import get_session
import re

router = APIRouter()

def is_strong_password(password: str) -> bool:
    if (
        len(password) >= 8
        and re.search(r"\d", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    ):
        return True
    else:
        raise WeakPasswordException()

def is_correct_username(username: str):
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise InvalidUsernameException()

@router.post("/register", response_model=UserRegistrationResponse, responses={
        400: {"description": "Bad Request", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },tags=['User']
)
def register(user: UserCreate, session: Session = Depends(get_session)):
    if not user.username or not user.password:
        raise UsernameAndPasswordRequired()
    is_correct_username(user.username)
    normalize_username = user.username.lower()
    is_strong_password(user.password)
    existing_user = session.exec(select(User).where(User.username == normalize_username)).first()
    if existing_user:
        raise UserAlreadyExistsException()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=normalize_username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserRegistrationResponse(id=str(new_user.id), username=new_user.username, message="User registered successfully.")

@router.post("/login", response_model=LoginResponse, responses={
        400: {"description": "Invalid Credentials", "model": ErrorResponse},
        404: {"description": "User Not Found", "model": ErrorResponse},
    },tags=['User']
)
def login(user: UserLogin, session: Session = Depends(get_session)):
    if not user.username or not user.password:
        raise UsernameAndPasswordRequired()
    normalize_username = user.username.lower()
    existing_user = session.exec(select(User).where(User.username == normalize_username)).first()
    if not existing_user:
        raise UserNotFoundException()
    if not bcrypt.checkpw(user.password.encode('utf-8'), existing_user.hashed_password.encode('utf-8')):
        raise InvalidCredentialsException()
    token = sign_jwt(str(existing_user.id))
    return LoginResponse(message="Login successful.", token=token)

