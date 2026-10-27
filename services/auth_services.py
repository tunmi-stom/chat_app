from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from schemas.users import UserCreateData, UserLoginData
from schemas.tokens import TokenData
from utils.helpers import hash_password, verify_password
from utils.enums import Roles
from auth.auth_handler import create_access_token

class AuthService:
    @staticmethod
    def user_signup(db: Session, data: UserCreateData):
        # Check if user exists
        db_user = db.query(User).filter(User.email == data.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User already exists"
            )
        
        # Create new user
        new_user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=True
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occured while adding user."
            )
    
    @staticmethod
    def user_login(db: Session, data: UserLoginData):
        # Check if user exists
        user = db.query(User).filter(User.email == data.email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot find user"
            )
        # Return error for an incorrect password
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Password"
            )
        
        token_data = TokenData(
            username=user.username,
            email=data.email
        )
        token = create_access_token(token_data)
        
        return token
    
    @staticmethod
    def user_logout(db: Session, token: str):
        pass
        
        