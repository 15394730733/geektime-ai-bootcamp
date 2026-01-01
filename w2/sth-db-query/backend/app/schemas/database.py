"""
Database-related Pydantic schemas.
"""

import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DatabaseBase(BaseModel):
    """Base database schema."""
    name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    url: str
    description: Optional[str] = Field(None, max_length=200)

    @field_validator('url')
    @classmethod
    def validate_postgresql_url(cls, v: str) -> str:
        """Validate PostgreSQL connection URL format."""
        # Basic PostgreSQL URL pattern validation
        if not v.startswith(('postgresql://', 'postgres://')):
            raise ValueError('URL must be a valid PostgreSQL connection string starting with postgresql:// or postgres://')

        # Extract and validate basic components
        url_pattern = r'^(postgresql|postgres)://([^:/@]+)(?::([^@]*))?@([^:/]+)(?::(\d+))?/([^?]+)$'
        match = re.match(url_pattern, v)

        if not match:
            raise ValueError('Invalid PostgreSQL URL format. Expected: postgresql://user:pass@host:port/database')

        return v

    @field_validator('name')
    @classmethod
    def validate_name_uniqueness(cls, v: str) -> str:
        """Validate database name format and uniqueness requirement."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Name must contain only alphanumeric characters, hyphens, and underscores')
        return v


class DatabaseCreate(DatabaseBase):
    """Schema for creating a database connection."""
    pass


class Database(DatabaseBase):
    """Database connection schema."""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class ColumnMetadata(BaseModel):
    """Column metadata schema."""
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False
    default_value: Optional[str] = None


class TableMetadata(BaseModel):
    """Table metadata schema."""
    name: str
    db_schema: str = Field(default="public", alias="schema")
    columns: List[ColumnMetadata]


class ViewMetadata(BaseModel):
    """View metadata schema."""
    name: str
    db_schema: str = Field(default="public", alias="schema")
    columns: List[ColumnMetadata]


class DatabaseMetadata(BaseModel):
    """Database metadata schema."""
    database: str
    tables: List[TableMetadata]
    views: List[ViewMetadata]
