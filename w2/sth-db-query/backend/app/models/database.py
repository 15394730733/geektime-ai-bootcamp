"""
Database connection models for SQLAlchemy.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from . import Base


class DatabaseConnection(Base):
    """Database connection model."""

    __tablename__ = "database_connections"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    db_metadata = relationship("DatabaseMetadata", back_populates="connection", cascade="all, delete-orphan")
    query_executions = relationship("QueryExecution", back_populates="connection", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DatabaseConnection(id='{self.id}', name='{self.name}', is_active={self.is_active})>"
