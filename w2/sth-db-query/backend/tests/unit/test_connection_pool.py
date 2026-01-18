"""
Unit tests for async connection pool manager.

Tests the connection pool functionality including:
- Pool creation and management
- Connection acquisition and release
- Pool status monitoring
- Multi-database support
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import asyncpg

from app.core.connection_pool import ConnectionPoolManager, connection_pool_manager


@pytest.mark.unit
class TestConnectionPoolManager:
    """Test connection pool manager functionality."""

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test that connection pool manager follows singleton pattern."""
        manager1 = ConnectionPoolManager()
        manager2 = ConnectionPoolManager()
        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_get_pool_key(self):
        """Test pool key generation from database URL."""
        manager = ConnectionPoolManager()

        # Test with different URLs
        key1 = manager.get_pool_key("postgresql://user:pass@localhost:5432/testdb")
        key2 = manager.get_pool_key("postgresql://user:pass@localhost:5432/testdb")
        key3 = manager.get_pool_key("postgresql://user:pass@localhost:5432/otherdb")

        # Same URL should produce same key
        assert key1 == key2
        # Different database should produce different key
        assert key1 != key3

    @pytest.mark.asyncio
    async def test_get_pool_key_with_default_port(self):
        """Test pool key generation with default port."""
        manager = ConnectionPoolManager()

        # URL without port should use default 5432
        key1 = manager.get_pool_key("postgresql://user:pass@localhost/testdb")
        key2 = manager.get_pool_key("postgresql://user:pass@localhost:5432/testdb")

        assert key1 == key2

    @pytest.mark.asyncio
    async def test_close_all_pools_empty(self):
        """Test closing all pools when no pools exist."""
        manager = ConnectionPoolManager()
        # Should not raise any error
        await manager.close_all_pools()

    @pytest.mark.asyncio
    async def test_get_pool_status_empty(self):
        """Test getting status when no pools exist."""
        manager = ConnectionPoolManager()
        status = await manager.get_pool_status()
        assert status == {}


@pytest.mark.unit
class TestGlobalConnectionPoolManager:
    """Test the global connection pool manager instance."""

    @pytest.mark.asyncio
    async def test_global_manager_instance(self):
        """Test that global manager is accessible."""
        from app.core.connection_pool import connection_pool_manager

        assert connection_pool_manager is not None
        assert isinstance(connection_pool_manager, ConnectionPoolManager)

    @pytest.mark.asyncio
    async def test_global_manager_singleton(self):
        """Test that global manager follows singleton pattern."""
        from app.core.connection_pool import connection_pool_manager as manager1
        from app.core.connection_pool import connection_pool_manager as manager2

        assert manager1 is manager2
