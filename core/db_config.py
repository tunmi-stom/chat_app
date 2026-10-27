from typing import Annotated
from fastapi import Depends
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
    
Base = declarative_base()

db_dependency = Annotated[Session, Depends(get_db)]