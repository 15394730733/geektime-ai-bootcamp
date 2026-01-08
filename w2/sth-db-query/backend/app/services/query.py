"""
Query execution service with SQL validation and result formatting.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import psycopg2
import psycopg2.extras
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_and_sanitize_sql
from app.core.errors import ValidationError, SQLSyntaxError
from app.core.config import settings
from app.services.database import DatabaseService


class QueryExecutionError(Exception):
    """Exception raised when query execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class QueryService:
    """Service for executing SQL queries with validation and formatting."""

    def __init__(self):
        self.database_service = DatabaseService()

    async def execute_query(
        self, 
        db: AsyncSession, 
        database_name: str, 
        sql: str
    ) -> Dict[str, Any]:
        """
        Execute a SQL query with validation and result formatting.

        Args:
            db: Database session
            database_name: Name of the database connection
            sql: SQL query to execute

        Returns:
            Dictionary containing query results with camelCase field names

        Raises:
            QueryExecutionError: If query validation or execution fails
        """
        try:
            # Validate and sanitize the SQL query
            validated_sql = validate_and_sanitize_sql(sql)
            
            # Get the database connection
            database_conn = await self.database_service.get_database(db, database_name)
            if not database_conn:
                raise QueryExecutionError(f"Database '{database_name}' not found")

            # Execute the query with timeout
            result = await self._execute_with_timeout(
                database_conn.url, 
                validated_sql,
                settings.query_timeout_seconds
            )

            # Format results with camelCase field names
            formatted_result = self._format_query_result(result, validated_sql)
            
            return formatted_result

        except (ValidationError, SQLSyntaxError) as e:
            raise QueryExecutionError(f"SQL validation failed: {e.message}", {
                "type": "validation_error",
                "sql": sql,
                "error": e.message
            })
        except psycopg2.Error as e:
            raise QueryExecutionError(f"Database query failed: {str(e)}", {
                "type": "database_error",
                "sql": sql,
                "error": str(e)
            })
        except asyncio.TimeoutError:
            raise QueryExecutionError(
                f"Query timed out after {settings.query_timeout_seconds} seconds", {
                "type": "timeout_error",
                "sql": sql,
                "timeout_seconds": settings.query_timeout_seconds
            })
        except Exception as e:
            raise QueryExecutionError(f"Query execution failed: {str(e)}", {
                "type": "execution_error",
                "sql": sql,
                "error": str(e)
            })

    async def _execute_with_timeout(
        self, 
        database_url: str, 
        sql: str, 
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """
        Execute query with timeout handling.

        Args:
            database_url: Database connection URL
            sql: Validated SQL query
            timeout_seconds: Query timeout in seconds

        Returns:
            Raw query results

        Raises:
            asyncio.TimeoutError: If query exceeds timeout
            psycopg2.Error: If database operation fails
        """
        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._execute_sync_query, database_url, sql),
                timeout=timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            # Re-raise timeout error for proper handling
            raise

    def _execute_sync_query(self, database_url: str, sql: str) -> Dict[str, Any]:
        """
        Execute query synchronously against PostgreSQL database.

        Args:
            database_url: Database connection URL
            sql: Validated SQL query

        Returns:
            Dictionary containing raw query results

        Raises:
            psycopg2.Error: If database operation fails
        """
        # Parse database URL
        parsed = urlparse(database_url)
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/')
        username = parsed.username
        password = parsed.password

        start_time = time.time()

        # Connect to PostgreSQL and execute query
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=10  # Connection timeout
        )

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Execute the query
                cursor.execute(sql)

                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert RealDictRow to regular dict for JSON serialization
                rows = [dict(row) for row in rows]

                execution_time_ms = int((time.time() - start_time) * 1000)

                return {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time_ms": execution_time_ms,
                    "query": sql
                }

        finally:
            conn.close()

    def _format_query_result(self, raw_result: Dict[str, Any], original_sql: str) -> Dict[str, Any]:
        """
        Format query results with camelCase field names.

        Args:
            raw_result: Raw query results from database
            original_sql: Original SQL query for reference

        Returns:
            Formatted results with camelCase field names
        """
        # Convert snake_case column names to camelCase
        formatted_columns = [self._to_camel_case(col) for col in raw_result["columns"]]
        
        # Convert row data to use camelCase keys
        formatted_rows = []
        for row in raw_result["rows"]:
            formatted_row = {}
            for original_key, value in row.items():
                camel_key = self._to_camel_case(original_key)
                formatted_row[camel_key] = value
            formatted_rows.append(formatted_row)

        return {
            "columns": formatted_columns,
            "rows": formatted_rows,
            "rowCount": raw_result["row_count"],
            "executionTime": raw_result["execution_time_ms"],
            "query": original_sql
        }

    def _to_camel_case(self, snake_str: str) -> str:
        """
        Convert snake_case string to camelCase.

        Args:
            snake_str: String in snake_case format

        Returns:
            String in camelCase format
        """
        if not snake_str:
            return snake_str
            
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])

    async def validate_query(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query without executing it.

        Args:
            sql: SQL query to validate

        Returns:
            Validation result with status and details
        """
        try:
            validated_sql = validate_and_sanitize_sql(sql)
            return {
                "valid": True,
                "sanitizedSql": validated_sql,
                "message": "Query is valid"
            }
        except SQLValidationError as e:
            return {
                "valid": False,
                "error": e.message,
                "message": f"Validation failed: {e.message}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": f"Validation error: {str(e)}"
            }