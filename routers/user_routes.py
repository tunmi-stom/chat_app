from fastapi import APIRouter, Depends
from core.db_config import db_dependency
from core.dependency import get_current_user
from services.user_services import UserService
from schemas.users import UserUpdateData

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/profile")
def profile(db: db_dependency, email: str = Depends(get_current_user)):
    user = UserService.dashboard(db, email)
    return {"detail": user}

@router.get("/{username}")
def get_user(db: db_dependency, username: str):
    user = UserService.get_user(db, username)
    return {"detail": user}

@router.patch("/update-profile")
def update_profile(db: db_dependency, data: UserUpdateData, email: str = Depends(get_current_user)):
    user = UserService.update_profile(db, email, data)
    return {"detail": user}
    