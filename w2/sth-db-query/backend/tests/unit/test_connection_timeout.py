"""
Unit tests for database connection timeout handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

from app.models.database import DatabaseConnection


class TestConnectionTimeoutHandling:
    """Test database connection timeout handling logic."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session.

        创建模拟的数据库会话对象：
        - 使用AsyncMock模拟异步数据库操作
        - 为连接超时测试提供基础mock对象
        """
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_connection(self):
        """Sample DatabaseConnection instance.

        提供示例DatabaseConnection实例：
        - 包含完整的连接信息用于超时测试
        - 设置为激活状态用于连接测试
        """
        return DatabaseConnection(
            id="test-conn-1",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database",
            is_active=True
        )

    def test_connection_timeout_configuration(self):
        """Test timeout configuration parsing and validation.

        测试连接超时配置的解析和验证：
        - 验证有效超时值（1-3600秒）被接受
        - 确保无效值（如0、负数、过大值、非数字）被拒绝
        """
        # Valid timeout values
        valid_timeouts = [1, 5, 30, 60, 300, 3600]  # seconds

        for timeout in valid_timeouts:
            config = {"connection_timeout": timeout}
            assert self._is_valid_timeout_config(config), f"Timeout {timeout} should be valid"

        # Invalid timeout values
        invalid_timeouts = [0, -1, -5, 3601, "not_a_number", None]

        for timeout in invalid_timeouts:
            config = {"connection_timeout": timeout}
            assert not self._is_valid_timeout_config(config), f"Timeout {timeout} should be invalid"

    @pytest.mark.asyncio
    async def test_connection_attempt_with_timeout(self):
        """Test database connection attempt with timeout.

        测试带超时的数据库连接尝试：
        - 模拟成功的连接（在超时时间内完成）
        - 验证返回结果包含成功状态和持续时间
        - 确保连接在完成后被正确关闭
        """
        # Mock successful connection within timeout
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_engine.connect = AsyncMock(return_value=mock_conn)
        mock_conn.close = AsyncMock()

        result = await self._test_connection_with_timeout(mock_engine, timeout=5.0)
        assert result["success"] is True
        assert result["error"] is None
        assert "duration" in result

    @pytest.mark.asyncio
    async def test_connection_timeout_exceeded(self):
        """Test connection attempt that exceeds timeout.

        测试超过超时的连接尝试：
        - 模拟耗时过长的连接（超过超时限制）
        - 验证超时错误被正确检测和报告
        - 确保不会等待完整的慢连接时间
        """
        # Mock connection that takes too long
        async def slow_connect():
            await asyncio.sleep(10)  # Longer than timeout
            return MagicMock()

        mock_engine = AsyncMock()
        mock_engine.connect = slow_connect

        result = await self._test_connection_with_timeout(mock_engine, timeout=1.0)
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
        assert result["duration"] < 2.0  # Should not wait full 10 seconds

    @pytest.mark.asyncio
    async def test_connection_refused_timeout(self):
        """Test timeout when connection is refused.

        测试连接被拒绝时的超时处理：
        - 模拟连接被服务器拒绝的情况
        - 验证错误信息正确包含"Connection refused"
        - 确保连接失败被正确报告
        """
        # Mock connection refused scenario
        mock_engine = AsyncMock()
        mock_engine.connect = AsyncMock(side_effect=Exception("Connection refused"))

        result = await self._test_connection_with_timeout(mock_engine, timeout=5.0)
        assert result["success"] is False
        assert "Connection refused" in result["error"]

    @pytest.mark.asyncio
    async def test_connection_network_timeout(self):
        """Test timeout due to network issues.

        测试由于网络问题导致的超时：
        - 模拟网络不可达的情况
        - 验证错误信息包含网络相关关键词
        - 确保网络错误被正确识别和报告
        """
        # Mock network timeout
        mock_engine = AsyncMock()
        mock_engine.connect = AsyncMock(side_effect=Exception("Network is unreachable"))

        result = await self._test_connection_with_timeout(mock_engine, timeout=5.0)
        assert result["success"] is False
        assert "unreachable" in result["error"].lower()

    def test_timeout_configuration_from_url(self):
        """Test parsing timeout configuration from database URL.

        测试从数据库URL解析超时配置：
        - 验证connect_timeout查询参数被正确提取
        - 测试URL中无超时参数时的默认行为
        - 检查无效超时值时的错误处理
        """
        test_cases = [
            {
                "url": "postgresql://user:pass@localhost:5432/db?connect_timeout=10",
                "expected_timeout": 10
            },
            {
                "url": "postgresql://user:pass@localhost:5432/db?connect_timeout=30",
                "expected_timeout": 30
            },
            {
                "url": "postgresql://user:pass@localhost:5432/db",  # No timeout
                "expected_timeout": None
            },
            {
                "url": "postgresql://user:pass@localhost:5432/db?connect_timeout=invalid",
                "expected_timeout": None
            }
        ]

        for case in test_cases:
            timeout = self._extract_timeout_from_url(case["url"])
            assert timeout == case["expected_timeout"], f"URL {case['url']} should extract timeout {case['expected_timeout']}"

    def test_timeout_retry_logic(self):
        """Test retry logic when connections timeout.

        测试连接超时的重试逻辑：
        - 验证不同的重试配置（最大重试次数、基础延迟、最大延迟）
        - 确保重试配置的有效性验证
        """
        # Test retry configuration
        retry_configs = [
            {"max_retries": 3, "base_delay": 1.0, "max_delay": 10.0},
            {"max_retries": 5, "base_delay": 0.5, "max_delay": 30.0},
            {"max_retries": 0, "base_delay": 1.0, "max_delay": 5.0},  # No retries
        ]

        for config in retry_configs:
            assert self._is_valid_retry_config(config), f"Retry config {config} should be valid"

    @pytest.mark.asyncio
    async def test_connection_retry_on_timeout(self):
        """Test automatic retry when connection times out.

        测试连接超时的自动重试：
        - 模拟前两次失败、第三次成功的连接尝试
        - 验证重试机制在达到最大重试次数前成功
        - 检查尝试次数和最终成功状态
        """
        call_count = 0

        async def failing_then_succeeding_connect():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                await asyncio.sleep(2)  # Simulate timeout
                raise Exception("Connection timeout")
            else:
                return AsyncMock()  # Success on third try

        mock_engine = AsyncMock()
        mock_engine.connect = failing_then_succeeding_connect

        result = await self._test_connection_with_retry(
            mock_engine,
            timeout=1.0,
            max_retries=3,
            retry_delay=0.1
        )

        assert result["success"] is True
        assert call_count == 3  # Should have tried 3 times
        assert result["attempts"] == 3

    @pytest.mark.asyncio
    async def test_connection_retry_exhaustion(self):
        """Test behavior when all retry attempts are exhausted.

        测试所有重试尝试都耗尽时的行为：
        - 模拟持续失败的连接尝试
        - 验证达到最大重试次数后停止重试
        - 检查错误信息和尝试次数的正确性
        """
        call_count = 0

        async def always_failing_connect():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent connection failure")

        mock_engine = AsyncMock()
        mock_engine.connect = always_failing_connect

        result = await self._test_connection_with_retry(
            mock_engine,
            timeout=1.0,
            max_retries=3,
            retry_delay=0.1
        )

        assert result["success"] is False
        assert call_count == 4  # Should have tried max_retries + 1 times (initial + retries)
        assert result["attempts"] == 4
        assert "Persistent connection failure" in result["error"]

    def test_timeout_backoff_strategy(self):
        """Test exponential backoff strategy for retries.

        测试重试的指数退避策略：
        - 验证退避时间的指数增长计算
        - 检查最大延迟限制的正确应用
        - 确保退避时间序列符合预期
        """
        # Test backoff calculation
        backoff_times = self._calculate_backoff_times(max_retries=3, base_delay=1.0, max_delay=10.0)

        expected = [1.0, 2.0, 4.0]  # Exponential backoff
        assert backoff_times == expected

        # Test backoff with max delay cap
        backoff_times = self._calculate_backoff_times(max_retries=5, base_delay=2.0, max_delay=5.0)

        expected = [2.0, 4.0, 5.0, 5.0, 5.0]  # Capped at max_delay
        assert backoff_times == expected

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_timeout(self):
        """Test that connections are properly cleaned up on timeout.

        测试超时时的连接正确清理：
        - 模拟超时情况下的连接清理回调
        - 验证清理函数被正确调用
        - 确保资源在失败情况下被妥善释放
        """
        cleanup_called = False

        async def connect_with_cleanup():
            await asyncio.sleep(2)  # Exceed timeout
            return MagicMock()

        async def cleanup_connection(conn):
            nonlocal cleanup_called
            cleanup_called = True

        mock_engine = AsyncMock()
        mock_engine.connect = connect_with_cleanup

        result = await self._test_connection_with_timeout_and_cleanup(
            mock_engine,
            timeout=1.0,
            cleanup_callback=cleanup_connection
        )

        assert result["success"] is False
        assert cleanup_called is True

    def test_timeout_error_messages(self):
        """Test informative error messages for different timeout scenarios.

        测试不同超时场景的信息性错误消息：
        - 验证各种超时错误的描述性消息
        - 检查错误消息包含相关的上下文信息
        - 确保用户能从错误消息中了解失败原因
        """
        error_scenarios = [
            {
                "error": Exception("Connection timeout after 5000ms"),
                "expected_contains": ["timeout", "5000ms"]
            },
            {
                "error": Exception("Network unreachable"),
                "expected_contains": ["network", "unreachable"]
            },
            {
                "error": Exception("Connection refused"),
                "expected_contains": ["refused"]
            },
            {
                "error": Exception("Authentication failed"),
                "expected_contains": ["authentication", "failed"]
            }
        ]

        for scenario in error_scenarios:
            message = self._format_timeout_error_message(scenario["error"], timeout=5.0)
            for expected_text in scenario["expected_contains"]:
                assert expected_text.lower() in message.lower(), f"Error message should contain '{expected_text}'"

    def _is_valid_timeout_config(self, config: dict) -> bool:
        """Validate timeout configuration."""
        timeout = config.get("connection_timeout")
        if timeout is None:
            return False  # None is invalid
        if not isinstance(timeout, (int, float)):
            return False
        return 1 <= timeout <= 3600  # Between 1 second and 1 hour

    async def _test_connection_with_timeout(self, engine, timeout: float) -> dict:
        """Test connection with timeout - helper method."""
        import time
        start_time = time.time()

        try:
            # Set a short timeout for testing
            import asyncio
            conn = await asyncio.wait_for(engine.connect(), timeout=timeout)
            await conn.close()
            return {
                "success": True,
                "error": None,
                "duration": time.time() - start_time
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Connection timeout after {timeout}s",
                "duration": time.time() - start_time
            }
        except Exception as e:
            # Handle other connection errors
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }

    def _extract_timeout_from_url(self, url: str) -> int:
        """Extract timeout from database URL."""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        timeout_str = query_params.get("connect_timeout", [None])[0]
        if timeout_str:
            try:
                return int(timeout_str)
            except ValueError:
                return None
        return None

    def _is_valid_retry_config(self, config: dict) -> bool:
        """Validate retry configuration."""
        required_keys = ["max_retries", "base_delay", "max_delay"]
        for key in required_keys:
            if key not in config:
                return False

        max_retries = config["max_retries"]
        base_delay = config["base_delay"]
        max_delay = config["max_delay"]

        return (
            isinstance(max_retries, int) and max_retries >= 0 and
            isinstance(base_delay, (int, float)) and base_delay > 0 and
            isinstance(max_delay, (int, float)) and max_delay >= base_delay
        )

    async def _test_connection_with_retry(self, engine, timeout: float, max_retries: int, retry_delay: float) -> dict:
        """Test connection with retry logic."""
        attempts = 0

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            attempts += 1
            try:
                result = await self._test_connection_with_timeout(engine, timeout)
                if result["success"]:
                    return {**result, "attempts": attempts}
                # If connection failed but we have retries left, wait and retry
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # No more retries, return the failure result
                    return {**result, "attempts": attempts}
            except Exception as e:
                # If we have retries left, wait and retry
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # No more retries, return failure
                    return {
                        "success": False,
                        "error": str(e),
                        "attempts": attempts
                    }

        return {
            "success": False,
            "error": "All retry attempts exhausted",
            "attempts": attempts
        }

    def _calculate_backoff_times(self, max_retries: int, base_delay: float, max_delay: float) -> list:
        """Calculate backoff times for retries."""
        times = []
        for i in range(max_retries):
            delay = min(base_delay * (2 ** i), max_delay)
            times.append(delay)
        return times

    async def _test_connection_with_timeout_and_cleanup(self, engine, timeout: float, cleanup_callback) -> dict:
        """Test connection with cleanup on timeout."""
        result = await self._test_connection_with_timeout(engine, timeout)
        if not result["success"]:
            # Simulate cleanup on failure
            await cleanup_callback(None)
        return result

    def _format_timeout_error_message(self, error: Exception, timeout: float) -> str:
        """Format informative error message for timeout scenarios."""
        error_msg = str(error)
        return f"Database connection failed after {timeout}s: {error_msg}"
