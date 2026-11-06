from sqlalchemy import String, Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from core.db_config import Base
from utils.enums import Roles

class RoomMembership(Base):
    __tablename__ = "room_membership"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("chat_users.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(String, ForeignKey("chat_rooms.room_id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default=Roles.USER.value)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "room_id",
            name="unique_room_membership"
        ),
    )