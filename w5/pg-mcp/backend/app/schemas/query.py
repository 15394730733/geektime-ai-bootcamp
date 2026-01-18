"""
Query-related Pydantic schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class QueryRequest(BaseModel):
    """SQL query request schema."""
    sql: str


class QueryResult(BaseModel):
    """SQL query result schema."""
    columns: List[str]
    rows: List[List]
    row_count: int = Field(alias="rowCount")
    execution_time_ms: int = Field(alias="executionTimeMs")
    truncated: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )


class NaturalLanguageQueryRequest(BaseModel):
    """Natural language query request schema."""
    prompt: str


class NaturalLanguageQueryResult(BaseModel):
    """Natural language query result schema."""
    generated_sql: str = Field(alias="generatedSql")
    columns: List[str]
    rows: List[List]
    row_count: int = Field(alias="rowCount")
    execution_time_ms: int = Field(alias="executionTimeMs")
    truncated: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )
