"""
Database adapter interface.

This module defines the abstract interface for database adapters,
allowing the application to support multiple database types (PostgreSQL, MySQL, etc.)
through a unified API.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ColumnInfo:
    """Column metadata information."""
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    default_value: Optional[str] = None


@dataclass
class TableMetadata:
    """Table or view metadata."""
    name: str
    schema: str
    object_type: str  # 'table' or 'view'
    columns: List[ColumnInfo]


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.

    Each database type (PostgreSQL, MySQL, etc.) should implement this interface
    to provide unified metadata extraction and query execution capabilities.
    """

    @abstractmethod
    async def connect(self, database_url: str) -> Any:
        """
        Establish a connection to the database.

        Args:
            database_url: Database connection URL

        Returns:
            Database connection object
        """
        pass

    @abstractmethod
    async def disconnect(self, connection: Any) -> None:
        """
        Close the database connection.

        Args:
            connection: Database connection object to close
        """
        pass

    @abstractmethod
    async def test_connection(self, connection: Any) -> bool:
        """
        Test if the database connection is alive.

        Args:
            connection: Database connection object

        Returns:
            True if connection is alive, False otherwise
        """
        pass

    @abstractmethod
    async def get_tables(self, connection: Any) -> List[Dict[str, Any]]:
        """
        Get list of tables in the database.

        Args:
            connection: Database connection object

        Returns:
            List of table information dictionaries with keys:
            - table_name: Name of the table
            - schema_name: Schema name
        """
        pass

    @abstractmethod
    async def get_views(self, connection: Any) -> List[Dict[str, Any]]:
        """
        Get list of views in the database.

        Args:
            connection: Database connection object

        Returns:
            List of view information dictionaries with keys:
            - view_name: Name of the view
            - schema_name: Schema name
        """
        pass

    @abstractmethod
    async def get_columns(
        self,
        connection: Any,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[ColumnInfo]:
        """
        Get column information for a specific table or view.

        Args:
            connection: Database connection object
            table_name: Name of the table or view
            schema_name: Schema name (optional)

        Returns:
            List of ColumnInfo objects
        """
        pass

    @abstractmethod
    async def get_primary_keys(
        self,
        connection: Any,
        table_name: str,
        schema_name: Optional[str] = None
    ) -> List[str]:
        """
        Get primary key column names for a table.

        Args:
            connection: Database connection object
            table_name: Name of the table
            schema_name: Schema name (optional)

        Returns:
            List of primary key column names
        """
        pass

    @abstractmethod
    async def execute_query(
        self,
        connection: Any,
        sql: str,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Args:
            connection: Database connection object
            sql: SQL query to execute
            timeout_seconds: Query timeout in seconds

        Returns:
            Dictionary with keys:
            - columns: List of column names
            - rows: List of data rows (each row is a list)
            - row_count: Number of rows returned
            - execution_time_ms: Execution time in milliseconds
        """
        pass

    @abstractmethod
    def serialize_value(self, value: Any) -> Any:
        """
        Serialize a database value to JSON-compatible format.

        Args:
            value: Database value to serialize

        Returns:
            JSON-compatible value
        """
        pass

    @abstractmethod
    async def set_query_timeout(self, connection: Any, timeout_seconds: int) -> None:
        """
        Set query timeout for the connection.

        Args:
            connection: Database connection object
            timeout_seconds: Timeout in seconds
        """
        pass

    async def get_metadata(
        self,
        connection: Any,
        connection_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get complete metadata for all tables and views in the database.

        This is a convenience method that combines get_tables, get_views,
        and get_columns to provide complete metadata.

        Args:
            connection: Database connection object
            connection_id: Connection ID for metadata storage

        Returns:
            List of metadata dictionaries suitable for storage
        """
        metadata_list = []

        # Get tables
        tables = await self.get_tables(connection)
        for table_info in tables:
            table_name = table_info['table_name']
            schema_name = table_info.get('schema_name', 'public')

            columns = await self.get_columns(connection, table_name, schema_name)

            metadata_list.append({
                'connection_id': connection_id,
                'object_type': 'table',
                'schema_name': schema_name,
                'object_name': table_name,
                'columns': [
                    {
                        'name': col.name,
                        'data_type': col.data_type,
                        'is_nullable': col.is_nullable,
                        'is_primary_key': col.is_primary_key,
                        'default_value': col.default_value
                    }
                    for col in columns
                ]
            })

        # Get views
        views = await self.get_views(connection)
        for view_info in views:
            view_name = view_info['view_name']
            schema_name = view_info.get('schema_name', 'public')

            columns = await self.get_columns(connection, view_name, schema_name)

            metadata_list.append({
                'connection_id': connection_id,
                'object_type': 'view',
                'schema_name': schema_name,
                'object_name': view_name,
                'columns': [
                    {
                        'name': col.name,
                        'data_type': col.data_type,
                        'is_nullable': col.is_nullable,
                        'is_primary_key': col.is_primary_key,
                        'default_value': col.default_value
                    }
                    for col in columns
                ]
            })

        return metadata_list
