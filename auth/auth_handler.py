from uuid import uuid4
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from core.config import settings
from schemas.tokens import TokenData
from typing import Any

def create_access_token(data: TokenData) -> str:
    expire_delta = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_TIMEDELTA)
    
    payload = {
        "sub": data.username,
        "jti": str(uuid4()),
        "iat": datetime.utcnow(),
        "exp": expire_delta,
        "email": data.email
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    
    return token

def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        return payload        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    