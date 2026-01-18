"""
Database metadata models for SQLAlchemy.
"""

import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from . import Base


class DatabaseMetadata(Base):
    """Database metadata model for caching table/view information."""

    __tablename__ = "database_metadata"

    id = Column(String, primary_key=True, index=True)
    connection_id = Column(String, ForeignKey("database_connections.id"), nullable=False, index=True)
    object_type = Column(Enum("table", "view", name="object_type"), nullable=False)
    schema_name = Column(String, nullable=False, default="public")
    object_name = Column(String, nullable=False, index=True)
    columns = Column(Text, nullable=False)  # JSON string containing column definitions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to DatabaseConnection
    connection = relationship("DatabaseConnection", back_populates="db_metadata")

    def get_columns(self) -> List[dict]:
        """Parse and return the columns as a list of dictionaries."""
        return json.loads(self.columns)

    def set_columns(self, columns: List[dict]) -> None:
        """Set the columns from a list of dictionaries."""
        self.columns = json.dumps(columns, ensure_ascii=False)

    def __repr__(self) -> str:
        return f"<DatabaseMetadata(id='{self.id}', connection_id='{self.connection_id}', object_name='{self.object_name}')>"
