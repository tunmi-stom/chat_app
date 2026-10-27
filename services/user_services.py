from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.room import Room
from models.user import User
from utils.helpers import generate_room_id, hash_password
from schemas.rooms import RoomCreateData
from schemas.users import UserResponse, UserUpdateData

class UserService:
    @staticmethod
    def dashboard(db: Session, email: str):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exists"
            )
            
        return UserResponse.model_validate(user)
    
    @staticmethod
    def update_profile(db: Session, email: str, data: UserUpdateData):
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exists"
            )
            
        # Update fields if they are provided
        if data.username != None:
            user.username = data.username
        if data.bio != None:
            user.bio = data.bio
        if data.password != None:
            user.hashed_password = hash_password(data.password)
            
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user."
            )
            
        return UserResponse.model_validate(user)
    
    @staticmethod
    def get_user(db: Session, username: str):
        # Check if user exists
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exists"
            )
            
        return UserResponse.model_validate(db_user)
                    
        