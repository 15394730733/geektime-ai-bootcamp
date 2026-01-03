"""
Database connection service layer with validation.
"""

import re
import psycopg2
import psycopg2.extras
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
        connection_test = await self._test_connection(database_data.url)
        if not connection_test["success"]:
            raise DatabaseServiceError(f"Database connection test failed: {connection_test['message']}")

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
        try:
            self._validate_url_format(url)

            # Actually test the database connection
            import time
            start_time = time.time()

            # Parse URL and test connection
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password

            # Test connection synchronously (since this is called from async context)
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=10  # 10 second timeout
            )
            conn.close()

            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "message": "Database connection successful",
                "latency_ms": latency_ms
            }
        except psycopg2.OperationalError as e:
            return {
                "success": False,
                "message": f"Database connection failed: {str(e)}",
                "error": str(e)
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
                "message": f"Unexpected error during connection test: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Connection test failed",
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

    async def execute_query(self, db: AsyncSession, database_name: str, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """Execute a SQL query against the specified database."""
        try:
            # Get the database connection
            database_conn = await self.get_database(db, database_name)
            if not database_conn:
                raise DatabaseServiceError(f"Database '{database_name}' not found")

            # Parse database URL
            parsed = urlparse(database_conn.url)
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            username = parsed.username
            password = parsed.password

            import time
            start_time = time.time()

            # Connect to PostgreSQL and execute query
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )

            try:
                cursor = conn.cursor()

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

        except psycopg2.Error as e:
            raise DatabaseServiceError(f"Database query failed: {str(e)}")
        except Exception as e:
            raise DatabaseServiceError(f"Query execution failed: {str(e)}")
