"""
Tag 数据库模型
定义 Tag 表结构和关联关系
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.database import Base


class Tag(Base):
    """Tag 数据模型"""
    
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(7), default="#0070f3", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    tickets = relationship("TicketTag", back_populates="tag", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', color='{self.color}')>"
