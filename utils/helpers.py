import secrets
from re import sub
from passlib.context import CryptContext

def generate_slug(string: str) -> str:
    # Let the slug be lowercase, trimmed, and replace spaces and special characters with hyphens
    string = string.lower().strip()
    
    # Get rid of any character that is not a letter, number, or hyphen
    string = sub(r'[^a-z0-9]+', '-', string)
    
    # Also remove any leading or trailing hyphens
    string = sub(r'(^-|-$)+', '', string)
    
    # return the slug
    return string
    
def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def generate_room_id(len: int):
    return secrets.token_urlsafe(len)