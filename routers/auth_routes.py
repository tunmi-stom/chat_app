from fastapi import APIRouter, Response, Depends
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
def logout(db: db_dependency, res: Response, token: str = Depends(security)):
    data = AuthService.user_logout(db, res, token)
    return {"detail": "Logout Successful", "data": data}
    
