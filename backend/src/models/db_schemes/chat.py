from ...config import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text,Index
from sqlalchemy.orm import relationship
from sqlalchemy import func

class Chat(SQLAlchemyBase):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pdf_id = Column(Integer, ForeignKey("pdfs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    summary = Column(Text, nullable=True)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    pdf = relationship("PDF", back_populates="chats")

    __table_args__ = (
        Index("ix_chats_user_created_at", "user_id", "created_at"),

    )
