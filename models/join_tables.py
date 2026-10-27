from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from core.db_config import Base

class RoomParticipants(Base):
    __tablename__ = "room_participants"
    
    user_id = Column(Integer, ForeignKey("chat_users.id", ondelete="CASCADE"), primary_key=True)
    room_id_int = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)