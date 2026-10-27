from pydantic import BaseModel, EmailStr, ConfigDict
from utils.enums import Roles

class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    is_active: bool
    bio: str
    
class UserCreateData(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginData(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    username: str
    email: EmailStr
    bio: str | None = None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
    
class UserUpdateData(BaseModel):
    username: str | None = None
    password: str | None = None
    bio: str | None = None