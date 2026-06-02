from sqlalchemy import Column, Integer, String, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .base import BaseModel


class InterviewMessage(BaseModel):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # interviewer(面试官)/candidate(候选人)
    content = Column(Text, nullable=False)
    question_index = Column(Integer, nullable=True)
    score = Column(DECIMAL(3, 1), nullable=True)
    feedback = Column(Text, nullable=True)

    # 关联关系
    interview = relationship("Interview", back_populates="messages")
