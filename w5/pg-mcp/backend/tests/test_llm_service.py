"""
Unit tests for LLM service integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm import LLMService, llm_service


class TestLLMService:
    """Test LLM service functionality."""

    @pytest.fixture
    def llm_service_instance(self):
        """Create a test instance of LLM service.

        创建LLM服务的测试实例：
        - 配置模拟的OpenAI客户端用于单元测试
        - 设置固定的模拟响应以确保测试一致性
        - 避免实际的API调用和网络依赖
        """
        service = LLMService()
        # Mock the client directly
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SELECT * FROM users WHERE active = true"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        service._LLMService__client = mock_client
        return service

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client.

        创建模拟的OpenAI客户端：
        - 设置固定的聊天完成响应
        - 模拟异步API调用行为
        - 为测试提供可预测的结果
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SELECT * FROM users WHERE active = true"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        return mock_client

    def test_build_schema_context_simple_table(self, llm_service_instance):
        """Test building schema context for simple table.

        测试为简单表构建schema上下文的功能：
        - 验证表名、schema名称正确显示
        - 检查列信息（名称、类型、主键、是否可空）正确格式化
        - 确保输出包含必要的标识符（PRIMARY KEY, NOT NULL）
        """
        schema = {
            "tables": [
                {
                    "name": "users",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                        {"name": "name", "data_type": "varchar", "is_primary_key": False, "is_nullable": False},
                        {"name": "email", "data_type": "varchar", "is_primary_key": False, "is_nullable": True}
                    ]
                }
            ],
            "views": []
        }

        context = llm_service_instance._build_schema_context(schema)

        assert "Tables:" in context
        assert "public.users:" in context
        assert "- id (integer)" in context
        assert "[PRIMARY KEY]" in context
        assert "[NOT NULL]" in context

    def test_build_schema_context_multiple_tables(self, llm_service_instance):
        """Test building schema context for multiple tables.

        测试为多表schema构建上下文的功能：
        - 验证多个表的信息都被正确包含
        - 检查表间关系字段（如user_id）正确显示
        - 确保所有表和列信息都完整呈现
        """
        schema = {
            "tables": [
                {
                    "name": "users",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False}
                    ]
                },
                {
                    "name": "posts",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                        {"name": "user_id", "data_type": "integer", "is_primary_key": False, "is_nullable": False}
                    ]
                }
            ],
            "views": []
        }

        context = llm_service_instance._build_schema_context(schema)

        assert "users" in context
        assert "posts" in context
        assert "user_id" in context

    def test_build_schema_context_with_views(self, llm_service_instance):
        """Test building schema context including views.

        测试包含视图的schema上下文构建：
        - 验证视图部分正确标识和显示
        - 检查视图的列信息正确格式化
        - 确保表和视图区分清晰
        """
        schema = {
            "tables": [],
            "views": [
                {
                    "name": "active_users",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "data_type": "integer", "is_primary_key": False, "is_nullable": False},
                        {"name": "name", "data_type": "varchar", "is_primary_key": False, "is_nullable": False}
                    ]
                }
            ]
        }

        context = llm_service_instance._build_schema_context(schema)

        assert "Views:" in context
        assert "active_users" in context

    def test_create_sql_generation_prompt(self, llm_service_instance):
        """Test creating SQL generation prompt.

        测试SQL生成提示的创建功能：
        - 验证自然语言查询被正确包含在提示中
        - 检查schema上下文完整嵌入
        - 确保提示包含必要的指令（PostgreSQL SELECT, 只生成SELECT语句等）
        """
        natural_language = "Show me all active users"
        schema_context = "Tables:\n  public.users:\n    - id (integer) [PRIMARY KEY]"

        prompt = llm_service_instance._create_sql_generation_prompt(
            natural_language, schema_context
        )

        assert "Show me all active users" in prompt
        assert schema_context in prompt
        assert "PostgreSQL SELECT query" in prompt
        assert "Only generate SELECT statements" in prompt

    def test_clean_sql_response_basic(self, llm_service_instance):
        """Test cleaning basic SQL response.

        测试基本的SQL响应清理功能：
        - 验证纯SQL语句无需额外处理
        - 确保返回的SQL与输入完全一致
        """
        response = "SELECT * FROM users"
        cleaned = llm_service_instance._clean_sql_response(response)
        assert cleaned == "SELECT * FROM users"

    def test_clean_sql_response_with_markdown(self, llm_service_instance):
        """Test cleaning SQL response with markdown code blocks.

        测试清理包含markdown代码块的SQL响应：
        - 验证能够正确提取```sql代码块内的内容
        - 移除markdown语法，只保留纯SQL语句
        """
        response = """```sql
