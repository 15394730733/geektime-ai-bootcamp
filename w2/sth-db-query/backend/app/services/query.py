"""
Query execution service with SQL validation and result formatting using asyncpg.
"""

import asyncio
import time
from typing import Dict, Any, Optional
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_and_sanitize_sql
from app.core.errors import ValidationError, SQLSyntaxError
from app.core.config import settings
from app.services.database import DatabaseService
from app.core.connection_pool import connection_pool_manager
from app.core.performance import performance_monitor, get_query_id


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
        query_id = get_query_id()

        try:
            # Validate and sanitize the SQL query
            validated_sql = validate_and_sanitize_sql(sql)

            # Get the database connection
            database_conn = await self.database_service.get_database(db, database_name)
            if not database_conn:
                raise QueryExecutionError(f"Database '{database_name}' not found")

            # Start performance monitoring
            performance_monitor.start_query(query_id, validated_sql, database_name)

            # Execute the query with timeout
            result = await self._execute_with_timeout(
                database_conn.url,
                validated_sql,
                settings.query_timeout_seconds
            )

            # End performance monitoring (success)
            performance_monitor.end_query(
                query_id,
                success=True,
                row_count=result.get("row_count", 0)
            )

            # Format results with camelCase field names
            formatted_result = self._format_query_result(result, validated_sql)

            return formatted_result

        except (ValidationError, SQLSyntaxError) as e:
            # End performance monitoring (failure)
            performance_monitor.end_query(
                query_id,
                success=False,
                error_message=e.message
            )
            raise QueryExecutionError(f"SQL validation failed: {e.message}", {
                "type": "validation_error",
                "sql": sql,
                "error": e.message
            })
        except asyncpg.PostgresError as e:
            # End performance monitoring (failure)
            performance_monitor.end_query(
                query_id,
                success=False,
                error_message=str(e)
            )
            raise QueryExecutionError(f"Database query failed: {str(e)}", {
                "type": "database_error",
                "sql": sql,
                "error": str(e)
            })
        except asyncio.TimeoutError:
            # End performance monitoring (failure)
            performance_monitor.end_query(
                query_id,
                success=False,
                error_message="Query timed out"
            )
            raise QueryExecutionError(
                f"Query timed out after {settings.query_timeout_seconds} seconds", {
                "type": "timeout_error",
                "sql": sql,
                "timeout_seconds": settings.query_timeout_seconds
            })
        except Exception as e:
            # End performance monitoring (failure)
            performance_monitor.end_query(
                query_id,
                success=False,
                error_message=str(e)
            )
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
        Execute query with timeout handling using asyncpg connection pool.

        Args:
            database_url: Database connection URL
            sql: Validated SQL query
            timeout_seconds: Query timeout in seconds

        Returns:
            Raw query results

        Raises:
            asyncio.TimeoutError: If query exceeds timeout
            asyncpg.PostgresError: If database operation fails
        """
        # Get connection from pool
        conn = await connection_pool_manager.get_connection(database_url)

        try:
            # Set query timeout
            await conn.execute(f"SET statement_timeout = {timeout_seconds * 1000}")

            # Execute query and fetch results
            start_time = time.time()

            # Use fetch for SELECT queries, execute for others
            sql_upper = sql.strip().upper()
            if sql_upper.startswith('SELECT') or sql_upper.startswith('WITH'):
                rows = await conn.fetch(sql)
                columns = list(rows[0].keys()) if rows else []
                row_count = len(rows)
            else:
                result = await conn.execute(sql)
                # For non-SELECT queries, get affected rows from result
                rows = []
                columns = []
                row_count = 0
                if result:
                    # Parse result string like "INSERT 0 1" or "UPDATE 1"
                    parts = result.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        row_count = int(parts[1])

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Convert Record objects to dicts
            rows_list = [dict(row) for row in rows]

            return {
                "columns": columns,
                "rows": rows_list,
                "row_count": row_count,
                "execution_time_ms": execution_time_ms,
                "query": sql
            }

        finally:
            # Return connection to pool
            await connection_pool_manager.return_connection(database_url, conn)

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
                # Handle asyncpg data types for JSON serialization
                formatted_row[camel_key] = self._serialize_value(value)
            formatted_rows.append(formatted_row)

        return {
            "columns": formatted_columns,
            "rows": formatted_rows,
            "rowCount": raw_result["row_count"],
            "executionTime": raw_result["execution_time_ms"],
            "query": original_sql
        }

    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize asyncpg data types for JSON.

        Args:
            value: Value from asyncpg

        Returns:
            JSON-serializable value
        """
        # Handle asyncpg specific types
        if isinstance(value, asyncpg.pgproto.UUID):
            return str(value)
        elif isinstance(value, (asyncpg.pgproto.numeric.Numeric,)):
            return float(value)
        elif isinstance(value, (bytes, bytearray)):
            return value.decode('utf-8', errors='replace')
        # Handle datetime, date, time objects
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        else:
            return value

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
        except ValidationError as e:
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
