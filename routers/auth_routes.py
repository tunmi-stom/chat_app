from fastapi import APIRouter, Response, Depends, Request, HTTPException, status
from core.db_config import db_dependency
from schemas.users import UserLoginData, UserCreateData
from services.auth_services import AuthService
from core.dependency import get_current_user, security

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup")
def signup(db: db_dependency, data: UserCreateData):
    AuthService.user_signup(db, data)
    return {"detail": "User registered."}

@router.post("/login")
def login(db: db_dependency, data: UserLoginData, res: Response):
    token = AuthService.user_login(db, data, res)
    
    return {
        "detail": "Login Successful", 
        "token": token, 
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    db: db_dependency, 
    req: Request, 
    res: Response, 
    email: str = Depends(get_current_user)
):
    token = req.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token not found"
        )
    data = AuthService.user_logout(db, res, token)
    return {"detail": "Logout Successful", "data": data}