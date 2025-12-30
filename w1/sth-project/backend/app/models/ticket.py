"""
Ticket 数据库模型
定义 Ticket 表结构和关联关系
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.database import Base


class Ticket(Base):
    """Ticket 数据模型"""
    
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tags = relationship("TicketTag", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, title='{self.title}', is_completed={self.is_completed})>"


class TicketTag(Base):
    """Ticket-Tag 关联表模型"""
    
    __tablename__ = "ticket_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    ticket = relationship("Ticket", back_populates="tags")
    tag = relationship("Tag", back_populates="tickets")
    
    def __repr__(self):
        return f"<TicketTag(ticket_id={self.ticket_id}, tag_id={self.tag_id})>"
