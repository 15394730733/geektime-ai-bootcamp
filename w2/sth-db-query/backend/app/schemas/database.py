"""
Database-related Pydantic schemas.
"""

import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


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
        url_pattern = r'^(postgresql|postgres)://([^:/@]+)(?::([^@]*))?@([^:/]+)(?::(\d+))?/([^?]+)(?:\?.*)?$'
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


class DatabaseUpdate(BaseModel):
    """Schema for updating a database connection."""
    url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=200)

    @field_validator('url')
    @classmethod
    def validate_postgresql_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate PostgreSQL connection URL format."""
        if v is None:
            return v
            
        # Basic PostgreSQL URL pattern validation
        if not v.startswith(('postgresql://', 'postgres://')):
            raise ValueError('URL must be a valid PostgreSQL connection string starting with postgresql:// or postgres://')

        # Extract and validate basic components
        url_pattern = r'^(postgresql|postgres)://([^:/@]+)(?::([^@]*))?@([^:/]+)(?::(\d+))?/([^?]+)(?:\?.*)?$'
        match = re.match(url_pattern, v)

        if not match:
            raise ValueError('Invalid PostgreSQL URL format. Expected: postgresql://user:pass@host:port/database')

        return v


class Database(DatabaseBase):
    """Database connection schema."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    is_active: bool = Field(default=True, alias="isActive")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )


class ColumnMetadata(BaseModel):
    """Column metadata schema."""
    name: str
    data_type: str = Field(alias="dataType")
    is_nullable: bool = Field(alias="isNullable")
    is_primary_key: bool = Field(default=False, alias="isPrimaryKey")
    default_value: Optional[str] = Field(None, alias="defaultValue")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )


class TableMetadata(BaseModel):
    """Table metadata schema."""
    name: str
    db_schema: str = Field(default="public", alias="schema")
    columns: List[ColumnMetadata]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )


class ViewMetadata(BaseModel):
    """View metadata schema."""
    name: str
    db_schema: str = Field(default="public", alias="schema")
    columns: List[ColumnMetadata]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )


class DatabaseMetadata(BaseModel):
    """Database metadata schema."""
    database: str
    tables: List[TableMetadata]
    views: List[ViewMetadata]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(field_name.split('_'))
        )
    )