"""
MySQL database adapter implementation.

This adapter provides MySQL-specific implementations for metadata extraction
and query execution using aiomysql.
"""

import aiomysql
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from app.core.db_adapter import DatabaseAdapter, ColumnInfo

logger = logging.getLogger(__name__)


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter using aiomysql."""

    def __init__(self):
        """Initialize MySQL adapter."""
        self.name = "MySQL"

    async def connect(self, database_url: str) -> aiomysql.Connection:
        """
        Establish a connection to MySQL database.

        Args:
            database_url: MySQL connection URL

        Returns:
            aiomysql connection object
        """
        from urllib.parse import urlparse

        parsed = urlparse(database_url)

        # Extract connection parameters
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        database = parsed.path.lstrip('/') if parsed.path else None
        username = parsed.username
        password = parsed.password

        connection = await aiomysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            db=database,
            autocommit=True,
            charset='utf8mb4',
            connect_timeout=10,
            read_default_file=None
        )

        return connection

    async def disconnect(self, connection: aiomysql.Connection) -> None:
        """
        Close the MySQL connection.

        Args:
            connection: aiomysql connection object
        """
        if connection:
            if not connection.closed:
                connection.close()

    async def test_connection(self, connection: aiomysql.Connection) -> bool:
        """
        Test if the MySQL connection is alive.

        Args:
            connection: aiomysql connection object

        Returns:
            True if connection is alive, False otherwise
        """
        try:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                return result[0] == 1 if result else False
        except Exception as e:
            logger.error(f"MySQL connection test failed: {str(e)}")
            return False

    async def get_tables(self, connection: aiomysql.Connection) -> List[Dict[str, Any]]:
        """
        Get list of tables in the MySQL database.

        Args:
            connection: aiomysql connection object

        Returns:
            List of table information dictionaries
        """
        query = """
            SELECT
                TABLE_SCHEMA as schema_name,
                TABLE_NAME as table_name
            FROM information_schema.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """

        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()

            return [
                {
                    'table_name': row.get('TABLE_NAME') or row.get('table_name'),
                    'schema_name': row.get('TABLE_SCHEMA') or row.get('schema_name')
                }
                for row in rows
                if (row.get('TABLE_NAME') or row.get('table_name')) and (row.get('TABLE_SCHEMA') or row.get('schema_name'))
            ]

    async def get_views(self, connection: aiomysql.Connection) -> List[Dict[str, Any]]:
        """
        Get list of views in the MySQL database.

        Args:
            connection: aiomysql connection object

        Returns:
            List of view information dictionaries
        """
        query = """
            SELECT
                TABLE_SCHEMA as schema_name,
                TABLE_NAME as view_name
            FROM information_schema.VIEWS
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """

        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()

            return [
                {
                    'view_name': row.get('TABLE_NAME') or row.get('table_name'),
                    'schema_name': row.get('TABLE_SCHEMA') or row.get('schema_name')
                }
                for row in rows
                if (row.get('TABLE_NAME') or row.get('table_name')) and (row.get('TABLE_SCHEMA') or row.get('schema_name'))
            ]

    async def get_columns(
        self,
        connection: aiomysql.Connection,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[ColumnInfo]:
        """
        Get column information for a specific MySQL table or view.

        Args:
            connection: aiomysql connection object
            table_name: Name of the table or view
            schema_name: Schema/database name (defaults to current database)

        Returns:
            List of ColumnInfo objects
        """
        if schema_name is None:
            # Get current database
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT DATABASE()")
                result = await cursor.fetchone()
                schema_name = result[0] if result else None

        if not schema_name:
            raise ValueError("Cannot determine schema/database name")

        query = """
            SELECT
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE = 'YES' as IS_NULLABLE,
                COALESCE(pk.COLUMN_NAME IS NOT NULL, false) as IS_PRIMARY_KEY,
                c.COLUMN_DEFAULT
            FROM information_schema.COLUMNS c
            LEFT JOIN (
                SELECT ku.COLUMN_NAME
                FROM information_schema.TABLE_CONSTRAINTS tc
                JOIN information_schema.KEY_COLUMN_USAGE ku
                    ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                    AND tc.TABLE_SCHEMA = %s
                    AND tc.TABLE_NAME = %s
            ) pk ON c.COLUMN_NAME = pk.COLUMN_NAME
            WHERE c.TABLE_SCHEMA = %s
                AND c.TABLE_NAME = %s
            ORDER BY c.ORDINAL_POSITION
        """

        async with connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (schema_name, table_name, schema_name, table_name))
            rows = await cursor.fetchall()

            return [
                ColumnInfo(
                    name=row.get('COLUMN_NAME') or row.get('column_name'),
                    data_type=row.get('DATA_TYPE') or row.get('data_type'),
                    is_nullable=bool(row.get('IS_NULLABLE') or row.get('is_nullable')),
                    is_primary_key=bool(row.get('IS_PRIMARY_KEY') or row.get('is_primary_key')),
                    default_value=row.get('COLUMN_DEFAULT') or row.get('column_default')
                )
                for row in rows
            ]

    async def get_primary_keys(
        self,
        connection: aiomysql.Connection,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[str]:
        """
        Get primary key column names for a MySQL table.

        Args:
            connection: aiomysql connection object
            table_name: Name of the table
            schema_name: Schema/database name (defaults to current database)

        Returns:
            List of primary key column names
        """
        if schema_name is None:
            # Get current database
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT DATABASE()")
                result = await cursor.fetchone()
                schema_name = result[0] if result else None

        if not schema_name:
            raise ValueError("Cannot determine schema/database name")

        query = """
            SELECT ku.COLUMN_NAME
            FROM information_schema.TABLE_CONSTRAINTS tc
            JOIN information_schema.KEY_COLUMN_USAGE ku
                ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                AND tc.TABLE_SCHEMA = %s
                AND tc.TABLE_NAME = %s
            ORDER BY ku.ORDINAL_POSITION
        """

        async with connection.cursor() as cursor:
            await cursor.execute(query, (schema_name, table_name))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def execute_query(
        self,
        connection: aiomysql.Connection,
        sql: str,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a SQL query against MySQL.

        Args:
            connection: aiomysql connection object
            sql: SQL query to execute
            timeout_seconds: Query timeout in seconds

        Returns:
            Dictionary with query results
        """
        import time

        start_time = time.time()

        # Set query timeout
        await self.set_query_timeout(connection, timeout_seconds)

        # Execute query
        sql_upper = sql.strip().upper()
        if sql_upper.startswith('SELECT') or sql_upper.startswith('WITH') or sql_upper.startswith('SHOW') or sql_upper.startswith('DESCRIBE'):
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql)
                rows = await cursor.fetchall()
                columns = list(rows[0].keys()) if rows else []
                row_count = len(rows)

                # Serialize values
                rows_list = [self._serialize_row(row) for row in rows]
        else:
            # For non-SELECT queries
            async with connection.cursor() as cursor:
                row_count = await cursor.execute(sql)
                columns = []
                rows_list = []

        execution_time_ms = int((time.time() - start_time) * 1000)

        return {
            'columns': columns,
            'rows': rows_list,
            'row_count': len(rows_list) if rows_list else row_count,
            'execution_time_ms': execution_time_ms,
        }

    def serialize_value(self, value: Any) -> Any:
        """
        Serialize a MySQL value to JSON-compatible format.

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

        # Handle bytes (BLOB in MySQL)
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')

        return value

    async def set_query_timeout(self, connection: aiomysql.Connection, timeout_seconds: int) -> None:
        """
        Set query timeout for MySQL connection.

        Args:
            connection: aiomysql connection object
            timeout_seconds: Timeout in seconds
        """
        try:
            # MySQL uses max_execution_time in milliseconds
            async with connection.cursor() as cursor:
                await cursor.execute(f"SET max_execution_time = {timeout_seconds * 1000}")
        except Exception as e:
            logger.warning(f"Failed to set MySQL query timeout: {str(e)}")

    def _serialize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize a MySQL row dict to JSON-compatible format.

        Args:
            row: Dictionary from aiomysql.DictCursor

        Returns:
            Dictionary with serialized values
        """
        return {key: self.serialize_value(value) for key, value in row.items()}
