from fastapi import APIRouter
from core.db_config import db_dependency
from schemas.users import UserLoginData, UserCreateData
from services.auth_services import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup")
def signup(db: db_dependency, data: UserCreateData):
    AuthService.user_signup(db, data)
    return {"detail": "User registered."}

@router.post("/login")
def login(db: db_dependency, data: UserLoginData):
    token = AuthService.user_login(db, data)
    return {
        "detail": "Login Successful", 
        "token": token, 
        "token_type": "bearer"
    }
    
