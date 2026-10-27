from pydantic_settings import BaseSettings
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cornet"
    API_VERSION: str = "0.1.0"
    API_V1_STR: str = "api/v1"
    
    DATABASE_URL: str = getenv("DATABASE_URL")
    JWT_SECRET: str = getenv("JWT_SECRET")
    JWT_ALGORITHM: str = getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_TIMEDELTA: int = 20
    
settings = Settings()