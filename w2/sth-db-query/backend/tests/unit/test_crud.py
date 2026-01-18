"""
Unit tests for database connection CRUD operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.database import (
    get_databases,
    get_database,
    create_database,
    update_database,
    delete_database
)
from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate


# Helper to run async functions in sync tests
def async_return(value):
    """Create a mock async function that returns a value."""
    async def _async_return(*args, **kwargs):
        return value
    return _async_return


def async_raise(exception):
    """Create a mock async function that raises an exception."""
    async def _async_raise(*args, **kwargs):
        raise exception
    return _async_raise


class TestDatabaseCRUD:
    """Test database connection CRUD operations."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session.

        创建模拟的数据库会话对象：
        - 使用AsyncMock模拟异步数据库操作
        - 为CRUD操作测试提供基础mock对象
        """
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_connection_data(self):
        """Sample database connection data.

        提供示例数据库连接数据：
        - 包含创建数据库连接所需的基本字段
        - 用于各种CRUD操作的测试数据
        """
        return DatabaseCreate(
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database"
        )

    @pytest.fixture
    def sample_connection(self):
        """Sample DatabaseConnection instance.

        提供示例DatabaseConnection实例：
        - 包含完整的数据库连接模型数据
        - 用于读取、更新、删除操作的测试
        """
        return DatabaseConnection(
            id="test-conn-1",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database",
            is_active=True
        )

    @pytest.mark.asyncio
    async def test_get_databases_success(self, mock_db_session):
        """Test successful retrieval of all database connections.

        测试成功获取所有数据库连接：
        - 模拟数据库中存在多个连接记录
        - 验证返回正确的连接列表
        - 检查数据库查询被正确调用
        """
        # Mock the query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            DatabaseConnection(id="1", name="db1", url="postgresql://localhost/db1"),
            DatabaseConnection(id="2", name="db2", url="postgresql://localhost/db2")
        ]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Execute the function
        result = await get_databases(mock_db_session)

        # Assertions
        assert len(result) == 2
        assert result[0].name == "db1"
        assert result[1].name == "db2"
        assert mock_db_session.execute.called
        assert mock_db_session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_get_databases_empty(self, mock_db_session):
        """Test retrieval when no database connections exist.

        测试获取空数据库连接列表：
        - 模拟数据库中没有任何连接记录
        - 验证返回空列表
        - 确保查询仍然被正确执行
        """
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await get_databases(mock_db_session)

        assert result == []
        assert mock_db_session.execute.called
        assert mock_db_session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_get_database_found(self, mock_db_session, sample_connection):
        """Test successful retrieval of a specific database connection.

        测试成功获取特定数据库连接：
        - 模拟按名称查找存在的连接
        - 验证返回正确的连接实例
        - 检查查询参数和调用次数
        """
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await get_database(mock_db_session, "test_db")

        assert result is sample_connection
        assert result.name == "test_db"
        assert mock_db_session.execute.called
        assert mock_db_session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_get_database_not_found(self, mock_db_session):
        """Test retrieval of non-existent database connection.

        测试获取不存在的数据库连接：
        - 模拟查找不存在的连接名称
        - 验证返回None值
        - 确保查询仍然被执行
        """
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await get_database(mock_db_session, "nonexistent")

        assert result is None
        assert mock_db_session.execute.called
        assert mock_db_session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_create_database_success(self, mock_db_session, sample_connection_data):
        """Test successful creation of a database connection.

        测试成功创建数据库连接：
        - 模拟完整的创建流程（添加、提交、刷新）
        - 验证返回的连接对象包含正确的数据
        - 检查所有数据库操作都被调用
        """
        created_connection = DatabaseConnection(
            id="generated-id",
            name=sample_connection_data.name,
            url=sample_connection_data.url,
            description=sample_connection_data.description,
            is_active=True
        )

        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = async_return(None)

        # Mock the refresh to set the returned object
        def refresh_side_effect(obj):
            obj.id = "generated-id"
        mock_db_session.refresh = AsyncMock(side_effect=refresh_side_effect)

        result = await create_database(mock_db_session, sample_connection_data)

        assert result.name == sample_connection_data.name
        assert result.url == sample_connection_data.url
        assert result.description == sample_connection_data.description
        assert result.id is not None  # ID should be generated
        assert len(result.id) > 0

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_database_success(self, mock_db_session, sample_connection, sample_connection_data):
        """Test successful update of a database connection.

        测试成功更新数据库连接：
        - 模拟查找现有连接并更新其属性
        - 验证连接信息被正确修改
        - 检查提交和刷新操作被调用
        """
        # Mock finding the existing connection
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Update data
        update_data = DatabaseCreate(
            name="test_db",
            url="postgresql://user:pass@localhost:5432/updated_db",
            description="Updated description"
        )

        result = await update_database(mock_db_session, "test_db", update_data)

        assert result is sample_connection
        assert result.url == "postgresql://user:pass@localhost:5432/updated_db"
        assert result.description == "Updated description"

        assert mock_db_session.commit.called
        assert mock_db_session.commit.call_count == 1
        assert mock_db_session.refresh.called
        assert mock_db_session.refresh.call_count == 1

    @pytest.mark.asyncio
    async def test_update_database_not_found(self, mock_db_session, sample_connection_data):
        """Test update of non-existent database connection.

        测试更新不存在的数据库连接：
        - 模拟尝试更新不存在的连接
        - 验证返回None值
        - 确保不会执行提交和刷新操作
        """
        # Mock not finding the connection
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await update_database(mock_db_session, "nonexistent", sample_connection_data)

        assert result is None
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_database_success(self, mock_db_session, sample_connection):
        """Test successful deletion of a database connection.

        测试成功删除数据库连接：
        - 模拟查找并删除现有连接
        - 验证返回True表示删除成功
        - 检查删除和提交操作被正确调用
        """
        # Mock finding the connection
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()

        result = await delete_database(mock_db_session, "test_db")

        assert result is True
        assert mock_db_session.delete.called
        assert mock_db_session.delete.call_count == 1
        assert mock_db_session.commit.called
        assert mock_db_session.commit.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_database_not_found(self, mock_db_session):
        """Test deletion of non-existent database connection.

        测试删除不存在的数据库连接：
        - 模拟尝试删除不存在的连接
        - 验证返回False表示删除失败
        - 确保不会执行删除和提交操作
        """
        # Mock not finding the connection
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await delete_database(mock_db_session, "nonexistent")

        assert result is False
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_crud_operations_with_db_errors(self, mock_db_session, sample_connection, sample_connection_data):
        """Test CRUD operations handle database errors gracefully.

        测试CRUD操作优雅处理数据库错误：
        - 验证创建、更新、删除操作在数据库错误时正确抛出异常
        - 检查错误传播机制正常工作
        - 确保异常信息被正确传递
        """
        # Test create with commit error
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(Exception, match="Database error"):
            await create_database(mock_db_session, sample_connection_data)

        # Test update with commit error
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(Exception, match="Database error"):
            await update_database(mock_db_session, "test_db", sample_connection_data)

        # Test delete with commit error
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(Exception, match="Database error"):
            await delete_database(mock_db_session, "test_db")
