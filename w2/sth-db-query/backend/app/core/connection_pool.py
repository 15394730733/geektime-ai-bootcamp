"""
Async database connection pool manager for PostgreSQL connections.

This module provides an async connection pool using asyncpg to improve performance
by reusing database connections instead of creating a new one for each query.
"""

import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
import asyncpg
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """
    Async manager for PostgreSQL connection pools using asyncpg.

    Maintains a separate pool for each unique database URL to allow
    connections to multiple databases.
    """

    _instance: Optional['ConnectionPoolManager'] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        """Implement singleton pattern for async safety."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pools: Dict[str, asyncpg.Pool] = {}
            cls._instance._pool_lock = asyncio.Lock()
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the connection pool manager."""
        if not hasattr(self, '_initialized'):
            self._pools: Dict[str, asyncpg.Pool] = {}
            self._pool_lock = asyncio.Lock()
            self._initialized = True

    def get_pool_key(self, database_url: str) -> str:
        """
        Generate a unique key for the connection pool based on database URL.

        Args:
            database_url: PostgreSQL connection URL

        Returns:
            Unique pool key string
        """
        # Parse URL and create key from host, port, and database
        parsed = urlparse(database_url)
        key = f"{parsed.hostname}:{parsed.port or 5432}/{parsed.path.lstrip('/')}"
        return key

    async def get_pool(self, database_url: str) -> asyncpg.Pool:
        """
        Get or create a connection pool for the given database URL.

        Args:
            database_url: PostgreSQL connection URL

        Returns:
            Async connection pool for the database
        """
        pool_key = self.get_pool_key(database_url)

        # Check if pool already exists
        async with self._pool_lock:
            if pool_key in self._pools:
                return self._pools[pool_key]

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
                    max_size=10,  # Maximum 10 connections per database
                    command_timeout=60,
                    max_queries=50000,  # Reset connection after 50000 queries
                    max_inactive_connection_lifetime=300.0,  # 5 minutes
                    setup=self._setup_connection,
                    init=self._init_connection
                )

                self._pools[pool_key] = connection_pool
                logger.info(f"Created asyncpg connection pool for {pool_key} (min=1, max=10)")
                return connection_pool

            except Exception as e:
                logger.error(f"Failed to create connection pool for {pool_key}: {str(e)}")
                raise

    async def _setup_connection(self, conn):
        """
        Setup connection configuration after acquiring from pool.

        Args:
            conn: asyncpg connection
        """
        # Set default statement timeout
        await conn.execute(f"SET statement_timeout = {settings.query_timeout_seconds * 1000}")

    async def _init_connection(self, conn):
        """
        Initialize connection when first created.

        Args:
            conn: asyncpg connection
        """
        # Any one-time initialization can go here
        pass

    async def get_connection(self, database_url: str) -> asyncpg.Connection:
        """
        Get a connection from the pool.

        Args:
            database_url: PostgreSQL connection URL

        Returns:
            Database connection from the pool

        Raises:
            Exception: If connection cannot be obtained
        """
        try:
            conn_pool = await self.get_pool(database_url)
            connection = await conn_pool.acquire()
            logger.debug(f"Got connection from pool for {self.get_pool_key(database_url)}")
            return connection
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {str(e)}")
            raise

    async def return_connection(self, database_url: str, connection: asyncpg.Connection):
        """
        Return a connection back to the pool.

        Args:
            database_url: PostgreSQL connection URL
            connection: Database connection to return
        """
        try:
            pool_key = self.get_pool_key(database_url)
            if pool_key in self._pools:
                await self._pools[pool_key].release(connection)
                logger.debug(f"Returned connection to pool for {pool_key}")
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {str(e)}")

    async def close_all_pools(self):
        """Close all connection pools and cleanup resources."""
        async with self._pool_lock:
            for pool_key, conn_pool in self._pools.items():
                try:
                    await conn_pool.close()
                    logger.info(f"Closed connection pool for {pool_key}")
                except Exception as e:
                    logger.error(f"Error closing pool for {pool_key}: {str(e)}")

            self._pools.clear()
            logger.info("All connection pools closed")

    async def get_pool_status(self) -> Dict[str, Dict[str, any]]:
        """
        Get status information for all connection pools.

        Returns:
            Dictionary with pool status information
        """
        status = {}
        async with self._pool_lock:
            for pool_key, conn_pool in self._pools.items():
                # Get pool statistics from asyncpg
                status[pool_key] = {
                    "min_size": conn_pool.get_min_size(),
                    "max_size": conn_pool.get_max_size(),
                    "size": conn_pool.get_size(),
                    "available": conn_pool.get_idle_size(),
                    "closed": conn_pool._closed  # Access internal attribute
                }
        return status


# Global connection pool manager instance
connection_pool_manager = ConnectionPoolManager()
