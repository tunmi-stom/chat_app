from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from models.user import User
from schemas.users import UserCreateData, UserLoginData
from schemas.tokens import TokenData
from models.token import RevokedToken
from utils.helpers import hash_password, verify_password
# from utils.enums import Roles
from auth.auth_handler import create_access_token, decode_token

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
    def user_login(
        db: Session, 
        data: UserLoginData, 
        # feat: Implementation of HttpOnly cookies
        res: Response
    ):
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
        
        res.set_cookie(
                key="access_token",
                value=token,
                secure=False, # tunmi_stom, remember to set this to True when deploying 
                httponly=True,
                samesite="lax",
                max_age=1200,
                path="/"
            )
        
        return token
    
    @staticmethod
    def user_logout(db: Session, res: Response, token: str):

        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token."
            )

        jti = payload["jti"]
        email = payload["email"]
        exp = payload["exp"]

        if not all([jti, email, exp]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload."
            )

        user = db.query(User).filter(
            User.email == email
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        existing_token = db.query(RevokedToken).filter(
            RevokedToken.jti == jti
        ).first()

        if existing_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token already revoked."
            )

        revoked_token = RevokedToken(
            jti=jti,
            expires_at=datetime.fromtimestamp(
                exp,
                tz=timezone.utc
            ),
            user_id=user.id
        )

        try:
            db.add(revoked_token)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not revoke token. Database error."
            )

        res.delete_cookie(
            key="access_token",
            httponly=True,
            secure=False,
            samesite="lax"
        )

        return