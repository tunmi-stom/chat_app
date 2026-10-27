from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.db_config import Base

class Room(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    room_id = Column(String, unique=True)
    desc = Column(Text, nullable=True)
    max_participants = Column(Integer, default=2)
    owner_id = Column(Integer, ForeignKey("chat_users.id"), nullable=True)
    hashed_pass_key = Column(String)
    is_active = Column(Boolean, default=True)
    
    participants = relationship("User", secondary="room_participants", back_populates="room")