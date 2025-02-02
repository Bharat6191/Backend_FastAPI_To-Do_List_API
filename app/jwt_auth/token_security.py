import time
import jwt
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
load_dotenv()
JWT_SECRET = str(os.getenv("secret"))
JWT_ALGORITHM = str(os.getenv("algorithm"))

def sign_jwt(user_id: str):
    payload={
        "user_id":user_id,
        "expires":time.time()+600
    }
    token=jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    return str(token)

def decode_jwt(token:str):
    try:
        decoded_token=jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
