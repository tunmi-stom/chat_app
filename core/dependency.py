from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth.auth_handler import decode_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )
        
    email = payload.get("email")
    
    return email

def get_websocket_user(websocket: WebSocket) -> str:
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

    email = payload.get("email")

    if not email:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token does not contain an email."
        )

    return email