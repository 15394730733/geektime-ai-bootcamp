"""
Unit tests for response utilities and error handling.
"""

import pytest
from app.utils.response import (
    APIResponse,
    ValidationErrorResponse,
    ErrorDetail,
    get_http_status_code
)


class TestAPIResponse:
    """Test API response utilities."""

    def test_success_response_creation(self):
        """Test creating a successful response.

        测试创建成功的API响应：
        - 验证success字段为True
        - 检查消息和数据字段正确设置
        - 确保error字段为None
        """
        response = APIResponse.success_response("Operation successful", {"id": 1})

        assert response.success is True
        assert response.message == "Operation successful"
        assert response.data == {"id": 1}
        assert response.error is None

    def test_success_response_default_message(self):
        """Test success response with default message.

        测试成功响应使用默认消息：
        - 验证未提供消息时使用"Success"作为默认值
        - 确保数据字段正确设置
        """
        response = APIResponse.success_response(data={"result": "ok"})

        assert response.success is True
        assert response.message == "Success"
        assert response.data == {"result": "ok"}

    def test_error_response_creation(self):
        """Test creating an error response.

        测试创建错误API响应：
        - 验证success字段为False
        - 检查错误代码和详细信息正确设置
        - 确保data字段为None
        """
        response = APIResponse.error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            {"field": "name", "issue": "required"}
        )

        assert response.success is False
        assert response.message == "Validation failed"
        assert response.data is None
        assert response.error["code"] == "VALIDATION_ERROR"
        assert response.error["details"] == {"field": "name", "issue": "required"}

    def test_error_response_minimal(self):
        """Test error response with minimal parameters.

        测试使用最小参数创建错误响应：
        - 验证只提供消息时的默认错误代码
        - 检查错误详细信息为None
        """
        response = APIResponse.error_response("Something went wrong")

        assert response.success is False
        assert response.message == "Something went wrong"
        assert response.error["code"] == "INTERNAL_ERROR"
        assert response.error["details"] is None


class TestValidationErrorResponse:
    """Test validation error response handling."""

    def test_validation_error_response_creation(self):
        """Test creating validation error response.

        测试创建验证错误响应：
        - 验证包含多个错误详情的响应结构
        - 检查每个错误的字段、消息和代码
        """
        errors = [
            ErrorDetail(field="name", message="Field required", code="missing"),
            ErrorDetail(field="email", message="Invalid format", code="invalid")
        ]

        response = ValidationErrorResponse(errors=errors)

        assert response.success is False
        assert response.message == "Validation failed"
        assert len(response.errors) == 2
        assert response.errors[0].field == "name"
        assert response.errors[0].message == "Field required"
        assert response.errors[0].code == "missing"

    def test_from_validation_errors_simple(self):
        """Test creating validation error response from Pydantic errors.

        测试从Pydantic错误创建验证错误响应：
        - 验证单个字段的错误转换
        - 检查错误消息和代码正确映射
        """
        pydantic_errors = {
            "name": [{"msg": "Field required", "type": "missing"}],
            "email": [{"msg": "Invalid email format", "type": "value_error"}]
        }

        response = ValidationErrorResponse.from_validation_errors(pydantic_errors)

        assert response.success is False
        assert len(response.errors) == 2

        # Check name error
        name_error = next(e for e in response.errors if e.field == "name")
        assert name_error.message == "Field required"
        assert name_error.code == "missing"

        # Check email error
        email_error = next(e for e in response.errors if e.field == "email")
        assert email_error.message == "Invalid email format"
        assert email_error.code == "value_error"

    def test_from_validation_errors_multiple_per_field(self):
        """Test handling multiple errors per field.

        测试处理单个字段的多个错误：
        - 验证多个错误详情都被正确处理
        - 检查错误列表包含所有错误信息
        """
        pydantic_errors = {
            "email": [
                {"msg": "Invalid format", "type": "value_error"},
                {"msg": "Too long", "type": "too_long"}
            ]
        }

        response = ValidationErrorResponse.from_validation_errors(pydantic_errors)

        assert len(response.errors) == 2
        email_errors = [e for e in response.errors if e.field == "email"]
        assert len(email_errors) == 2
        assert {e.message for e in email_errors} == {"Invalid format", "Too long"}

    def test_from_validation_errors_empty(self):
        """Test handling empty validation errors.

        测试处理空的验证错误：
        - 验证空错误字典的处理逻辑
        - 检查错误列表为空
        """
        response = ValidationErrorResponse.from_validation_errors({})

        assert response.success is False
        assert len(response.errors) == 0


