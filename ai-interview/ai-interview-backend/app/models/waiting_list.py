from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP
from .base import BaseModel


class WaitingList(BaseModel):
    __tablename__ = "waiting_list"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    university = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)