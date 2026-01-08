"""
Database connection service layer with validation.
"""

import re
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time

from app.crud.database import (
    get_databases, get_database, create_database, update_database, delete_database,
    get_database_metadata, create_database_metadata, delete_database_metadata
)
from app.models.database import DatabaseConnection
from app.models.metadata import DatabaseMetadata
from app.schemas.database import DatabaseCreate, DatabaseUpdate, Database
from app.core.security import validate_and_sanitize_sql
from app.core.errors import (
    DatabaseQueryError, NetworkError, AuthenticationError, ConfigurationError,
    ValidationError, TimeoutError, categorize_psycopg2_error, categorize_timeout_error
)

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

    async def get_database(self, db: AsyncSession, name: str) -> Optional[Database]:
        """Get a specific database connection by name."""
        connection = await get_database(db, name)
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

    async def update_database(self, db: AsyncSession, name: str, database_data: DatabaseCreate) -> Optional[Database]:
        """Update an existing database connection."""
        # Validate the database data
        await self._validate_database_data(db, database_data, exclude_name=name)

        # Get existing connection to check if URL changed
        existing = await get_database(db, name)
        if not existing:
            return None
            
        url_changed = existing.url != database_data.url

        # Test the connection if URL changed
        if url_changed:
            connection_test = await self._test_connection(database_data.url)
            if not connection_test["success"]:
                error_info = connection_test.get("error_info")
                if error_info and isinstance(error_info, DatabaseQueryError):
                    raise error_info
                else:
                    raise NetworkError(
                        message=f"Database connection test failed: {connection_test['message']}",
                        technical_details=connection_test.get('error', '')
                    )

        # Update the database connection
        connection = await update_database(db, name, database_data)
        if not connection:
            return None
            
        # Refresh metadata if URL changed to ensure metadata persistence
        if url_changed:
            try:
                await self.refresh_database_metadata(db, connection.url, connection.id)
            except Exception as e:
                # Log warning but don't fail the update
                # In a production system, you'd use proper logging
                print(f"Warning: Failed to refresh metadata after database update for '{name}': {str(e)}")
        
        return Database.model_validate(connection)

    async def update_database_partial(self, db: AsyncSession, name: str, update_data: DatabaseUpdate) -> Optional[Database]:
        """Update an existing database connection with partial data."""
        # Get existing connection
        existing = await get_database(db, name)
        if not existing:
            return None

        # Only validate and test connection if URL is being changed
        url_changed = False
        if update_data.url is not None and existing.url != update_data.url:
            url_changed = True
            # Validate URL format
            self._validate_url_format(update_data.url)
            
            # Test the new connection
            connection_test = await self._test_connection(update_data.url)
            if not connection_test["success"]:
                error_info = connection_test.get("error_info")
                if error_info and isinstance(error_info, DatabaseQueryError):
                    raise error_info
                else:
                    raise NetworkError(
                        message=f"Database connection test failed: {connection_test['message']}",
                        technical_details=connection_test.get('error', '')
                    )

        # Create a full DatabaseCreate object for the existing update method
        full_update_data = DatabaseCreate(
            name=existing.name,  # Keep existing name
            url=update_data.url if update_data.url is not None else existing.url,
            description=update_data.description if update_data.description is not None else existing.description
        )

        # Use existing update method
        return await self.update_database(db, name, full_update_data)

    async def delete_database(self, db: AsyncSession, name: str) -> bool:
        """Delete a database connection."""
        return await delete_database(db, name)

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
        """Get the current connection status for a database."""
        try:
            database_conn = await self.get_database(db, name)
            if not database_conn:
                raise DatabaseServiceError(f"Database '{name}' not found")
            
            # Test the actual connection
            connection_test = await self._test_connection(database_conn.url)
            
            # Update the stored status based on the test result
            if connection_test["success"] != database_conn.is_active:
                await self.update_connection_status(db, name, connection_test["success"])
                database_conn.is_active = connection_test["success"]
            
            return {
                "name": database_conn.name,
                "is_active": database_conn.is_active,
                "last_tested": datetime.utcnow().isoformat(),
                "connection_test": connection_test
            }
        except Exception as e:
            raise DatabaseServiceError(f"Failed to get connection status: {str(e)}")

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
            raise ValidationError(
                message="Database URL is required",
                user_message="Please provide a valid database connection URL.",
                suggestions=["Enter a PostgreSQL connection URL in the format: postgresql://user:password@host:port/database"]
            )

        try:
            parsed = urlparse(url)

            # Must be postgresql scheme
            if parsed.scheme not in ["postgresql", "postgres"]:
                raise ConfigurationError(
                    message="Only PostgreSQL databases are supported",
                    user_message="This tool only supports PostgreSQL databases.",
                    suggestions=[
                        "Use a PostgreSQL database URL",
                        "Ensure the URL starts with 'postgresql://' or 'postgres://'",
                        "Contact support if you need to connect to other database types"
                    ]
                )

            # Must have hostname
            if not parsed.hostname:
                raise ConfigurationError(
                    message="Database URL must include a valid hostname",
                    user_message="The database URL is missing a hostname.",
                    suggestions=[
                        "Include the database server hostname or IP address",
                        "Example: postgresql://user:password@localhost:5432/database"
                    ]
                )

            # Must have database name
            if not parsed.path or parsed.path == '/':
                raise ConfigurationError(
                    message="Database URL must include a database name",
                    user_message="The database URL is missing a database name.",
                    suggestions=[
                        "Include the database name in the URL path",
                        "Example: postgresql://user:password@host:5432/mydatabase"
                    ]
                )

            # Validate port if specified
            if parsed.port is not None and (parsed.port < 1 or parsed.port > 65535):
                raise ConfigurationError(
                    message="Database port must be between 1 and 65535",
                    user_message="The database port number is invalid.",
                    suggestions=[
                        "Use a valid port number (typically 5432 for PostgreSQL)",
                        "Remove the port to use the default (5432)"
                    ]
                )

        except DatabaseQueryError:
            raise
        except Exception as e:
            raise ConfigurationError(
                message=f"Invalid database URL format: {str(e)}",
                user_message="The database URL format is invalid.",
                suggestions=[
                    "Use the format: postgresql://user:password@host:port/database",
                    "Check for typos in the URL",
                    "Ensure special characters are properly encoded"
                ],
                technical_details=str(e)
            )

    async def _validate_name_uniqueness(self, db: AsyncSession, name: str, exclude_name: Optional[str] = None):
        """Validate that database name is unique."""
        query = select(DatabaseConnection).where(DatabaseConnection.name == name)

        if exclude_name:
            query = query.where(DatabaseConnection.name != exclude_name)

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
        """Test database connection with optimized performance."""
        try:
            self._validate_url_format(url)

            # Actually test the database connection
            import time
            import asyncio
            start_time = time.time()

            # Parse URL and test connection
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password

            # Test connection with shorter timeout and run in thread pool to avoid blocking
            import psycopg2
            
            def sync_test_connection():
                """Synchronous connection test to run in thread pool."""
                try:
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password,
                        connect_timeout=3  # Reduced to 3 seconds for faster feedback
                    )
                    conn.close()
                    return True, None
                except Exception as e:
                    return False, e
            
            # Run the connection test in a thread pool to avoid blocking the event loop
            try:
                loop = asyncio.get_event_loop()
                success, error = await loop.run_in_executor(None, sync_test_connection)
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                if success:
                    return {
                        "success": True,
                        "message": "Database connection successful",
                        "latency_ms": latency_ms
                    }
                else:
                    # Handle the error
                    if isinstance(error, psycopg2.OperationalError):
                        categorized_error = categorize_psycopg2_error(error)
                        return {
                            "success": False,
                            "message": categorized_error.user_message,
                            "error": str(error),
                            "error_info": categorized_error,
                            "latency_ms": latency_ms
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Connection failed: {str(error)}",
                            "error": str(error),
                            "latency_ms": latency_ms
                        }
                        
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "message": "Connection test timed out",
                    "error": "Connection timeout after 3 seconds",
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
            database_conn = await self.get_database(db, database_name)
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

            # Extract metadata from the actual database (synchronous operation)
            metadata_list = self._extract_database_metadata(database_url, connection_id)

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

    def _extract_database_metadata(self, database_url: str, connection_id: str) -> List[Dict[str, Any]]:
        """Extract metadata from PostgreSQL database."""
        try:
            # Parse database URL to get connection parameters
            parsed = urlparse(database_url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password

            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )

            try:
                metadata_list = []

                # Get tables
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT
                            schemaname as schema_name,
                            tablename as table_name
                        FROM pg_tables
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, tablename
                    """)

                    tables = cursor.fetchall()

                    for table in tables:
                        schema_name = table['schema_name']
                        table_name = table['table_name']

                        # Get columns for this table
                        cursor.execute("""
                            SELECT
                                c.column_name,
                                c.data_type,
                                c.is_nullable = 'YES' as is_nullable,
                                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
                                c.column_default as default_value
                            FROM information_schema.columns c
                            LEFT JOIN (
                                SELECT ku.column_name
                                FROM information_schema.table_constraints tc
                                JOIN information_schema.key_column_usage ku
                                    ON tc.constraint_name = ku.constraint_name
                                WHERE tc.constraint_type = 'PRIMARY KEY'
                                    AND tc.table_schema = %s
                                    AND tc.table_name = %s
                            ) pk ON c.column_name = pk.column_name
                            WHERE c.table_schema = %s
                                AND c.table_name = %s
                            ORDER BY c.ordinal_position
                        """, (schema_name, table_name, schema_name, table_name))

                        columns = cursor.fetchall()

                        column_list = []
                        for col in columns:
                            column_list.append({
                                "name": col['column_name'],
                                "data_type": col['data_type'],
                                "is_nullable": col['is_nullable'],
                                "is_primary_key": col['is_primary_key'],
                                "default_value": col['default_value']
                            })

                        metadata_list.append({
                            "connection_id": connection_id,
                            "object_type": "table",
                            "schema_name": schema_name,
                            "object_name": table_name,
                            "columns": column_list
                        })

                    # Get views
                    cursor.execute("""
                        SELECT
                            schemaname as schema_name,
                            viewname as view_name
                        FROM pg_views
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, viewname
                    """)

                    views = cursor.fetchall()

                    for view in views:
                        schema_name = view['schema_name']
                        view_name = view['view_name']

                        # Get columns for this view (similar to tables)
                        cursor.execute("""
                            SELECT
                                column_name,
                                data_type,
                                is_nullable = 'YES' as is_nullable,
                                false as is_primary_key,  -- Views don't have primary keys
                                NULL as default_value
                            FROM information_schema.columns
                            WHERE table_schema = %s
                                AND table_name = %s
                            ORDER BY ordinal_position
                        """, (schema_name, view_name))

                        columns = cursor.fetchall()

                        column_list = []
                        for col in columns:
                            column_list.append({
                                "name": col['column_name'],
                                "data_type": col['data_type'],
                                "is_nullable": col['is_nullable'],
                                "is_primary_key": col['is_primary_key'],
                                "default_value": col['default_value']
                            })

                        metadata_list.append({
                            "connection_id": connection_id,
                            "object_type": "view",
                            "schema_name": schema_name,
                            "object_name": view_name,
                            "columns": column_list
                        })

                return metadata_list

            finally:
                conn.close()

        except Exception as e:
            raise DatabaseServiceError(f"Failed to extract database metadata: {str(e)}")

    async def execute_query(self, db: AsyncSession, database_name: str, sql: str, max_rows: int = 1000, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Execute a SQL query against the specified database with timeout handling."""
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

            # Parse database URL
            parsed = urlparse(database_conn.url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password

            import time
            start_time = time.time()

            # Connect to PostgreSQL and execute query with timeout
            try:
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    connect_timeout=10  # Connection timeout
                )

                try:
                    cursor = conn.cursor()
                    
                    # Set statement timeout for the query
                    cursor.execute(f"SET statement_timeout = {timeout_seconds * 1000}")  # Convert to milliseconds

                    # Execute the query
                    cursor.execute(sql)

                    # Get column names
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    # Fetch all rows (with limit)
                    rows = cursor.fetchall()
                    truncated = len(rows) > max_rows

                    if truncated:
                        rows = rows[:max_rows]

                    # Convert rows to list of lists (JSON serializable)
                    rows = [list(row) for row in rows]

                    execution_time_ms = int((time.time() - start_time) * 1000)

                    return {
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows),
                        "execution_time_ms": execution_time_ms,
                        "truncated": truncated
                    }

                finally:
                    conn.close()

            except psycopg2.OperationalError as e:
                error_msg = str(e).lower()
                if 'timeout' in error_msg or 'canceling statement due to statement timeout' in error_msg:
                    raise categorize_timeout_error("Query execution", timeout_seconds)
                else:
                    raise categorize_psycopg2_error(e)
            
            except psycopg2.Error as e:
                raise categorize_psycopg2_error(e)

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
