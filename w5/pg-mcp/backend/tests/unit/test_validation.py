"""
Unit tests for database URL validation functionality.
"""

import pytest
from urllib.parse import urlparse


class TestDatabaseURLValidation:
    """Test database URL validation logic."""

    def test_valid_postgresql_url(self):
        """Test validation of valid PostgreSQL URLs.

        测试有效PostgreSQL URL的验证：
        - 验证包含完整凭据的主机名和端口的URL
        - 测试省略密码的情况
        - 检查使用默认端口的情况
        - 验证IP地址作为主机名的用法
        """
        valid_urls = [
            "postgresql://user:pass@localhost:5432/dbname",
            "postgresql://user@localhost:5432/dbname",
            "postgresql://localhost:5432/dbname",
            "postgresql://user:pass@host.com:5432/dbname",
            "postgresql://user:pass@host.com/dbname",  # default port
            "postgresql://user:pass@192.168.1.1:5432/dbname",
        ]

        for url in valid_urls:
            assert self._is_valid_database_url(url), f"URL should be valid: {url}"

    def test_invalid_postgresql_url(self):
        """Test validation of invalid PostgreSQL URLs.

        测试无效PostgreSQL URL的验证：
        - 验证错误的scheme（如mysql）被拒绝
        - 测试不完整的URL（如缺少数据库名、主机名）
        - 检查空字符串和非URL格式的输入
        """
        invalid_urls = [
            "mysql://user:pass@localhost:3306/dbname",  # wrong scheme
            "postgresql://user:pass@",  # incomplete
            "postgresql://user:pass@localhost",  # no database
            "postgresql://user:pass@:5432/dbname",  # empty host
            "postgresql://:pass@localhost:5432/dbname",  # empty user
            "",  # empty string
            "not-a-url",  # not a URL
        ]

        for url in invalid_urls:
            assert not self._is_valid_database_url(url), f"URL should be invalid: {url}"

    def test_postgresql_url_components(self):
        """Test extraction of PostgreSQL URL components.

        测试PostgreSQL URL组件的提取：
        - 验证scheme、hostname、port的正确解析
        - 检查username、password的提取
        - 确保path（数据库名）的正确获取
        """
        url = "postgresql://user:pass@localhost:5432/dbname"
        parsed = urlparse(url)

        assert parsed.scheme == "postgresql"
        assert parsed.hostname == "localhost"
        assert parsed.port == 5432
        assert parsed.username == "user"
        assert parsed.password == "pass"
        assert parsed.path == "/dbname"

    def test_database_name_extraction(self):
        """Test extraction of database name from URL.

        测试从URL中提取数据库名称：
        - 验证标准格式和省略端口格式的数据库名提取
        - 测试包含下划线和复杂名称的数据库
        - 确保path前缀斜杠被正确移除
        """
        test_cases = [
            ("postgresql://user:pass@localhost:5432/dbname", "dbname"),
            ("postgresql://user:pass@localhost/dbname", "dbname"),
            ("postgresql://localhost:5432/dbname", "dbname"),
            ("postgresql://user:pass@host.com:5432/complex_db_name", "complex_db_name"),
        ]

        for url, expected_db in test_cases:
            parsed = urlparse(url)
            db_name = parsed.path.lstrip('/')
            assert db_name == expected_db, f"Expected {expected_db}, got {db_name} for URL {url}"

    def test_connection_string_validation(self):
        """Test validation of complete connection strings.

        测试完整连接字符串的验证：
        - 验证连接对象的必需字段存在
        - 检查字段类型的正确性
        - 为完整的验证逻辑实现预留位置
        """
        # This would test the full validation logic once implemented
        valid_connection = {
            "name": "test_db",
            "url": "postgresql://user:pass@localhost:5432/test_db",
            "description": "Test database"
        }

        # Basic structure validation
        assert "name" in valid_connection
        assert "url" in valid_connection
        assert isinstance(valid_connection["name"], str)
        assert isinstance(valid_connection["url"], str)

    def test_empty_url_validation(self):
        """Test validation of empty or None URLs.

        测试空值或None URL的验证：
        - 验证空字符串被正确拒绝
        - 检查None值被正确处理
        - 确保边界情况下的鲁棒性
        """
        assert not self._is_valid_database_url("")
        assert not self._is_valid_database_url(None)

    def test_url_scheme_validation(self):
        """Test validation of URL schemes.

        测试URL scheme的验证：
        - 验证postgresql和postgres scheme被接受
        - 确保其他数据库scheme（如mysql、sqlite等）被拒绝
        - 检查非数据库scheme（如http、https）也被拒绝
        """
        valid_schemes = ["postgresql", "postgres"]
        invalid_schemes = ["mysql", "sqlite", "oracle", "mssql", "http", "https"]

        for scheme in valid_schemes:
            url = f"{scheme}://user:pass@localhost:5432/dbname"
            assert self._is_valid_database_url(url), f"Scheme {scheme} should be valid"

        for scheme in invalid_schemes:
            url = f"{scheme}://user:pass@localhost:5432/dbname"
            assert not self._is_valid_database_url(url), f"Scheme {scheme} should be invalid"

    def _is_valid_database_url(self, url: str) -> bool:
        """
        Helper method to validate database URL.
        This is a placeholder - actual implementation will be in the validation service.
        """
        if not url or not isinstance(url, str):
            return False

        try:
            parsed = urlparse(url)
            # Basic validation
            if not (
                parsed.scheme in ["postgresql", "postgres"] and
                parsed.hostname is not None and
                parsed.path and parsed.path != '/'
            ):
                return False

            # Additional validation: if username is provided, it should not be empty
            if parsed.username is not None and parsed.username == "":
                return False

            # Host should not be empty
            if parsed.hostname == "":
                return False

            return True
        except Exception:
            return False
