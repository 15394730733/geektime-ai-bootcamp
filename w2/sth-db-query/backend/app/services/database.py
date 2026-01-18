"""
Database connection service layer with multi-database support.

Supports PostgreSQL and MySQL databases using adapter pattern.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time

logger = logging.getLogger(__name__)

from app.crud.database import (
    get_databases, get_database, get_database_by_name, create_database, update_database, delete_database,
    get_database_metadata, create_database_metadata, delete_database_metadata
)
from app.models.database import DatabaseConnection
from app.models.metadata import DatabaseMetadata
from app.schemas.database import DatabaseCreate, DatabaseUpdate, Database
from app.core.security import validate_and_sanitize_sql
from app.core.errors import (
    DatabaseQueryError, NetworkError, AuthenticationError, ConfigurationError,
    ValidationError, TimeoutError, categorize_asyncpg_error, categorize_timeout_error
)
from app.core.connection_pool import connection_pool_manager
from app.core.adapter_factory import AdapterFactory
from app.core.db_type_detector import DatabaseType, DatabaseTypeDetector

# Alias for backward compatibility
DatabaseServiceError = DatabaseQueryError


class DatabaseService:
    """Service layer for database connection management."""

    def __init__(self):
        pass

    async def list_databases(self, db: AsyncSession) -> List[Database]:
        """List all database connections."""
        connections = await get_databases(db)
        return [Database.model_validate(conn) for conn in connections]

    async def get_database(self, db: AsyncSession, id: str) -> Optional[Database]:
        """Get a specific database connection by id."""
        connection = await get_database(db, id)
        return Database.model_validate(connection) if connection else None

    async def get_database_by_name(self, db: AsyncSession, name: str) -> Optional[Database]:
        """Get a specific database connection by name."""
        connection = await get_database_by_name(db, name)
        return Database.model_validate(connection) if connection else None

    async def create_database(self, db: AsyncSession, database_data: DatabaseCreate) -> Database:
        """Create a new database connection with validation."""
        try:
            # Validate the database data
            await self._validate_database_data(db, database_data)

            # Test the connection
            connection_test = await self._test_connection(database_data.url)
            if not connection_test["success"]:
                # The _test_connection method now returns categorized errors
                error_info = connection_test.get("error_info")
                if error_info and isinstance(error_info, DatabaseQueryError):
                    raise error_info
                else:
                    raise NetworkError(
                        message=f"Database connection test failed: {connection_test['message']}",
                        technical_details=connection_test.get('error', '')
                    )

            # Create the database connection
            connection = await create_database(db, database_data)
            return Database.model_validate(connection)
        except DatabaseQueryError:
            raise
        except Exception as e:
            raise DatabaseQueryError(
                message=f"Failed to create database connection: {str(e)}",
                technical_details=str(e)
            )

    async def update_database(self, db: AsyncSession, id: str, database_data: DatabaseCreate) -> Optional[Database]:
        """Update an existing database connection."""
        # Validate the database data
        await self._validate_database_data(db, database_data, exclude_id=id)

        # Get existing connection
        existing = await get_database(db, id)
        if not existing:
            return None

        # Check if URL changed and test connection if needed
        url_changed = existing.url != database_data.url
        await self._validate_connection_if_changed(database_data.url, url_changed, existing.url)

        # Update the database connection
        connection = await update_database(db, id, database_data)
        if not connection:
            return None

        # Refresh metadata if URL changed to ensure metadata persistence
        await self._refresh_metadata_if_url_changed(db, connection, url_changed, existing.name)

        return Database.model_validate(connection)

    async def update_database_partial(self, db: AsyncSession, id: str, update_data: DatabaseUpdate) -> Optional[Database]:
        """Update an existing database connection with partial data."""
        # Get existing connection
        existing = await get_database(db, id)
        if not existing:
            return None

        # Determine if URL is changing
        url_changed = update_data.url is not None and existing.url != update_data.url

        # Validate URL if it's changing
        if url_changed:
            self._validate_url_format(update_data.url)
            await self._validate_connection_if_changed(update_data.url, url_changed, existing.url)

        # Create a full DatabaseCreate object for the update
        full_update_data = DatabaseCreate(
            name=update_data.name if update_data.name is not None else existing.name,
            url=update_data.url if update_data.url is not None else existing.url,
            description=update_data.description if update_data.description is not None else existing.description
        )

        # Use the main update method
        return await self.update_database(db, id, full_update_data)

    async def _validate_connection_if_changed(self, new_url: str, url_changed: bool, old_url: str):
        """
        Validate and test connection if URL has changed.

        Args:
            new_url: New database URL
            url_changed: Whether the URL has changed
            old_url: Old database URL for logging

        Raises:
            NetworkError: If connection test fails
        """
        if url_changed:
            connection_test = await self._test_connection(new_url)
            if not connection_test["success"]:
                error_info = connection_test.get("error_info")
                if error_info and isinstance(error_info, DatabaseQueryError):
                    raise error_info
                else:
                    raise NetworkError(
                        message=f"Database connection test failed: {connection_test['message']}",
                        technical_details=connection_test.get('error', '')
                    )

    async def _refresh_metadata_if_url_changed(self, db: AsyncSession, connection, url_changed: bool, name: str):
        """
        Refresh metadata if URL changed to ensure metadata persistence.

        Args:
            db: Database session
            connection: Database connection object
            url_changed: Whether the URL has changed
            name: Database name for logging
        """
        if url_changed:
            try:
                await self.refresh_database_metadata(db, connection.url, connection.id)
            except Exception as e:
                # Log warning but don't fail the update
                logger.warning(f"Failed to refresh metadata after database update for '{name}': {str(e)}")

    async def delete_database(self, db: AsyncSession, id: str) -> bool:
        """Delete a database connection."""
        return await delete_database(db, id)

    async def test_connection(self, url: str) -> Dict[str, Any]:
        """Test database connection and return status."""
        return await self._test_connection(url)

    async def get_connection_status(self, db: AsyncSession, name: str) -> bool:
        """Get the connection status of a database."""
        try:
            connection = await get_database(db, name)
            if not connection:
                raise DatabaseServiceError(f"Database '{name}' not found")
            return connection.is_active
        except Exception as e:
            raise DatabaseServiceError(f"Failed to get connection status: {str(e)}")

    async def update_connection_status(self, db: AsyncSession, name: str, is_active: bool) -> Optional[Database]:
        """Update the connection status of a database."""
        try:
            connection = await get_database(db, name)
            if not connection:
                raise DatabaseServiceError(f"Database '{name}' not found")
            
            connection.is_active = is_active
            await db.commit()
            await db.refresh(connection)
            return Database.model_validate(connection)
        except Exception as e:
            raise DatabaseServiceError(f"Failed to update connection status: {str(e)}")

    async def ensure_metadata_persistence(self, db: AsyncSession, name: str) -> Dict[str, Any]:
        """
        Ensure metadata is persisted for a database connection.
        
        This method checks if metadata exists for the database and refreshes it if needed.
        Validates requirement 8.3: metadata updates are saved to SQLite database.
        """
        try:
            # Get the database connection
            database_conn = await self.get_database(db, name)
            if not database_conn:
                raise DatabaseServiceError(f"Database '{name}' not found")
            
            # Check if metadata exists
            existing_metadata = await self.get_database_metadata(db, name)
            
            # If no metadata exists, extract and store it
            if not existing_metadata or not existing_metadata.get("tables"):
                await self.refresh_database_metadata(db, database_conn.url, database_conn.id)
                refreshed_metadata = await self.get_database_metadata(db, name)
                
                return {
                    "database": name,
                    "metadata_refreshed": True,
                    "tables_count": len(refreshed_metadata.get("tables", [])),
                    "views_count": len(refreshed_metadata.get("views", [])),
                    "message": "Metadata was missing and has been refreshed"
                }
            else:
                return {
                    "database": name,
                    "metadata_refreshed": False,
                    "tables_count": len(existing_metadata.get("tables", [])),
                    "views_count": len(existing_metadata.get("views", [])),
                    "message": "Metadata already exists and is persisted"
                }
                
        except Exception as e:
            raise DatabaseServiceError(f"Failed to ensure metadata persistence for '{name}': {str(e)}")

    async def force_metadata_refresh(self, db: AsyncSession, name: str) -> Dict[str, Any]:
        """
        Force a metadata refresh for a database connection.
        
        This ensures that any changes to the database schema are captured
        and persisted in the metadata store.
        """
        try:
            # Get the database connection
            database_conn = await self.get_database(db, name)
            if not database_conn:
                raise DatabaseServiceError(f"Database '{name}' not found")
            
            # Force refresh metadata
            await self.refresh_database_metadata(db, database_conn.url, database_conn.id)
            refreshed_metadata = await self.get_database_metadata(db, name)
            
            return {
                "database": name,
                "metadata_refreshed": True,
                "tables_count": len(refreshed_metadata.get("tables", [])),
                "views_count": len(refreshed_metadata.get("views", [])),
                "message": "Metadata has been forcefully refreshed and persisted"
            }
            
        except Exception as e:
            raise DatabaseServiceError(f"Failed to force metadata refresh for '{name}': {str(e)}")

    async def _validate_database_data(self, db: AsyncSession, data: DatabaseCreate, exclude_id: Optional[str] = None):
        """Validate database connection data."""
        # Validate URL format
        self._validate_url_format(data.url)

        # Check name uniqueness
        await self._validate_name_uniqueness(db, data.name, exclude_id)

        # Validate name format
        self._validate_name_format(data.name)

    def _validate_url_format(self, url: str):
        """Validate database URL format (supports PostgreSQL and MySQL)."""
        if not url or not isinstance(url, str):
            raise ValidationError(
                message="Database URL is required",
                user_message="Please provide a valid database connection URL.",
                suggestions=[
                    "Enter a PostgreSQL connection URL: postgresql://user:password@host:port/database",
                    "Enter a MySQL connection URL: mysql://user:password@host:port/database"
                ]
            )

        try:
            parsed = urlparse(url)

            # Detect database type
            db_type = DatabaseTypeDetector.detect(url)

            if db_type == DatabaseType.UNKNOWN:
                raise ConfigurationError(
                    message="Unsupported database type",
                    user_message="This tool supports PostgreSQL and MySQL databases only.",
                    suggestions=[
                        "Use a PostgreSQL database URL (postgresql://user:password@host:port/database)",
                        "Use a MySQL database URL (mysql://user:password@host:port/database)",
                        "Ensure the URL scheme is either 'postgresql', 'postgres', or 'mysql'"
                    ]
                )

            # Must have hostname
            if not parsed.hostname:
                raise ConfigurationError(
                    message="Database URL must include a valid hostname",
                    user_message="The database URL is missing a hostname.",
                    suggestions=[
                        "Include the database server hostname or IP address",
                        "Example (PostgreSQL): postgresql://user:password@localhost:5432/database",
                        "Example (MySQL): mysql://user:password@localhost:3306/database"
                    ]
                )

            # Must have database name
            if not parsed.path or parsed.path == '/':
                raise ConfigurationError(
                    message="Database URL must include a database name",
                    user_message="The database URL is missing a database name.",
                    suggestions=[
                        "Include the database name in the URL path",
                        "Example: postgresql://user:password@host:5432/mydatabase",
                        "Example: mysql://user:password@host:3306/mydatabase"
                    ]
                )

            # Validate port if specified
            if parsed.port is not None and (parsed.port < 1 or parsed.port > 65535):
                raise ConfigurationError(
                    message="Database port must be between 1 and 65535",
                    user_message="The database port number is invalid.",
                    suggestions=[
                        "Use a valid port number (5432 for PostgreSQL, 3306 for MySQL)",
                        "Remove the port to use the default"
                    ]
                )

        except DatabaseQueryError:
            raise
        except Exception as e:
            raise ConfigurationError(
                message=f"Invalid database URL format: {str(e)}",
                user_message="The database URL format is invalid.",
                suggestions=[
                    "PostgreSQL format: postgresql://user:password@host:port/database",
                    "MySQL format: mysql://user:password@host:port/database",
                    "Check for typos in the URL",
                    "Ensure special characters are properly encoded"
                ],
                technical_details=str(e)
            )

    async def _validate_name_uniqueness(self, db: AsyncSession, name: str, exclude_id: Optional[str] = None):
        """Validate that database name is unique."""
        query = select(DatabaseConnection).where(DatabaseConnection.name == name)

        if exclude_id:
            query = query.where(DatabaseConnection.id != exclude_id)

        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            raise ValidationError(
                message=f"Database connection with name '{name}' already exists",
                user_message=f"A database connection named '{name}' already exists.",
                suggestions=[
                    "Choose a different name for your database connection",
                    "Update the existing connection instead of creating a new one"
                ]
            )

    def _validate_name_format(self, name: str):
        """Validate database connection name format."""
        if not name or not isinstance(name, str):
            raise ValidationError(
                message="Database name is required",
                user_message="Please provide a name for the database connection.",
                suggestions=["Enter a descriptive name for your database connection"]
            )

        name = name.strip()
        if not name:
            raise ValidationError(
                message="Database name cannot be empty",
                user_message="The database name cannot be empty.",
                suggestions=["Enter a non-empty name for your database connection"]
            )

        # Name should only contain alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValidationError(
                message="Database name must contain only alphanumeric characters, hyphens, and underscores",
                user_message="The database name contains invalid characters.",
                suggestions=[
                    "Use only letters, numbers, hyphens (-), and underscores (_)",
                    "Remove spaces and special characters from the name"
                ]
            )

        if len(name) > 50:
            raise ValidationError(
                message="Database name cannot exceed 50 characters",
                user_message="The database name is too long.",
                suggestions=["Use a shorter name (maximum 50 characters)"]
            )

    async def _test_connection(self, url: str) -> Dict[str, Any]:
        """Test database connection using adapter and connection pool."""
        try:
            self._validate_url_format(url)

            start_time = time.time()

            # Create adapter for the database type
            adapter = AdapterFactory.create_adapter(url)

            # Use async connection pool to test connection
            try:
                conn = await connection_pool_manager.get_connection(url)
                # Test the connection with adapter
                is_alive = await adapter.test_connection(conn)

                # Return connection to pool
                await connection_pool_manager.return_connection(url, conn)

                latency_ms = int((time.time() - start_time) * 1000)

                if is_alive:
                    return {
                        "success": True,
                        "message": "Database connection successful",
                        "latency_ms": latency_ms
                    }
                else:
                    return {
                        "success": False,
                        "message": "Database connection test failed",
                        "error": "Connection test returned False",
                        "latency_ms": latency_ms
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Connection failed: {str(e)}",
                    "error": str(e),
                    "latency_ms": int((time.time() - start_time) * 1000)
                }

        except DatabaseQueryError as e:
            return {
                "success": False,
                "message": e.user_message,
                "error": str(e),
                "error_info": e
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error during connection test: {str(e)}",
                "error": str(e)
            }

    async def get_database_metadata(self, db: AsyncSession, database_name: str) -> Dict[str, Any]:
        """Get cached metadata for a database connection."""
        try:
            # Get the database connection to ensure it exists and get the ID
            database_conn = await self.get_database_by_name(db, database_name)
            if not database_conn:
                raise DatabaseServiceError(f"Database '{database_name}' not found")

            metadata_records = await get_database_metadata(db, database_conn.id)

            tables = []
            views = []

            for record in metadata_records:
                columns = record.get_columns()
                metadata_item = {
                    "name": record.object_name,
                    "schema": record.schema_name,
                    "columns": columns
                }

                if record.object_type == "table":
                    tables.append(metadata_item)
                elif record.object_type == "view":
                    views.append(metadata_item)

            # Extract database name from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(database_conn.url)
            database_name = parsed_url.path.lstrip('/')

            return {
                "database": database_name,  # Return actual database name from URL
                "tables": tables,
                "views": views
            }
        except Exception as e:
            raise DatabaseServiceError(f"Failed to get database metadata: {str(e)}")

    async def refresh_database_metadata(self, db: AsyncSession, database_url: str, connection_id: str) -> Dict[str, Any]:
        """Refresh metadata by connecting to the actual database and extracting information."""
        try:
            # Delete existing metadata
            await delete_database_metadata(db, connection_id)

            # Extract metadata from the actual database (asynchronous operation)
            metadata_list = await self._extract_database_metadata(database_url, connection_id)

            # Save new metadata
            if metadata_list:
                await create_database_metadata(db, metadata_list)

            # Return the metadata - need to find database name by ID
            # Get database connection by ID to find the name
            query = select(DatabaseConnection).where(DatabaseConnection.id == connection_id)
            result = await db.execute(query)
            db_conn = result.scalar_one_or_none()
            if not db_conn:
                raise DatabaseServiceError(f"Database connection with ID '{connection_id}' not found")

            return await self.get_database_metadata(db, db_conn.name)

        except Exception as e:
            raise DatabaseServiceError(f"Failed to refresh database metadata: {str(e)}")

    async def _extract_database_metadata(self, database_url: str, connection_id: str) -> List[Dict[str, Any]]:
        """Extract metadata from database (PostgreSQL or MySQL) using adapter."""
        try:
            # Create adapter for the database type
            adapter = AdapterFactory.create_adapter(database_url)

            # Get connection from pool
            conn = await connection_pool_manager.get_connection(database_url)

            try:
                # Use adapter to get metadata
                metadata_list = await adapter.get_metadata(conn, connection_id)
                return metadata_list

            finally:
                # Return connection to pool
                await connection_pool_manager.return_connection(database_url, conn)

        except Exception as e:
            raise DatabaseServiceError(f"Failed to extract database metadata: {str(e)}")

    async def execute_query(self, db: AsyncSession, database_name: str, sql: str, max_rows: int = 1000, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Execute a SQL query against the specified database using adapter."""
        try:
            # Get the database connection
            database_conn = await self.get_database(db, database_name)
            if not database_conn:
                raise ConfigurationError(
                    message=f"Database '{database_name}' not found",
                    user_message=f"The database '{database_name}' was not found in your connections.",
                    suggestions=[
                        "Check that the database name is spelled correctly",
                        "Verify the database connection exists",
                        "Refresh the database list"
                    ]
                )

            # Create adapter for the database type
            adapter = AdapterFactory.create_adapter(database_conn.url)

            # Get connection from pool
            conn = await connection_pool_manager.get_connection(database_conn.url)

            try:
                # Execute query using adapter
                result = await adapter.execute_query(conn, sql, timeout_seconds)

                # Apply max_rows truncation if needed
                truncated = False
                if len(result['rows']) > max_rows:
                    result['rows'] = result['rows'][:max_rows]
                    result['row_count'] = max_rows
                    result['rowCount'] = max_rows  # Also update camelCase version
                    truncated = True

                result['truncated'] = truncated
                return result

            except Exception as e:
                # Re-raise database-specific errors
                raise

            finally:
                # Return connection to pool
                await connection_pool_manager.return_connection(database_conn.url, conn)

        except DatabaseQueryError:
            raise
        except Exception as e:
            raise DatabaseQueryError(
                message=f"Query execution failed: {str(e)}",
                user_message="An unexpected error occurred while executing your query.",
                suggestions=[
                    "Check your SQL syntax",
                    "Verify the database connection is still active",
                    "Try a simpler query to test the connection"
                ],
                technical_details=str(e)
            )

    async def execute_query_by_url(self, database_url: str, sql: str, max_rows: int = 1000, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Execute a SQL query against the specified database URL using adapter."""
        try:
            # Create adapter for the database type
            adapter = AdapterFactory.create_adapter(database_url)

            # Get connection from pool
            conn = await connection_pool_manager.get_connection(database_url)

            try:
                # Execute query using adapter
                result = await adapter.execute_query(conn, sql, timeout_seconds)

                # Apply max_rows truncation if needed
                truncated = False
                if len(result['rows']) > max_rows:
                    result['rows'] = result['rows'][:max_rows]
                    result['row_count'] = max_rows
                    result['rowCount'] = max_rows  # Also update camelCase version
                    truncated = True

                result['truncated'] = truncated
                return result

            except Exception as e:
                # Re-raise database-specific errors
                raise

            finally:
                # Return connection to pool
                await connection_pool_manager.return_connection(database_url, conn)

        except DatabaseQueryError:
            raise
        except Exception as e:
            raise DatabaseQueryError(
                message=f"Query execution failed: {str(e)}",
                user_message="An unexpected error occurred while executing your query.",
                suggestions=[
                    "Check your SQL syntax",
                    "Verify the database connection is still active",
                    "Try a simpler query to test the connection"
                ],
                technical_details=str(e)
            )
