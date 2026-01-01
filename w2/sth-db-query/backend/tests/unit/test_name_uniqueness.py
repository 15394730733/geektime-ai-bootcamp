"""
Unit tests for database connection name uniqueness validation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate


# Helper to run async functions in sync tests
def async_return(value):
    """Create a mock async function that returns a value."""
    async def _async_return(*args, **kwargs):
        return value
    return _async_return


class TestConnectionNameUniqueness:
    """Test database connection name uniqueness validation."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session.

        创建模拟的数据库会话对象：
        - 使用AsyncMock模拟异步数据库操作
        - 为名称唯一性验证测试提供基础mock对象
        """
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_connection_data(self):
        """Sample database connection data.

        提供示例数据库连接数据：
        - 包含名称、URL和描述字段
        - 用于各种名称唯一性测试场景
        """
        return DatabaseCreate(
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database"
        )

    @pytest.mark.asyncio
    async def test_unique_name_validation_success(self, mock_db_session, sample_connection_data):
        """Test that validation passes for unique connection names.

        测试唯一名称验证通过的情况：
        - 模拟数据库中不存在同名连接
        - 验证唯一性检查返回True
        - 确保新名称可以被接受
        """
        # Mock no existing connection with this name
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        is_unique = await self._is_connection_name_unique(mock_db_session, "unique_name")
        assert is_unique is True

    @pytest.mark.asyncio
    async def test_unique_name_validation_failure(self, mock_db_session, sample_connection_data):
        """Test that validation fails for duplicate connection names.

        测试重复名称验证失败的情况：
        - 模拟数据库中已存在同名连接
        - 验证唯一性检查返回False
        - 确保重复名称被正确拒绝
        """
        existing_connection = DatabaseConnection(
            id="existing-id",
            name="duplicate_name",
            url="postgresql://user:pass@localhost:5432/existing_db"
        )

        # Mock existing connection with this name
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_connection
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        is_unique = await self._is_connection_name_unique(mock_db_session, "duplicate_name")
        assert is_unique is False

    @pytest.mark.asyncio
    async def test_unique_name_validation_during_update(self, mock_db_session, sample_connection_data):
        """Test uniqueness validation during update operations.

        测试更新操作中的名称唯一性验证：
        - 验证将连接名从"conn1"更改为"conn2"时"conn2"的可用性
        - 测试目标名称已被其他连接使用时的冲突检测
        - 验证将连接名更改为相同名称（即不修改）是被允许的
        - 确保更新操作的唯一性逻辑不同于创建操作
        """
        # Scenario: updating connection "conn1" to name "conn2"
        # Should check if "conn2" is available (not used by other connections)

        # Mock: "conn2" is available
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        is_unique = await self._is_connection_name_unique_for_update(
            mock_db_session, "conn1", "conn2"
        )
        assert is_unique is True

        # Scenario: "conn2" is used by another connection
        other_connection = DatabaseConnection(
            id="other-id",
            name="conn2",
            url="postgresql://user:pass@localhost:5432/other_db"
        )

        mock_result.scalar_one_or_none.return_value = other_connection
        is_unique = await self._is_connection_name_unique_for_update(
            mock_db_session, "conn1", "conn2"
        )
        assert is_unique is False

        # Scenario: updating "conn1" to same name "conn1" should be allowed
        current_connection = DatabaseConnection(
            id="conn1-id",
            name="conn1",
            url="postgresql://user:pass@localhost:5432/conn1_db"
        )

        mock_result.scalar_one_or_none.return_value = current_connection
        is_unique = await self._is_connection_name_unique_for_update(
            mock_db_session, "conn1", "conn1"
        )
        assert is_unique is True

    @pytest.mark.asyncio
    async def test_name_uniqueness_edge_cases(self, mock_db_session):
        """Test edge cases for name uniqueness validation.

        测试名称唯一性验证的边界情况：
        - 验证空字符串和纯空格名称被拒绝
        - 测试正常名称、包含连字符、下划线、数字的名称被接受
        - 检查包含空格和特殊字符的名称被正确拒绝
        - 验证超长名称的处理
        """
        test_cases = [
            ("", False),  # Empty name
            ("   ", False),  # Whitespace only
            ("normal_name", True),  # Normal case
            ("name-with-dashes", True),  # With dashes
            ("name_with_underscores", True),  # With underscores
            ("name123", True),  # With numbers
            ("123name", True),  # Starting with numbers
            ("a", True),  # Single character
            ("a" * 100, True),  # Very long name
            ("name with spaces", False),  # Spaces (invalid)
            ("name@special", False),  # Special characters
            ("name#hash", False),  # Special characters
            ("name$dollar", False),  # Special characters
        ]

        for name, should_be_allowed in test_cases:
            if should_be_allowed:
                # Mock as unique
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_db_session.execute = AsyncMock(return_value=mock_result)

                is_unique = await self._is_connection_name_unique(mock_db_session, name)
                assert is_unique is True, f"Name '{name}' should be considered unique"
            else:
                # For invalid names, we test the name format validation instead
                is_valid = self._is_valid_connection_name(name)
                assert is_valid is False, f"Name '{name}' should be invalid"

    @pytest.mark.asyncio
    async def test_case_sensitivity_in_uniqueness(self, mock_db_session):
        """Test case sensitivity in name uniqueness validation.

        测试名称唯一性验证的大小写敏感性：
        - 验证数据库名称是大小写敏感的
        - 确认"test_db"和"Test_DB"被视为不同名称
        - 确保完全匹配的名称（包括大小写）会被拒绝
        """
        # For this test, we need to simulate different database responses
        # First test: "test_db" should be unique (different from "Test_DB")
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = None  # No match for "test_db"
        mock_db_session.execute = AsyncMock(return_value=mock_result1)

        is_unique = await self._is_connection_name_unique(mock_db_session, "test_db")
        assert is_unique is True, "Names should be case-sensitive"

        # Second test: "Test_DB" should conflict (exact match)
        existing_connection = DatabaseConnection(
            id="existing-id",
            name="Test_DB",
            url="postgresql://user:pass@localhost:5432/test_db"
        )
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = existing_connection  # Match found for "Test_DB"
        mock_db_session.execute = AsyncMock(return_value=mock_result2)

        is_unique = await self._is_connection_name_unique(mock_db_session, "Test_DB")
        assert is_unique is False, "Exact case match should conflict"

    @pytest.mark.asyncio
    async def test_concurrent_uniqueness_validation(self, mock_db_session):
        """Test uniqueness validation under concurrent operations.

        测试并发操作下的唯一性验证：
        - 模拟竞态条件场景
        - 验证第一次调用时名称可用
        - 模拟并发创建后名称被占用
        - 确保第二次调用正确检测到冲突
        """
        # This simulates a race condition scenario
        # First call - name is available
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result1)

        is_unique1 = await self._is_connection_name_unique(mock_db_session, "race_condition_name")
        assert is_unique1 is True

        # Second call - name is now taken (simulating concurrent creation)
        existing_connection = DatabaseConnection(
            id="concurrent-id",
            name="race_condition_name",
            url="postgresql://user:pass@localhost:5432/concurrent_db"
        )

        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = existing_connection
        mock_db_session.execute = AsyncMock(return_value=mock_result2)

        is_unique2 = await self._is_connection_name_unique(mock_db_session, "race_condition_name")
        assert is_unique2 is False

    @pytest.mark.asyncio
    async def test_uniqueness_validation_error_handling(self, mock_db_session):
        """Test error handling in uniqueness validation.

        测试唯一性验证中的错误处理：
        - 模拟数据库连接失败的情况
        - 验证异常被正确抛出
        - 确保错误信息被正确传播
        """
        # Mock database error
        mock_db_session.execute = AsyncMock(side_effect=Exception("Database connection failed"))

        with pytest.raises(Exception, match="Database connection failed"):
            await self._is_connection_name_unique(mock_db_session, "test_name")

    def _is_valid_connection_name(self, name: str) -> bool:
        """
        Validate connection name format.
        This is a placeholder - actual implementation will be in the validation service.
        """
        if not name or not isinstance(name, str):
            return False

        name = name.strip()
        if not name:
            return False

        # Name should not contain spaces or special characters
        import re
        if re.search(r'[^\w\-]', name):
            return False

        # Name should not be too long
        if len(name) > 100:
            return False

        return True

    async def _is_connection_name_unique(self, db: AsyncSession, name: str) -> bool:
        """
        Check if connection name is unique.
        This is a placeholder - actual implementation will be in the validation service.
        """
        from sqlalchemy import select

        result = await db.execute(
            select(DatabaseConnection).where(DatabaseConnection.name == name)
        )
        existing = result.scalar_one_or_none()
        return existing is None

    async def _is_connection_name_unique_for_update(self, db: AsyncSession, current_name: str, new_name: str) -> bool:
        """
        Check if new name is unique for update operations.
        This is a placeholder - actual implementation will be in the validation service.
        """
        if current_name == new_name:
            return True  # Same name is allowed

        return await self._is_connection_name_unique(db, new_name)
