from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db_config import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("chat_users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, server_default=func.now())