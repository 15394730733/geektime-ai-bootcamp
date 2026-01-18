"""
PostgreSQL database adapter implementation.

This adapter provides PostgreSQL-specific implementations for metadata extraction
and query execution using asyncpg.
"""

import asyncpg
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from app.core.db_adapter import DatabaseAdapter, ColumnInfo

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter using asyncpg."""

    def __init__(self):
        """Initialize PostgreSQL adapter."""
        self.name = "PostgreSQL"

    async def connect(self, database_url: str) -> asyncpg.Connection:
        """
        Establish a connection to PostgreSQL database.

        Args:
            database_url: PostgreSQL connection URL

        Returns:
            asyncpg connection object
        """
        return await asyncpg.connect(database_url)

    async def disconnect(self, connection: asyncpg.Connection) -> None:
        """
        Close the PostgreSQL connection.

        Args:
            connection: asyncpg connection object
        """
        await connection.close()

    async def test_connection(self, connection: asyncpg.Connection) -> bool:
        """
        Test if the PostgreSQL connection is alive.

        Args:
            connection: asyncpg connection object

        Returns:
            True if connection is alive, False otherwise
        """
        try:
            result = await connection.fetchval("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"PostgreSQL connection test failed: {str(e)}")
            return False

    async def get_tables(self, connection: asyncpg.Connection) -> List[Dict[str, Any]]:
        """
        Get list of tables in the PostgreSQL database.

        Args:
            connection: asyncpg connection object

        Returns:
            List of table information dictionaries
        """
        query = """
            SELECT
                schemaname as schema_name,
                tablename as table_name
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename
        """
        rows = await connection.fetch(query)
        return [
            {
                'table_name': row['table_name'],
                'schema_name': row['schema_name']
            }
            for row in rows
        ]

    async def get_views(self, connection: asyncpg.Connection) -> List[Dict[str, Any]]:
        """
        Get list of views in the PostgreSQL database.

        Args:
            connection: asyncpg connection object

        Returns:
            List of view information dictionaries
        """
        query = """
            SELECT
                schemaname as schema_name,
                viewname as view_name
            FROM pg_views
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, viewname
        """
        rows = await connection.fetch(query)
        return [
            {
                'view_name': row['view_name'],
                'schema_name': row['schema_name']
            }
            for row in rows
        ]

    async def get_columns(
        self,
        connection: asyncpg.Connection,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[ColumnInfo]:
        """
        Get column information for a specific PostgreSQL table or view.

        Args:
            connection: asyncpg connection object
            table_name: Name of the table or view
            schema_name: Schema name (defaults to 'public')

        Returns:
            List of ColumnInfo objects
        """
        if schema_name is None:
            schema_name = 'public'

        query = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as is_nullable,
                COALESCE(pk.column_name IS NOT NULL, false) as is_primary_key,
                c.column_default as default_value
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = $1
                    AND tc.table_name = $2
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_schema = $1
                AND c.table_name = $2
            ORDER BY c.ordinal_position
        """

        rows = await connection.fetch(query, schema_name, table_name)

        return [
            ColumnInfo(
                name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'],
                is_primary_key=row['is_primary_key'],
                default_value=row['default_value']
            )
            for row in rows
        ]

    async def get_primary_keys(
        self,
        connection: asyncpg.Connection,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[str]:
        """
        Get primary key column names for a PostgreSQL table.

        Args:
            connection: asyncpg connection object
            table_name: Name of the table
            schema_name: Schema name (defaults to 'public')

        Returns:
            List of primary key column names
        """
        if schema_name is None:
            schema_name = 'public'

        query = """
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = $1
                AND tc.table_name = $2
            ORDER BY ku.ordinal_position
        """

        rows = await connection.fetch(query, schema_name, table_name)
        return [row['column_name'] for row in rows]

    async def execute_query(
        self,
        connection: asyncpg.Connection,
        sql: str,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a SQL query against PostgreSQL.

        Args:
            connection: asyncpg connection object
            sql: SQL query to execute
            timeout_seconds: Query timeout in seconds

        Returns:
            Dictionary with query results
        """
        import time

        start_time = time.time()

        # Set statement timeout
        await self.set_query_timeout(connection, timeout_seconds)

        # Execute query
        sql_upper = sql.strip().upper()
        if sql_upper.startswith('SELECT') or sql_upper.startswith('WITH'):
            rows = await connection.fetch(sql)
            columns = list(rows[0].keys()) if rows else []
            row_count = len(rows)

            # Convert Record objects to dicts and serialize values
            rows_list = [self._serialize_row(row) for row in rows]
        else:
            # For non-SELECT queries
            result = await connection.execute(sql)
            columns = []
            rows_list = []
            row_count = 0

            # Get affected row count
            if 'SELECT' not in sql_upper:
                # Parse result string for row count
                if result:
                    match = result.split()[-1]
                    try:
                        row_count = int(match)
                    except ValueError:
                        row_count = 0

        execution_time_ms = int((time.time() - start_time) * 1000)

        return {
            'columns': columns,
            'rows': rows_list,
            'row_count': len(rows_list) if rows_list else row_count,
            'rowCount': len(rows_list) if rows_list else row_count,  # Frontend expects camelCase
            'execution_time_ms': execution_time_ms,
            'executionTimeMs': execution_time_ms,  # Frontend expects camelCase
        }

    def serialize_value(self, value: Any) -> Any:
        """
        Serialize a PostgreSQL value to JSON-compatible format.

        Args:
            value: Database value to serialize

        Returns:
            JSON-compatible value
        """
        if value is None:
            return None

        # Handle datetime
        if isinstance(value, datetime):
            return value.isoformat()

        # Handle date
        if isinstance(value, date):
            return value.isoformat()

        # Handle decimal
        if isinstance(value, Decimal):
            return float(value)

        # Handle bytes
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')

        return value

    async def set_query_timeout(self, connection: asyncpg.Connection, timeout_seconds: int) -> None:
        """
        Set query timeout for PostgreSQL connection.

        Args:
            connection: asyncpg connection object
            timeout_seconds: Timeout in seconds
        """
        await connection.execute(f"SET statement_timeout = {timeout_seconds * 1000}")

    def _serialize_row(self, row: asyncpg.Record) -> Dict[str, Any]:
        """
        Serialize an asyncpg Record to a dict with JSON-compatible values.

        Args:
            row: asyncpg Record object

        Returns:
            Dictionary with serialized values
        """
        return {key: self.serialize_value(value) for key, value in dict(row).items()}
