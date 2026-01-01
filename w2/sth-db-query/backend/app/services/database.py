"""
Database connection service layer with validation.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.database import get_databases, get_database, create_database, update_database, delete_database
from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate, Database
from app.core.security import validate_and_sanitize_sql


class DatabaseServiceError(Exception):
    """Exception raised when database service operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DatabaseService:
    """Service layer for database connection management."""

    def __init__(self):
        pass

    async def list_databases(self, db: AsyncSession) -> List[Database]:
        """List all database connections."""
        connections = await get_databases(db)
        return [Database.model_validate(conn) for conn in connections]

    async def get_database(self, db: AsyncSession, name: str) -> Optional[Database]:
        """Get a specific database connection by name."""
        connection = await get_database(db, name)
        return Database.model_validate(connection) if connection else None

    async def create_database(self, db: AsyncSession, database_data: DatabaseCreate) -> Database:
        """Create a new database connection with validation."""
        # Validate the database data
        await self._validate_database_data(db, database_data)

        # Test the connection
        await self._test_connection(database_data.url)

        # Create the database connection
        connection = await create_database(db, database_data)
        return Database.model_validate(connection)

    async def update_database(self, db: AsyncSession, name: str, database_data: DatabaseCreate) -> Optional[Database]:
        """Update an existing database connection."""
        # Validate the database data
        await self._validate_database_data(db, database_data, exclude_name=name)

        # Test the connection if URL changed
        existing = await get_database(db, name)
        if existing and existing.url != database_data.url:
            await self._test_connection(database_data.url)

        # Update the database connection
        connection = await update_database(db, name, database_data)
        return Database.model_validate(connection) if connection else None

    async def delete_database(self, db: AsyncSession, name: str) -> bool:
        """Delete a database connection."""
        return await delete_database(db, name)

    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Test database connection and return status."""
        return await self._test_connection(url)

    async def _validate_database_data(self, db: AsyncSession, data: DatabaseCreate, exclude_name: Optional[str] = None):
        """Validate database connection data."""
        # Validate URL format
        self._validate_url_format(data.url)

        # Check name uniqueness
        await self._validate_name_uniqueness(db, data.name, exclude_name)

        # Validate name format
        self._validate_name_format(data.name)

    def _validate_url_format(self, url: str):
        """Validate database URL format."""
        if not url or not isinstance(url, str):
            raise DatabaseServiceError("Database URL is required")

        try:
            parsed = urlparse(url)

            # Must be postgresql scheme
            if parsed.scheme not in ["postgresql", "postgres"]:
                raise DatabaseServiceError("Only PostgreSQL databases are supported")

            # Must have hostname
            if not parsed.hostname:
                raise DatabaseServiceError("Database URL must include a valid hostname")

            # Must have database name
            if not parsed.path or parsed.path == '/':
                raise DatabaseServiceError("Database URL must include a database name")

            # Validate port if specified
            if parsed.port is not None and (parsed.port < 1 or parsed.port > 65535):
                raise DatabaseServiceError("Database port must be between 1 and 65535")

        except Exception as e:
            raise DatabaseServiceError(f"Invalid database URL format: {str(e)}")

    async def _validate_name_uniqueness(self, db: AsyncSession, name: str, exclude_name: Optional[str] = None):
        """Validate that database name is unique."""
        query = select(DatabaseConnection).where(DatabaseConnection.name == name)

        if exclude_name:
            query = query.where(DatabaseConnection.name != exclude_name)

        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            raise DatabaseServiceError(f"Database connection with name '{name}' already exists")

    def _validate_name_format(self, name: str):
        """Validate database connection name format."""
        if not name or not isinstance(name, str):
            raise DatabaseServiceError("Database name is required")

        name = name.strip()
        if not name:
            raise DatabaseServiceError("Database name cannot be empty")

        # Name should only contain alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise DatabaseServiceError(
                "Database name must contain only alphanumeric characters, hyphens, and underscores"
            )

        if len(name) > 50:
            raise DatabaseServiceError("Database name cannot exceed 50 characters")

    async def _test_connection(self, url: str) -> Dict[str, Any]:
        """Test database connection."""
        # This is a placeholder - actual implementation would test the connection
        # For now, we'll do basic URL validation
        try:
            self._validate_url_format(url)
            return {
                "success": True,
                "message": "Connection URL format is valid",
                "latency_ms": 0
            }
        except DatabaseServiceError as e:
            return {
                "success": False,
                "message": str(e),
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Connection test failed",
                "error": str(e)
            }
