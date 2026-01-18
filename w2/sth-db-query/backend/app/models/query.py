"""
Query execution models for SQLAlchemy.
"""

import json
from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from . import Base


class QueryExecution(Base):
    """Query execution model."""

    __tablename__ = "query_executions"

    id = Column(String, primary_key=True, index=True)
    connection_id = Column(String, ForeignKey("database_connections.id"), nullable=False, index=True)
    query_type = Column(Enum("manual", "natural_language", name="query_type"), nullable=False)
    original_input = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    final_sql = Column(Text, nullable=False)
    execution_status = Column(
        Enum("pending", "success", "error", "timeout", name="execution_status"),
        nullable=False,
        default="pending"
    )
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    result_row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    connection = relationship("DatabaseConnection", back_populates="query_executions")
    result = relationship("QueryResult", back_populates="query", uselist=False)

    def __repr__(self) -> str:
        return f"<QueryExecution(id='{self.id}', status='{self.execution_status}', type='{self.query_type}')>"


class QueryResult(Base):
    """Query result model."""

    __tablename__ = "query_results"

    id = Column(String, primary_key=True, index=True)
    query_id = Column(String, ForeignKey("query_executions.id"), nullable=False, unique=True)
    columns = Column(Text, nullable=False)  # JSON string containing column names
    rows = Column(Text, nullable=False)     # JSON string containing row data
    truncated = Column(String, nullable=False, default="false")  # Store as string for SQLite compatibility

    # Relationship to QueryExecution
    query = relationship("QueryExecution", back_populates="result")

    def get_columns(self) -> List[str]:
        """Parse and return the columns as a list."""
        return json.loads(self.columns)

    def set_columns(self, columns: List[str]) -> None:
        """Set the columns from a list."""
        self.columns = json.dumps(columns, ensure_ascii=False)

    def get_rows(self) -> List[List[Any]]:
        """Parse and return the rows as a list of lists."""
        return json.loads(self.rows)

    def set_rows(self, rows: List[List[Any]]) -> None:
        """Set the rows from a list of lists."""
        self.rows = json.dumps(rows, ensure_ascii=False)

    def is_truncated(self) -> bool:
        """Check if results were truncated."""
        return self.truncated.lower() == "true"

    def set_truncated(self, truncated: bool) -> None:
        """Set the truncated flag."""
        self.truncated = "true" if truncated else "false"

    def __repr__(self) -> str:
        return f"<QueryResult(id='{self.id}', query_id='{self.query_id}', truncated={self.is_truncated()})>"