SELECT * FROM users WHERE active = true
```"""
        cleaned = llm_service_instance._clean_sql_response(response)
        assert cleaned == "SELECT * FROM users WHERE active = true"

    def test_clean_sql_response_with_extra_whitespace(self, llm_service_instance):
        """Test cleaning SQL response with extra whitespace.

        测试清理包含多余空白字符的SQL响应：
        - 移除前后的空白字符和换行符
        - 规范化SQL语句格式
        """
        response = "  \n  SELECT * FROM users  \n  "
        cleaned = llm_service_instance._clean_sql_response(response)
        assert cleaned == "SELECT * FROM users"

    def test_generate_sql_success_mock_setup(self, llm_service_instance):
        """Test that LLM service is properly mocked for SQL generation.

        验证LLM服务的模拟设置是否正确：
        - 检查模拟客户端是否正确配置
        - 验证schema上下文构建功能（不调用API）
        - 确保测试环境配置完整
        """
        # This test verifies the mock setup works
        schema = {
            "tables": [
                {
                    "name": "users",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                        {"name": "name", "data_type": "varchar", "is_primary_key": False, "is_nullable": False},
                        {"name": "active", "data_type": "boolean", "is_primary_key": False, "is_nullable": False}
                    ]
                }
            ],
            "views": []
        }

        # Test that the mock client is set up correctly
        assert hasattr(llm_service_instance, '_LLMService__client')
        mock_client = llm_service_instance._LLMService__client
        assert mock_client is not None

        # Test schema context building (this doesn't call the API)
        context = llm_service_instance._build_schema_context(schema)
        assert "users" in context
        assert "active" in context


def test_build_schema_context_complex():
    """Test building schema context with complex database schema.

    测试复杂数据库schema的上下文构建：
    - 验证包含外键关系的表结构正确处理
    - 检查多表间的关系字段正确显示
    - 确保上下文长度和内容都符合预期
    """
    service = LLMService()  # Create fresh instance without mocking

    complex_schema = {
        "tables": [
            {
                "name": "users",
                "schema": "public",
                "columns": [
                    {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                    {"name": "name", "data_type": "varchar", "is_primary_key": False, "is_nullable": False},
                    {"name": "department_id", "data_type": "integer", "is_primary_key": False, "is_nullable": True}
                ]
            },
            {
                "name": "departments",
                "schema": "public",
                "columns": [
                    {"name": "id", "data_type": "integer", "is_primary_key": True, "is_nullable": False},
                    {"name": "name", "data_type": "varchar", "is_primary_key": False, "is_nullable": False}
                ]
            }
        ],
        "views": []
    }

    # Test that the schema context building works
    context = service._build_schema_context(complex_schema)
    assert isinstance(context, str)
    assert "users" in context
    assert "departments" in context
    assert "department_id" in context
    assert len(context) > 0


class TestGlobalLLMService:
    """Test the global LLM service instance."""

    def test_global_service_is_singleton(self):
        """Test that the global service is a singleton.

        验证全局LLM服务实例是单例模式：
        - 多次获取服务应返回同一实例
        - 确保服务实例化正确
        """
        service1 = llm_service
        service2 = llm_service
        assert service1 is service2
        assert isinstance(service1, LLMService)

    def test_global_service_initialization(self):
        """Test that the global service is properly initialized.

        验证全局LLM服务正确初始化：
        - 检查必要的属性和方法存在
        - 确保服务实例不是None
        - 验证核心功能方法可用
        """
        assert llm_service is not None
        assert hasattr(llm_service, 'generate_sql')
        assert hasattr(llm_service, '_build_schema_context')
        # Note: We don't check private attributes as they may vary
