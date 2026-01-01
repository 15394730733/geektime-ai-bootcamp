"""
Query-related Pydantic schemas.
"""

from typing import List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """SQL query request schema."""
    sql: str


class QueryResult(BaseModel):
    """SQL query result schema."""
    columns: List[str]
    rows: List[List]
    row_count: int
    execution_time_ms: int
    truncated: bool = False


class NaturalLanguageQueryRequest(BaseModel):
    """Natural language query request schema."""
    prompt: str


class NaturalLanguageQueryResult(BaseModel):
    """Natural language query result schema."""
    generated_sql: str
    columns: List[str]
    rows: List[List]
    row_count: int
    execution_time_ms: int
    truncated: bool = False
