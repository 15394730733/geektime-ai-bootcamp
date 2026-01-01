"""
Pytest configuration and fixtures for the Database Query Tool.
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session.

    为测试会话创建异步事件循环实例：
    - 使用pytest-asyncio插件需要的会话级fixture
    - 创建新的事件循环实例用于异步测试
    - 在测试结束后正确关闭循环
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_url():
    """SQLite test database URL.

    提供用于测试的SQLite内存数据库URL：
    - 使用内存数据库避免文件系统依赖
    - 每次测试会话都是独立的数据库实例
    - 不需要持久化测试数据
    """
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Create test database engine.

    创建测试数据库引擎：
    - 使用SQLite内存数据库配置
    - 设置check_same_thread=False以支持多线程访问
    - 使用StaticPool避免连接池问题
    """
    return create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    """Create test session factory.

    创建测试数据库会话工厂：
    - 配置为autocommit=False和autoflush=False
    - 绑定到测试数据库引擎
    - 为每个测试提供独立的数据库会话
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session(TestingSessionLocal, engine) -> Generator[Session, None, None]:
    """Create test database session.

    创建函数级测试数据库会话：
    - 每个测试函数使用独立的数据库连接
    - 使用事务确保测试隔离性
    - 测试结束后自动回滚和清理连接
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create test client for FastAPI app.

    创建FastAPI应用程序的测试客户端：
    - 提供与HTTP请求相同的测试接口
    - 每个测试函数使用独立的客户端实例
    - 自动处理应用程序的启动和清理
    """
    # For now, skip database setup to avoid connection issues
    # TODO: Fix database connection for full API testing
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sample_database_data():
    """Sample database connection data for tests.

    提供测试用的示例数据库连接数据：
    - 包含数据库名称、URL和描述
    - 使用标准的PostgreSQL连接格式
    - 为数据库CRUD测试提供一致的测试数据
    """
    return {
        "name": "test_db",
        "url": "postgresql://user:pass@localhost:5432/test_db",
        "description": "Test database for unit tests"
    }


@pytest.fixture(scope="function")
def sample_query_data():
    """Sample query data for tests.

    提供测试用的示例查询数据：
    - 包含基本的SQL SELECT语句
    - 用于测试查询执行功能
    """
    return {
        "sql": "SELECT * FROM users LIMIT 10"
    }


@pytest.fixture(scope="function")
def sample_natural_language_query():
    """Sample natural language query for tests.

    提供测试用的示例自然语言查询数据：
    - 包含用户友好的查询提示
    - 用于测试LLM SQL生成功能
    """
    return {
        "prompt": "Show me all users in the system"
    }
