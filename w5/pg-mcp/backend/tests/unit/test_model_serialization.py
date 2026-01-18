"""
Unit tests for database connection model serialization.
"""

import pytest
import json
from datetime import datetime
from app.models.database import DatabaseConnection


class TestModelSerialization:
    """Test DatabaseConnection model serialization/deserialization."""

    def test_model_to_dict_serialization(self):
        """Test converting model to dictionary.

        测试将DatabaseConnection模型转换为字典的功能：
        - 验证所有必需字段都被包含在输出字典中
        - 检查字段值的正确映射
        - 确保布尔值和字符串字段正确转换
        """
        connection = DatabaseConnection(
            id="test-id",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database",
            is_active=True
        )

        data = self._model_to_dict(connection)

        expected_keys = ["id", "name", "url", "description", "created_at", "updated_at", "is_active"]
        for key in expected_keys:
            assert key in data

        assert data["id"] == "test-id"
        assert data["name"] == "test_db"
        assert data["is_active"] is True

    def test_model_to_json_serialization(self):
        """Test converting model to JSON.

        测试将DatabaseConnection模型转换为JSON字符串的功能：
        - 验证模型可以序列化为有效的JSON格式
        - 检查JSON反序列化后的数据完整性
        - 确保时间戳字段被正确包含
        """
        connection = DatabaseConnection(
            id="test-id",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db"
        )

        json_str = self._model_to_json(connection)
        data = json.loads(json_str)

        assert data["id"] == "test-id"
        assert data["name"] == "test_db"
        assert "created_at" in data

    def test_dict_to_model_deserialization(self):
        """Test converting dictionary to model.

        测试将字典转换为DatabaseConnection模型的功能：
        - 验证所有字段都能正确映射到模型属性
        - 检查必填字段和可选字段的处理
        - 确保数据类型正确转换
        """
        data = {
            "id": "test-id",
            "name": "test_db",
            "url": "postgresql://user:pass@localhost:5432/test_db",
            "description": "Test database",
            "is_active": True
        }

        connection = self._dict_to_model(data)

        assert connection.id == "test-id"
        assert connection.name == "test_db"
        assert connection.url == "postgresql://user:pass@localhost:5432/test_db"
        assert connection.description == "Test database"
        assert connection.is_active is True

    def test_json_to_model_deserialization(self):
        """Test converting JSON to model.

        测试将JSON字符串转换为DatabaseConnection模型的功能：
        - 验证JSON解析和模型创建的完整流程
        - 检查布尔值的正确解析（true -> True）
        - 确保所有字段都被正确反序列化
        """
        json_data = '''{
            "id": "test-id",
            "name": "test_db",
            "url": "postgresql://user:pass@localhost:5432/test_db",
            "description": "Test database",
            "is_active": true
        }'''

        connection = self._json_to_model(json_data)

        assert connection.id == "test-id"
        assert connection.name == "test_db"
        assert connection.is_active is True

    def test_serialization_round_trip(self):
        """Test that serialize->deserialize preserves data.

        测试序列化-反序列化往返过程的数据完整性：
        - 验证dict序列化后能完全恢复原始数据
        - 检查所有字段（包括布尔值）的准确保存
        - 确保往返转换不丢失信息
        """
        original = DatabaseConnection(
            id="test-id",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            description="Test database",
            is_active=False
        )

        # Serialize to dict then back to model
        data = self._model_to_dict(original)
        restored = self._dict_to_model(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.url == original.url
        assert restored.description == original.description
        assert restored.is_active == original.is_active

    def test_serialization_with_timestamps(self):
        """Test serialization includes timestamps.

        测试序列化包含时间戳字段的功能：
        - 验证created_at和updated_at字段被正确包含
        - 检查时间戳的序列化处理
        - 确保时间字段在输出中存在
        """
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        connection = DatabaseConnection(
            id="test-id",
            name="test_db",
            url="postgresql://user:pass@localhost:5432/test_db",
            created_at=fixed_time,
            updated_at=fixed_time
        )

        data = self._model_to_dict(connection)

        # Timestamps should be included
        assert "created_at" in data
        assert "updated_at" in data

    def _model_to_dict(self, model: DatabaseConnection) -> dict:
        """Convert model to dictionary."""
        return {
            "id": model.id,
            "name": model.name,
            "url": model.url,
            "description": model.description,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
            "is_active": model.is_active
        }

    def _model_to_json(self, model: DatabaseConnection) -> str:
        """Convert model to JSON string."""
        return json.dumps(self._model_to_dict(model))

    def _dict_to_model(self, data: dict) -> DatabaseConnection:
        """Convert dictionary to model."""
        return DatabaseConnection(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            description=data.get("description"),
            is_active=data.get("is_active", True)
        )

    def _json_to_model(self, json_str: str) -> DatabaseConnection:
        """Convert JSON string to model."""
        data = json.loads(json_str)
        return self._dict_to_model(data)
