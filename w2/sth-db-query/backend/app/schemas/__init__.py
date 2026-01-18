"""
Pydantic schemas package.

This module contains all Pydantic models used for API request/response validation.
"""

from .database import (
    Database,
    DatabaseBase,
    DatabaseCreate,
    DatabaseMetadata,
    TableMetadata,
    ViewMetadata,
    ColumnMetadata,
)
from .query import (
    QueryRequest,
    QueryResult,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResult,
)

__all__ = [
    "Database",
    "DatabaseBase",
    "DatabaseCreate",
    "DatabaseMetadata",
    "TableMetadata",
    "ViewMetadata",
    "ColumnMetadata",
    "QueryRequest",
    "QueryResult",
    "NaturalLanguageQueryRequest",
    "NaturalLanguageQueryResult",
]
