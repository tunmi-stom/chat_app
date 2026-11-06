from pydantic import BaseModel, EmailStr

class TokenData(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    
class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int
    