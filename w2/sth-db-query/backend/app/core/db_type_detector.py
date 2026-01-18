"""
Database type detection module.

This module provides utilities to detect the type of database from a connection URL.
Supports PostgreSQL and MySQL databases.
"""

from enum import Enum
from urllib.parse import urlparse
from typing import Optional
import re


class DatabaseType(Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    UNKNOWN = "unknown"


class DatabaseTypeDetector:
    """Detects database type from connection URL."""

    # Database scheme patterns
    SCHEME_PATTERNS = {
        DatabaseType.POSTGRESQL: [
            'postgresql',
            'postgres',
            'postgresql+asyncpg',
            'postgres+asyncpg',
        ],
        DatabaseType.MYSQL: [
            'mysql',
            'mysql+aiomysql',
            'mysql+pymysql',
        ],
    }

    @classmethod
    def detect(cls, database_url: str) -> DatabaseType:
        """
        Detect database type from connection URL.

        Args:
            database_url: Database connection URL

        Returns:
            DatabaseType enum value

        Examples:
            >>> DatabaseTypeDetector.detect("postgresql://user:pass@host/db")
            <DatabaseType.POSTGRESQL: 'postgresql'>
            >>> DatabaseTypeDetector.detect("mysql://user:pass@host/db")
            <DatabaseType.MYSQL: 'mysql'>
        """
        if not database_url or not isinstance(database_url, str):
            return DatabaseType.UNKNOWN

        try:
            parsed = urlparse(database_url)
            scheme = parsed.scheme.lower()

            # Check for PostgreSQL
            if any(scheme.startswith(pg_scheme) for pg_scheme in cls.SCHEME_PATTERNS[DatabaseType.POSTGRESQL]):
                return DatabaseType.POSTGRESQL

            # Check for MySQL
            if any(scheme.startswith(mysql_scheme) for mysql_scheme in cls.SCHEME_PATTERNS[DatabaseType.MYSQL]):
                return DatabaseType.MYSQL

            return DatabaseType.UNKNOWN

        except Exception:
            return DatabaseType.UNKNOWN

    @classmethod
    def is_supported(cls, database_url: str) -> bool:
        """
        Check if database type is supported.

        Args:
            database_url: Database connection URL

        Returns:
            True if database type is supported, False otherwise
        """
        db_type = cls.detect(database_url)
        return db_type != DatabaseType.UNKNOWN

    @classmethod
    def is_postgresql(cls, database_url: str) -> bool:
        """
        Check if database URL is PostgreSQL.

        Args:
            database_url: Database connection URL

        Returns:
            True if PostgreSQL, False otherwise
        """
        return cls.detect(database_url) == DatabaseType.POSTGRESQL

    @classmethod
    def is_mysql(cls, database_url: str) -> bool:
        """
        Check if database URL is MySQL.

        Args:
            database_url: Database connection URL

        Returns:
            True if MySQL, False otherwise
        """
        return cls.detect(database_url) == DatabaseType.MYSQL

    @classmethod
    def get_default_port(cls, database_type: DatabaseType) -> int:
        """
        Get default port for database type.

        Args:
            database_type: Database type enum

        Returns:
            Default port number

        Raises:
            ValueError: If database type is unknown
        """
        default_ports = {
            DatabaseType.POSTGRESQL: 5432,
            DatabaseType.MYSQL: 3306,
        }

        if database_type not in default_ports:
            raise ValueError(f"Unknown database type: {database_type}")

        return default_ports[database_type]

    @classmethod
    def normalize_url(cls, database_url: str) -> str:
        """
        Normalize database URL by ensuring scheme consistency.

        Args:
            database_url: Database connection URL

        Returns:
            Normalized database URL

        Examples:
            >>> DatabaseTypeDetector.normalize_url("postgres://user:pass@host/db")
            'postgresql://user:pass@host/db'
        """
        db_type = cls.detect(database_url)

        if db_type == DatabaseType.POSTGRESQL:
            # Normalize to postgresql://
            pattern = r'^(postgres(?:\+[^:]+)?):'
            replacement = r'postgresql:'
            if '+asyncpg' not in database_url:
                normalized = re.sub(pattern, replacement, database_url, flags=re.IGNORECASE)
                # Add asyncpg if not present
                if 'postgresql+' not in normalized:
                    normalized = normalized.replace('postgresql:', 'postgresql+asyncpg:', 1)
                return normalized
            return database_url

        elif db_type == DatabaseType.MYSQL:
            # Normalize to mysql+aiomysql://
            if not database_url.startswith('mysql+aiomysql'):
                pattern = r'^(mysql(?:\+[^:]+)?):'
                replacement = r'mysql+aiomysql:'
                return re.sub(pattern, replacement, database_url, flags=re.IGNORECASE)
            return database_url

        return database_url


# Convenience functions for backward compatibility
def detect_database_type(database_url: str) -> DatabaseType:
    """Detect database type from URL."""
    return DatabaseTypeDetector.detect(database_url)


def is_postgresql(database_url: str) -> bool:
    """Check if URL is PostgreSQL."""
    return DatabaseTypeDetector.is_postgresql(database_url)


def is_mysql(database_url: str) -> bool:
    """Check if URL is MySQL."""
    return DatabaseTypeDetector.is_mysql(database_url)


def normalize_database_url(database_url: str) -> str:
    """Normalize database URL."""
    return DatabaseTypeDetector.normalize_url(database_url)
