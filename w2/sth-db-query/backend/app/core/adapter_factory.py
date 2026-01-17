"""
Database adapter factory.

This module provides a factory for creating database adapters based on
database type detection from connection URLs.
"""

from typing import Optional
import logging

from app.core.db_adapter import DatabaseAdapter
from app.core.db_type_detector import DatabaseType, DatabaseTypeDetector
from app.adapters.postgres_adapter import PostgreSQLAdapter
from app.adapters.mysql_adapter import MySQLAdapter

logger = logging.getLogger(__name__)


class AdapterFactory:
    """
    Factory for creating database adapters.

    This factory automatically detects the database type from the connection URL
    and returns the appropriate adapter instance.
    """

    _adapters = {
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
        DatabaseType.MYSQL: MySQLAdapter,
    }

    @classmethod
    def create_adapter(cls, database_url: str) -> DatabaseAdapter:
        """
        Create a database adapter based on the connection URL.

        Args:
            database_url: Database connection URL

        Returns:
            DatabaseAdapter instance

        Raises:
            ValueError: If database type is not supported

        Examples:
            >>> adapter = AdapterFactory.create_adapter("postgresql://user:pass@host/db")
            >>> isinstance(adapter, PostgreSQLAdapter)
            True
            >>> adapter = AdapterFactory.create_adapter("mysql://user:pass@host/db")
            >>> isinstance(adapter, MySQLAdapter)
            True
        """
        db_type = DatabaseTypeDetector.detect(database_url)

        if db_type == DatabaseType.UNKNOWN:
            raise ValueError(
                f"Unsupported database type for URL: {database_url}. "
                f"Supported types: PostgreSQL, MySQL"
            )

        adapter_class = cls._adapters.get(db_type)

        if adapter_class is None:
            raise ValueError(
                f"No adapter registered for database type: {db_type.value}. "
                f"Supported types: {list(cls._adapters.keys())}"
            )

        adapter = adapter_class()
        logger.info(f"Created {adapter.name} adapter for {db_type.value} database")

        return adapter

    @classmethod
    def get_adapter(cls, db_type: DatabaseType) -> DatabaseAdapter:
        """
        Get an adapter for a specific database type.

        Args:
            db_type: DatabaseType enum value

        Returns:
            DatabaseAdapter instance

        Raises:
            ValueError: If database type is not supported
        """
        adapter_class = cls._adapters.get(db_type)

        if adapter_class is None:
            raise ValueError(
                f"No adapter registered for database type: {db_type.value}. "
                f"Supported types: {list(cls._adapters.keys())}"
            )

        return adapter_class()

    @classmethod
    def register_adapter(cls, db_type: DatabaseType, adapter_class: type) -> None:
        """
        Register a new adapter for a database type.

        This allows extending the factory with custom adapters.

        Args:
            db_type: DatabaseType enum value
            adapter_class: Adapter class (must inherit from DatabaseAdapter)
        """
        if not issubclass(adapter_class, DatabaseAdapter):
            raise ValueError(
                f"Adapter class must inherit from DatabaseAdapter: {adapter_class}"
            )

        cls._adapters[db_type] = adapter_class
        logger.info(f"Registered {adapter_class.__name__} for {db_type.value}")

    @classmethod
    def is_supported(cls, database_url: str) -> bool:
        """
        Check if a database URL is supported.

        Args:
            database_url: Database connection URL

        Returns:
            True if supported, False otherwise
        """
        return DatabaseTypeDetector.is_supported(database_url)


# Convenience functions for backward compatibility
def create_adapter(database_url: str) -> DatabaseAdapter:
    """Create a database adapter from URL."""
    return AdapterFactory.create_adapter(database_url)


def get_adapter(db_type: DatabaseType) -> DatabaseAdapter:
    """Get an adapter for a specific database type."""
    return AdapterFactory.get_adapter(db_type)
