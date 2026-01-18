"""
Database models package.

This module contains all SQLAlchemy models for the database query tool.
Models are imported here for easy access throughout the application.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the base class for all models
Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
from .query import QueryExecution, QueryResult  # noqa: E402,F401
from .metadata import DatabaseMetadata  # noqa: E402,F401
from .database import DatabaseConnection  # noqa: E402,F401

__all__ = [
    "Base",
    "DatabaseConnection",
    "DatabaseMetadata",
    "QueryExecution",
    "QueryResult",
]
