from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from core.db_config import Base

class User(Base):
    __tablename__ = "chat_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    
    room = relationship("Room", secondary="room_participants", back_populates="participants")