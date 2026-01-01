"""
Unit tests for PostgreSQL URL format validation.
"""

import pytest
from urllib.parse import urlparse


class TestPostgreSQLURLValidation:
    """Test PostgreSQL-specific URL validation logic."""

    def test_valid_postgresql_urls(self):
        """Test validation of correctly formatted PostgreSQL URLs.

        测试正确格式化的PostgreSQL URL验证：
        - 验证包含完整凭据的主机名和端口的URL
        - 测试IPv6地址格式
        - 检查URL编码字符的处理
        - 确保各种有效URL格式都被接受
        """
        valid_urls = [
            "postgresql://user:password@localhost:5432/database",
            "postgresql://user@localhost:5432/database",
            "postgresql://localhost:5432/database",
            "postgresql://user:password@host.example.com:5432/db_name",
            "postgresql://user:password@192.168.1.100:5432/my_db",
            "postgresql://user:password@[::1]:5432/database",  # IPv6
            "postgresql://user%40domain:pass@localhost:5432/db",  # URL-encoded chars
        ]

        for url in valid_urls:
            assert self._is_valid_postgres_url(url), f"URL should be valid: {url}"

    def test_invalid_postgresql_urls(self):
        """Test rejection of invalid PostgreSQL URLs.

        测试无效PostgreSQL URL的拒绝：
        - 验证错误scheme（如mysql、postgres、http）被拒绝
        - 检查缺少主机名或数据库名的URL
        - 测试无效端口号的处理
        - 确保各种无效格式都被正确拒绝
        """
        invalid_urls = [
            "mysql://user:pass@localhost:3306/db",  # Wrong scheme
            "postgres://user:pass@localhost:5432/db",  # Wrong scheme (postgres vs postgresql)
            "http://user:pass@localhost:5432/db",  # HTTP scheme
            "postgresql://user:pass@",  # Missing host
            "postgresql://user:pass@:5432/db",  # Empty host
            "postgresql://user:pass@localhost",  # Missing database
            "postgresql://user:pass@localhost:5432/",  # Empty database
            "postgresql://user:pass@localhost:5432",  # Missing database entirely
            "",  # Empty string
            "not-a-url",  # Not a URL
            "postgresql://user:pass@localhost:99999/db",  # Invalid port (too high)
            "postgresql://user:pass@localhost:0/db",  # Invalid port (zero)
        ]

        for url in invalid_urls:
            assert not self._is_valid_postgres_url(url), f"URL should be invalid: {url}"

    def test_postgresql_port_validation(self):
        """Test PostgreSQL port number validation.

        测试PostgreSQL端口号验证：
        - 验证有效端口范围（1-65535）内的端口被接受
        - 检查无效端口（如0、负数、超过65535）被拒绝
        - 确保端口验证的边界条件正确
        """
        # Valid ports
        valid_ports = [5432, 1, 65535, 10000, 20000]
        for port in valid_ports:
            url = f"postgresql://user:pass@localhost:{port}/db"
            assert self._is_valid_postgres_url(url), f"Port {port} should be valid"

        # Invalid ports
        invalid_ports = [0, -1, 65536, 99999, "abc"]
        for port in invalid_ports:
            url = f"postgresql://user:pass@localhost:{port}/db"
            assert not self._is_valid_postgres_url(url), f"Port {port} should be invalid"

    def test_postgresql_database_name_validation(self):
        """Test PostgreSQL database name validation.

        测试PostgreSQL数据库名验证：
        - 验证有效数据库名格式（字母、数字、下划线、连字符）
        - 检查最大长度限制（63字符）
        - 确保包含空格或特殊字符的名称被拒绝
        """
        # Valid database names
        valid_db_names = [
            "mydb",
            "my_db",
            "db-with-dashes",
            "db_with_underscores",
            "123database",
            "database123",
            "a",  # Single character
            "a" * 63,  # Maximum length (PostgreSQL limit)
        ]

        for db_name in valid_db_names:
            url = f"postgresql://user:pass@localhost:5432/{db_name}"
            assert self._is_valid_postgres_url(url), f"Database name '{db_name}' should be valid"

        # Invalid database names (too long, special chars)
        invalid_db_names = [
            "",  # Empty
            "a" * 64,  # Too long
            "db with spaces",
            "db@special",
            "db#hash",
            "db$dollar",
            "db%percent",
        ]

        for db_name in invalid_db_names:
            url = f"postgresql://user:pass@localhost:5432/{db_name}"
            assert not self._is_valid_postgres_url(url), f"Database name '{db_name}' should be invalid"

    def test_postgresql_username_validation(self):
        """Test PostgreSQL username validation.

        测试PostgreSQL用户名验证：
        - 验证有效用户名格式（字母、数字、下划线、连字符）
        - 检查包含@符号的用户名（URL编码后）
        - 确保空用户名被拒绝
        """
        # Valid usernames
        valid_usernames = [
            "user",
            "user_name",
            "user-name",
            "user123",
            "123user",
            "user%40domain.com",  # URL-encoded @ symbol
        ]

        for username in valid_usernames:
            url = f"postgresql://{username}:pass@localhost:5432/db"
            assert self._is_valid_postgres_url(url), f"Username '{username}' should be valid"

        # Invalid usernames (empty)
        invalid_usernames = [""]
        for username in invalid_usernames:
            url = f"postgresql://{username}:pass@localhost:5432/db"
            assert not self._is_valid_postgres_url(url), f"Username '{username}' should be invalid"

    def test_postgresql_password_validation(self):
        """Test PostgreSQL password validation.

        测试PostgreSQL密码验证：
        - 验证密码可以包含特殊字符和空格
        - 检查空密码是被允许的
        - 确保URL编码的密码字符串被正确处理
        """
        # Passwords can be empty or contain special characters
        valid_passwords = [
            "password",
            "pass123",
            "p%40ssw0rd%21",  # URL-encoded @ and !
            "pass%20with%20spaces",  # URL-encoded spaces
            "",  # Empty password
            "pass%2520with%2520encoding",  # URL-encoded
        ]

        for password in valid_passwords:
            url = f"postgresql://user:{password}@localhost:5432/db"
            assert self._is_valid_postgres_url(url), f"Password '{password}' should be valid"

    def test_postgresql_host_validation(self):
        """Test PostgreSQL host validation.

        测试PostgreSQL主机验证：
        - 验证各种主机名格式（localhost、IP地址、域名）
        - 检查IPv6地址格式的支持
        - 确保包含无效字符的主机名被拒绝
        """
        # Valid hosts
        valid_hosts = [
            "localhost",
            "127.0.0.1",
            "192.168.1.100",
            "[::1]",  # IPv6 with brackets (correct format)
            "host.example.com",
            "sub.domain.example.com",
            "host-name",
            "host_name",
        ]

        for host in valid_hosts:
            url = f"postgresql://user:pass@{host}:5432/db"
            assert self._is_valid_postgres_url(url), f"Host '{host}' should be valid"

        # Invalid hosts
        invalid_hosts = [
            "",  # Empty
            "host with spaces",
            "host@domain",  # Invalid character
            "host#domain",  # Invalid character
        ]

        for host in invalid_hosts:
            url = f"postgresql://user:pass@{host}:5432/db"
            assert not self._is_valid_postgres_url(url), f"Host '{host}' should be invalid"

    def test_postgresql_url_components_extraction(self):
        """Test extraction of components from PostgreSQL URLs.

        测试从PostgreSQL URL提取组件：
        - 验证scheme、username、password的正确解析
        - 检查hostname、port、database的提取
        - 确保各种URL格式的组件都能正确分离
        """
        test_cases = [
            {
                "url": "postgresql://user:pass@localhost:5432/db",
                "expected": {
                    "scheme": "postgresql",
                    "username": "user",
                    "password": "pass",
                    "hostname": "localhost",
                    "port": 5432,
                    "database": "db"
                }
            },
            {
                "url": "postgresql://user@localhost:5432/db",
                "expected": {
                    "scheme": "postgresql",
                    "username": "user",
                    "password": None,
                    "hostname": "localhost",
                    "port": 5432,
                    "database": "db"
                }
            },
            {
                "url": "postgresql://localhost:5432/db",
                "expected": {
                    "scheme": "postgresql",
                    "username": None,
                    "password": None,
                    "hostname": "localhost",
                    "port": 5432,
                    "database": "db"
                }
            }
        ]

        for case in test_cases:
            parsed = urlparse(case["url"])
            assert parsed.scheme == case["expected"]["scheme"]
            assert parsed.username == case["expected"]["username"]
            assert parsed.password == case["expected"]["password"]
            assert parsed.hostname == case["expected"]["hostname"]
            assert parsed.port == case["expected"]["port"]
            assert parsed.path.lstrip('/') == case["expected"]["database"]

    def test_postgresql_connection_string_generation(self):
        """Test generation of PostgreSQL connection strings.

        测试PostgreSQL连接字符串生成：
        - 验证从组件构建完整URL的功能
        - 检查认证信息、主机、端口、数据库的正确组合
        - 确保生成的URL格式标准且正确
        """
        # This would test the reverse: creating URLs from components
        components = {
            "username": "user",
            "password": "pass",
            "host": "localhost",
            "port": 5432,
            "database": "db"
        }

        expected_url = "postgresql://user:pass@localhost:5432/db"
        generated_url = self._build_postgres_url(**components)
        assert generated_url == expected_url

    def test_postgresql_url_normalization(self):
        """Test URL normalization for PostgreSQL.

        测试PostgreSQL URL规范化：
        - 验证等效URL规范化后的统一性
        - 检查路径末尾斜杠的移除
        - 确保规范化后的URL格式一致
        """
        # Test that equivalent URLs are normalized the same way
        equivalent_urls = [
            "postgresql://user:pass@localhost:5432/db",
            "postgresql://user:pass@localhost:5432/db/",  # trailing slash
        ]

        normalized = [self._normalize_postgres_url(url) for url in equivalent_urls]
        assert all(url == normalized[0] for url in normalized), "Equivalent URLs should normalize to the same string"

    def _is_valid_postgres_url(self, url: str) -> bool:
        """
        Helper method to validate PostgreSQL URL.
        This is a placeholder - actual implementation will be in the validation service.
        """
        if not url or not isinstance(url, str):
            return False

        try:
            parsed = urlparse(url)

            # Must be postgresql scheme
            if parsed.scheme != "postgresql":
                return False

            # Netloc should not contain multiple @ symbols (invalid URL format)
            if parsed.netloc.count('@') > 1:
                return False

            # Must have hostname (handle IPv6 addresses)
            hostname = parsed.hostname
            if not hostname:
                # Check if it's an IPv6 address in brackets
                if parsed.netloc and parsed.netloc.startswith('[') and ']' in parsed.netloc:
                    hostname = parsed.netloc.split(']')[0] + ']'
                elif '::' in parsed.netloc:
                    # Extract hostname from netloc (remove credentials if present)
                    if '@' in parsed.netloc:
                        # user:pass@::1:5432 -> ::1
                        after_auth = parsed.netloc.split('@', 1)[1]
                        # Find the IPv6 address before the port
                        # IPv6 addresses contain :: and may be followed by :port
                        if ':' in after_auth:
                            # Split and find where the IPv6 address ends
                            parts = after_auth.split(':')
                            ipv6_parts = []
                            for i, part in enumerate(parts):
                                ipv6_parts.append(part)
                                # Check if this looks like an IPv6 address
                                test_addr = ':'.join(ipv6_parts)
                                if '::' in test_addr and test_addr.count(':') >= 2:
                                    # This might be the full IPv6 address
                                    hostname = test_addr
                                    break
                            else:
                                # Fallback: assume first part is hostname
                                hostname = parts[0]
                        else:
                            hostname = after_auth
                    else:
                        # ::1:5432 -> ::1
                        hostname = parsed.netloc.split(':')[0]
                else:
                    return False

            # Port must be valid if specified
            # Handle IPv6 addresses where urlparse can't properly parse the port
            try:
                port = parsed.port
                # urlparse.port validates range 0-65535, but we want 1-65535
                if port is not None and (port < 1 or port > 65535):
                    return False
            except (ValueError, TypeError):
                # Port is invalid (out of range, not a number, etc.)
                return False
            if port is None and hostname and '::' in hostname:
                # For IPv6 addresses, port might not be parsed correctly by urlparse
                # Check if there's a port after the hostname in netloc
                if '@' in parsed.netloc:
                    after_auth = parsed.netloc.split('@', 1)[1]
                else:
                    after_auth = parsed.netloc
                # Look for :port after hostname
                if ':' in after_auth and not after_auth.endswith(':'):
                    try:
                        port_str = after_auth.split(':', 1)[1]
                        if port_str.isdigit():
                            port = int(port_str)
                            if port < 1 or port > 65535:
                                return False
                    except (ValueError, IndexError):
                        pass
            # Hostname should not contain spaces or @
            if hostname and (' ' in hostname or '@' in hostname):
                return False

            # Must have database name
            if not parsed.path or parsed.path == '/':
                return False

            # Database name should not be too long and not contain invalid chars
            db_name = parsed.path.lstrip('/')
            # Fragment is not allowed in database URLs
            if parsed.fragment:
                return False
            if len(db_name) > 63 or ' ' in db_name or not all(c.isalnum() or c in '_-' for c in db_name):
                return False

            # Username should not be empty and should not contain invalid chars
            if parsed.username is not None and len(parsed.username.strip()) == 0:
                return False

            return True
        except Exception:
            return False

    def _build_postgres_url(self, username: str, password: str, host: str, port: int, database: str) -> str:
        """Helper to build PostgreSQL URL from components."""
        auth = f"{username}:{password}@" if password else f"{username}@" if username else ""
        return f"postgresql://{auth}{host}:{port}/{database}"

    def _normalize_postgres_url(self, url: str) -> str:
        """Helper to normalize PostgreSQL URL."""
        parsed = urlparse(url)
        # Remove trailing slash from path
        path = parsed.path.rstrip('/')
        # Reconstruct URL
        return parsed._replace(path=path).geturl()
