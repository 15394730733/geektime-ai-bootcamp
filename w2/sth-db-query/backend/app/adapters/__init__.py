"""
Database adapters for different database types.

This package contains adapter implementations for various database types,
providing a unified interface for metadata extraction and query execution.
"""

from app.adapters.postgres_adapter import PostgreSQLAdapter
from app.adapters.mysql_adapter import MySQLAdapter

__all__ = [
    'PostgreSQLAdapter',
    'MySQLAdapter',
]
