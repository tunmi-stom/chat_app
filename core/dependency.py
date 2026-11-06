from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth.auth_handler import decode_token
from auth.auth_bearer import CookieBearer
from core.db_config import get_db
from models.token import RevokedToken

security = CookieBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )
    
    # token identifier
    jti: str = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Broken token."
        )
        
    revoked_token = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if revoked_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is revoked"
        )
        
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain an email."
        )
    
    return email

def get_websocket_user(
    websocket: WebSocket, 
    db: Session = Depends(get_db)
) -> str:
    token = websocket.cookies.get("access_token")

    if not token:
        token = websocket.query_params.get("token")
        
    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing authentication token."
        )

    payload = decode_token(token)
    if payload is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token."
        )

    # token identifier
    jti: str = payload.get("jti")
    if not jti:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Broken token."
        )
        
    revoked_token = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if revoked_token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token is revoked"
        )
        
    email = payload.get("email")
    if not email:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token does not contain an email."
        )

    return email