class TestErrorDetail:
    """Test ErrorDetail model."""

    def test_error_detail_creation_complete(self):
        """Test creating complete error detail.

        测试创建完整的错误详情对象：
        - 验证所有字段（field, message, code）都正确设置
        - 检查字段值的准确性
        """
        error = ErrorDetail(
            field="username",
            message="Must be at least 3 characters",
            code="too_short"
        )

        assert error.field == "username"
        assert error.message == "Must be at least 3 characters"
        assert error.code == "too_short"

    def test_error_detail_creation_minimal(self):
        """Test creating minimal error detail.

        测试创建最小化的错误详情对象：
        - 验证只提供必需字段时的行为
        - 检查可选字段的默认值
        """
        error = ErrorDetail(field="password", message="Required field")

        assert error.field == "password"
        assert error.message == "Required field"
        assert error.code is None


class TestHTTPStatusCodes:
    """Test HTTP status code mapping."""

    def test_get_http_status_code_known_errors(self):
        """Test mapping known error codes to HTTP status.

        测试已知错误代码到HTTP状态码的映射：
        - 验证各种错误类型的正确映射
        - 检查常见的HTTP状态码（400, 404, 409, 500, 503等）
        """
        assert get_http_status_code("VALIDATION_ERROR") == 400
        assert get_http_status_code("NOT_FOUND") == 404
        assert get_http_status_code("CONFLICT") == 409
        assert get_http_status_code("INTERNAL_ERROR") == 500
        assert get_http_status_code("SERVICE_UNAVAILABLE") == 503
        assert get_http_status_code("BAD_REQUEST") == 400
        assert get_http_status_code("UNAUTHORIZED") == 401
        assert get_http_status_code("FORBIDDEN") == 403

    def test_get_http_status_code_unknown_error(self):
        """Test unknown error code defaults to 500.

        测试未知错误代码的默认处理：
        - 验证未定义的错误代码返回500状态码
        - 检查空字符串的处理
        """
        assert get_http_status_code("UNKNOWN_ERROR") == 500
        assert get_http_status_code("RANDOM_CODE") == 500
        assert get_http_status_code("") == 500

    def test_get_http_status_code_case_sensitive(self):
        """Test error code matching is case sensitive.

        测试错误代码匹配是否大小写敏感：
        - 验证大小写不匹配时返回默认值500
        - 检查正确的大小写匹配
        """
        # The current implementation is case sensitive
        assert get_http_status_code("VALIDATION_ERROR") == 400
        assert get_http_status_code("validation_error") == 500  # Unknown code defaults to 500
        assert get_http_status_code("Validation_Error") == 500  # Unknown code defaults to 500


class TestResponseIntegration:
    """Test response utilities integration."""

    def test_api_response_serialization(self):
        """Test API response can be serialized to JSON.

        测试API响应对象的JSON序列化：
        - 验证响应可以转换为字典格式
        - 检查所有字段正确序列化
        """
        response = APIResponse.success_response("Test", {"key": "value"})

        # This should not raise an exception
        data = response.model_dump()
        assert data["success"] is True
        assert data["message"] == "Test"
        assert data["data"] == {"key": "value"}
        assert data["error"] is None

    def test_validation_error_response_serialization(self):
        """Test validation error response serialization.

        测试验证错误响应的序列化：
        - 验证复杂错误结构正确转换为字典
        - 检查错误详情数组的序列化
        """
        response = ValidationErrorResponse.from_validation_errors({
            "field1": [{"msg": "Error 1", "type": "error_type"}]
        })

        data = response.model_dump()
        assert data["success"] is False
        assert data["message"] == "Validation failed"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "field1"
        assert data["errors"][0]["message"] == "Error 1"

    def test_error_response_with_status_code(self):
        """Test error response with appropriate HTTP status code.

        测试错误响应与HTTP状态码的关联：
        - 验证错误响应可以正确映射到HTTP状态码
        - 检查NOT_FOUND错误返回404状态码
        """
        error_response = APIResponse.error_response("Not found", "NOT_FOUND")
        status_code = get_http_status_code(error_response.error["code"])

        assert status_code == 404
        assert error_response.success is False
        assert error_response.error["code"] == "NOT_FOUND"

    def test_complete_error_flow(self):
        """Test complete error handling flow.

        测试完整的错误处理流程：
        - 从Pydantic验证错误到最终响应
        - 验证错误转换、序列化等完整流程
        - 检查所有错误字段都被正确处理
        """
        # Simulate validation error from Pydantic
        pydantic_errors = {
            "username": [{"msg": "Required field", "type": "missing"}],
            "password": [{"msg": "Too short", "type": "too_short"}]
        }

        # Create validation error response
        validation_response = ValidationErrorResponse.from_validation_errors(pydantic_errors)

        # Verify structure
        assert validation_response.success is False
        assert len(validation_response.errors) == 2

        # Check that each field has an error
        fields = {error.field for error in validation_response.errors}
        assert fields == {"username", "password"}

        # Verify serialization works
        serialized = validation_response.model_dump()
        assert serialized["success"] is False
        assert len(serialized["errors"]) == 2
