from sqlalchemy import Column, Integer, func, TIMESTAMP
from sqlalchemy.sql import text
from app.db.base import Base


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
