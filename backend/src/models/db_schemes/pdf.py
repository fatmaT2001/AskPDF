from ...config import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from typing import List, Optional
from sqlalchemy import func

class PDF(SQLAlchemyBase):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)

    user = relationship("User", back_populates="pdfs")
    chats = relationship("Chat", back_populates="pdf", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_pdfs_user_uploaded_at", "user_id", "uploaded_at"),
    )