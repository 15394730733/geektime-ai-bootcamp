"""
Multi-database connection pool manager.

This module provides an async connection pool manager that supports both
PostgreSQL (asyncpg) and MySQL (aiomysql) databases.
"""

import asyncio
from typing import Dict, Optional, Any, Union
from urllib.parse import urlparse
import asyncpg
import aiomysql
import logging

from app.core.config import settings
from app.core.db_type_detector import DatabaseType, DatabaseTypeDetector

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """
    Async manager for multi-database connection pools.

    Maintains separate pools for PostgreSQL and MySQL databases,
    allowing connections to multiple databases of different types.
    """

    _instance: Optional['ConnectionPoolManager'] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        """Implement singleton pattern for async safety."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._postgres_pools: Dict[str, asyncpg.Pool] = {}
            cls._instance._mysql_pools: Dict[str, aiomysql.Pool] = {}
            cls._instance._pool_lock = asyncio.Lock()
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the connection pool manager."""
        if not hasattr(self, '_initialized'):
            self._postgres_pools: Dict[str, asyncpg.Pool] = {}
            self._mysql_pools: Dict[str, aiomysql.Pool] = {}
            self._pool_lock = asyncio.Lock()
            self._initialized = True

    def get_pool_key(self, database_url: str) -> str:
        """
        Generate a unique key for the connection pool based on database URL.

        Args:
            database_url: Database connection URL

        Returns:
            Unique pool key string
        """
        # Parse URL and create key from host, port, and database
        parsed = urlparse(database_url)
        db_type = DatabaseTypeDetector.detect(database_url)

        default_port = 5432 if db_type == DatabaseType.POSTGRESQL else 3306
        key = f"{db_type.value}/{parsed.hostname}:{parsed.port or default_port}/{parsed.path.lstrip('/')}"
        return key

    async def get_pool(self, database_url: str) -> Union[asyncpg.Pool, aiomysql.Pool]:
        """
        Get or create a connection pool for the given database URL.

        Args:
            database_url: Database connection URL (PostgreSQL or MySQL)

        Returns:
            Async connection pool for the database

        Raises:
            ValueError: If database type is not supported
        """
        pool_key = self.get_pool_key(database_url)
        db_type = DatabaseTypeDetector.detect(database_url)

        # Check if pool already exists
        async with self._pool_lock:
            if db_type == DatabaseType.POSTGRESQL:
                return await self._get_postgres_pool(database_url, pool_key)
            elif db_type == DatabaseType.MYSQL:
                return await self._get_mysql_pool(database_url, pool_key)
            else:
                raise ValueError(f"Unsupported database type: {db_type.value}")

    async def _get_postgres_pool(self, database_url: str, pool_key: str) -> asyncpg.Pool:
        """Get or create PostgreSQL connection pool."""
        if pool_key in self._postgres_pools:
            return self._postgres_pools[pool_key]

        # Parse database URL
        parsed = urlparse(database_url)
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/')
        username = parsed.username
        password = parsed.password

        # Create new pool with asyncpg
        try:
            connection_pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                min_size=1,
                max_size=10,
                command_timeout=60,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,
                setup=self._setup_postgres_connection,
                init=self._init_postgres_connection
            )

            self._postgres_pools[pool_key] = connection_pool
            logger.info(f"Created asyncpg connection pool for {pool_key} (min=1, max=10)")
            return connection_pool

        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool for {pool_key}: {str(e)}")
            raise

    async def _get_mysql_pool(self, database_url: str, pool_key: str) -> aiomysql.Pool:
        """Get or create MySQL connection pool."""
        if pool_key in self._mysql_pools:
            return self._mysql_pools[pool_key]

        # Parse database URL
        parsed = urlparse(database_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        database = parsed.path.lstrip('/') if parsed.path else None
        username = parsed.username
        password = parsed.password

        # Create new pool with aiomysql
        try:
            connection_pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=username,
                password=password,
                db=database,
                minsize=1,
                maxsize=10,
                autocommit=True,
                charset='utf8mb4'
            )

            self._mysql_pools[pool_key] = connection_pool
            logger.info(f"Created aiomysql connection pool for {pool_key} (min=1, max=10)")
            return connection_pool

        except Exception as e:
            logger.error(f"Failed to create MySQL connection pool for {pool_key}: {str(e)}")
            raise

    async def _setup_postgres_connection(self, conn):
        """Setup PostgreSQL connection configuration after acquiring from pool."""
        # Set default statement timeout
        await conn.execute(f"SET statement_timeout = {settings.query_timeout_seconds * 1000}")

    async def _init_postgres_connection(self, conn):
        """Initialize PostgreSQL connection when first created."""
        # Any one-time initialization can go here
        pass

    async def get_connection(self, database_url: str) -> Union[asyncpg.Connection, aiomysql.Connection]:
        """
        Get a connection from the pool.

        Args:
            database_url: Database connection URL

        Returns:
            Database connection from the pool

        Raises:
            Exception: If connection cannot be obtained
        """
        try:
            conn_pool = await self.get_pool(database_url)
            db_type = DatabaseTypeDetector.detect(database_url)

            if db_type == DatabaseType.POSTGRESQL:
                connection = await conn_pool.acquire()
            elif db_type == DatabaseType.MYSQL:
                connection = await conn_pool.acquire()
            else:
                raise ValueError(f"Unsupported database type: {db_type.value}")

            logger.debug(f"Got connection from pool for {self.get_pool_key(database_url)}")
            return connection

        except Exception as e:
            logger.error(f"Failed to get connection from pool: {str(e)}")
            raise

    async def return_connection(self, database_url: str, connection: Union[asyncpg.Connection, aiomysql.Connection]):
        """
        Return a connection back to the pool.

        Args:
            database_url: Database connection URL
            connection: Database connection to return
        """
        try:
            pool_key = self.get_pool_key(database_url)
            db_type = DatabaseTypeDetector.detect(database_url)

            if db_type == DatabaseType.POSTGRESQL and pool_key in self._postgres_pools:
                await self._postgres_pools[pool_key].release(connection)
                logger.debug(f"Returned PostgreSQL connection to pool for {pool_key}")
            elif db_type == DatabaseType.MYSQL and pool_key in self._mysql_pools:
                await self._mysql_pools[pool_key].release(connection)
                logger.debug(f"Returned MySQL connection to pool for {pool_key}")

        except Exception as e:
            logger.error(f"Failed to return connection to pool: {str(e)}")

    async def close_all_pools(self):
        """Close all connection pools and cleanup resources."""
        async with self._pool_lock:
            # Close PostgreSQL pools
            for pool_key, conn_pool in self._postgres_pools.items():
                try:
                    await conn_pool.close()
                    logger.info(f"Closed PostgreSQL connection pool for {pool_key}")
                except Exception as e:
                    logger.error(f"Error closing PostgreSQL pool for {pool_key}: {str(e)}")

            # Close MySQL pools
            for pool_key, conn_pool in self._mysql_pools.items():
                try:
                    conn_pool.close()
                    await conn_pool.wait_closed()
                    logger.info(f"Closed MySQL connection pool for {pool_key}")
                except Exception as e:
                    logger.error(f"Error closing MySQL pool for {pool_key}: {str(e)}")

            self._postgres_pools.clear()
            self._mysql_pools.clear()
            logger.info("All connection pools closed")

    async def get_pool_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all connection pools.

        Returns:
            Dictionary with pool status information
        """
        status = {}
        async with self._pool_lock:
            # PostgreSQL pools
            for pool_key, conn_pool in self._postgres_pools.items():
                status[pool_key] = {
                    "database_type": "postgresql",
                    "min_size": conn_pool.get_min_size(),
                    "max_size": conn_pool.get_max_size(),
                    "size": conn_pool.get_size(),
                    "available": conn_pool.get_idle_size(),
                    "closed": conn_pool._closed
                }

            # MySQL pools
            for pool_key, conn_pool in self._mysql_pools.items():
                status[pool_key] = {
                    "database_type": "mysql",
                    "min_size": conn_pool.minsize,
                    "max_size": conn_pool.maxsize,
                    "size": conn_pool.size,
                    "closed": conn_pool.closed
                }

        return status


# Global connection pool manager instance
connection_pool_manager = ConnectionPoolManager()
