from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

class CookieBearer(HTTPBearer):
    async  def __call__(self, req: Request):
        token = req.cookies.get("access_token")
        
        if not token:
            authorization = req.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer"):
                token = authorization.split(" ", 1)[1]
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated."
            )
        
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )