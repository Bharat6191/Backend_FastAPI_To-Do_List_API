from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from ..jwt_auth.token_security import decode_jwt

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials and credentials.scheme == "Bearer":
            token_payload = self.verify_jwt(credentials.credentials)
            if not token_payload:
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            return token_payload
        raise HTTPException(status_code=403, detail="Invalid authorization code")

    def verify_jwt(self, token: str) -> Optional[dict]:
        payload = decode_jwt(token)
        return payload if payload else None # type: ignore