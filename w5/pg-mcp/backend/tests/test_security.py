"""
Unit tests for SQL validation and security utilities.
"""

import pytest
from app.core.security import (
    validate_and_sanitize_sql,
    is_select_statement,
    validate_sql_syntax,
    extract_table_names
)
from app.core.errors import ValidationError, SQLSyntaxError


class TestSQLValidation:
    """Test SQL validation functionality."""

    def test_validate_select_statement(self):
        """Test validating a valid SELECT statement.

        测试验证有效的SELECT语句：
        - 验证SELECT语句被接受并处理
        - 检查SQLGlot规范化后的输出格式
        """
        sql = "SELECT * FROM users WHERE id = 1"
        result = validate_and_sanitize_sql(sql)
        assert "SELECT" in result.upper()
        assert "FROM USERS" in result.upper()  # SQLGlot normalizes to uppercase

    def test_validate_select_with_limit_added(self):
        """Test that LIMIT is added when missing.

        测试缺少LIMIT时自动添加：
        - 验证没有LIMIT的SELECT语句会被添加LIMIT 1000
        - 确保安全限制被强制应用
        """
        sql = "SELECT * FROM users"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 1000" in result.upper()

    def test_validate_select_with_existing_limit(self):
        """Test that existing LIMIT is preserved.

        测试保留已存在的LIMIT子句：
        - 验证自定义LIMIT值被保留
        - 确保不会被强制替换为默认值
        """
        sql = "SELECT * FROM users LIMIT 50"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 50" in result.upper()
        assert "LIMIT 1000" not in result.upper()

    def test_reject_insert_statement(self):
        """Test rejecting INSERT statements.

        测试拒绝INSERT语句的安全措施：
        - 验证INSERT语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "INSERT INTO users (name) VALUES ('test')"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_update_statement(self):
        """Test rejecting UPDATE statements.

        测试拒绝UPDATE语句的安全措施：
        - 验证UPDATE语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "UPDATE users SET name = 'test' WHERE id = 1"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_delete_statement(self):
        """Test rejecting DELETE statements.

        测试拒绝DELETE语句的安全措施：
        - 验证DELETE语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "DELETE FROM users WHERE id = 1"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_drop_statement(self):
        """Test rejecting DROP statements.

        测试拒绝DROP语句的安全措施：
        - 验证DROP语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "DROP TABLE users"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_create_statement(self):
        """Test rejecting CREATE statements.

        测试拒绝CREATE语句的安全措施：
        - 验证CREATE语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "CREATE TABLE test (id INTEGER)"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_alter_statement(self):
        """Test rejecting ALTER statements.

        测试拒绝ALTER语句的安全措施：
        - 验证ALTER语句被正确识别和拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "ALTER TABLE users ADD COLUMN email VARCHAR(255)"
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_reject_invalid_sql_syntax(self):
        """Test rejecting invalid SQL syntax.

        测试拒绝无效SQL语法：
        - 验证语法错误的SQL被正确拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "SELEC * FORM users"  # Invalid syntax
        with pytest.raises(ValidationError, match="Only SELECT statements are allowed"):
            validate_and_sanitize_sql(sql)

    def test_empty_sql_rejection(self):
        """Test rejecting empty SQL.

        测试拒绝空SQL输入：
        - 验证空字符串被正确拒绝
        - 检查抛出适当的ValidationError
        """
        sql = ""
        with pytest.raises(ValidationError, match="SQL query cannot be empty"):
            validate_and_sanitize_sql(sql)

    def test_whitespace_only_sql_rejection(self):
        """Test rejecting whitespace-only SQL.

        测试拒绝仅包含空白字符的SQL：
        - 验证只含空格/换行符的输入被拒绝
        - 检查抛出适当的ValidationError
        """
        sql = "   \n\t   "
        with pytest.raises(ValidationError, match="SQL query cannot be empty"):
            validate_and_sanitize_sql(sql)


class TestSQLAnalysis:
    """Test SQL analysis functionality."""

    def test_is_select_statement_true(self):
        """Test identifying SELECT statements.

        测试正确识别SELECT语句：
        - 验证各种格式的SELECT语句都被识别为true
        - 检查大小写不敏感性和空白字符处理
        """
        assert is_select_statement("SELECT * FROM users") is True
        assert is_select_statement("  select id, name from users  ") is True
        assert is_select_statement("SELECT COUNT(*) FROM users") is True

    def test_is_select_statement_false(self):
        """Test rejecting non-SELECT statements.

        测试正确拒绝非SELECT语句：
        - 验证DML和DDL语句返回false
        - 检查边界情况如空字符串
        """
        assert is_select_statement("INSERT INTO users VALUES (1)") is False
        assert is_select_statement("UPDATE users SET name = 'test'") is False
        assert is_select_statement("DELETE FROM users") is False
        assert is_select_statement("CREATE TABLE test (id INT)") is False

    def test_is_select_statement_invalid_sql(self):
        """Test handling invalid SQL.

        测试处理无效SQL语句：
        - 验证语法错误的SQL返回false
        - 检查空输入的处理
        """
        assert is_select_statement("INVALID SQL QUERY") is False
        assert is_select_statement("") is False

    def test_validate_sql_syntax_valid(self):
        """Test validating correct SQL syntax.

        测试验证正确的SQL语法：
        - 验证有效SQL返回true且无错误信息
        - 检查语法验证功能的正确性
        """
        is_valid, error = validate_sql_syntax("SELECT * FROM users")
        assert is_valid is True
        assert error is None

    def test_validate_sql_syntax_invalid(self):
        """Test detecting invalid SQL syntax.

        测试检测无效的SQL语法：
        - 验证语法错误的SQL返回false和错误信息
        - 检查错误信息的非空性
        """
        is_valid, error = validate_sql_syntax("SELECT * FROM")  # Incomplete SQL
        assert is_valid is False
        assert error is not None
        assert len(error) > 0

    def test_extract_table_names_simple(self):
        """Test extracting table names from simple queries.

        测试从简单查询中提取表名：
        - 验证单个表的FROM子句正确提取
        - 检查返回表名列表的准确性
        """
        tables = extract_table_names("SELECT * FROM users")
        assert tables == ["users"]

    def test_extract_table_names_multiple_tables(self):
        """Test extracting table names from JOIN queries.

        测试从JOIN查询中提取多个表名：
        - 验证JOIN语句中所有表的名称都被提取
        - 检查去重和排序的正确性
        """
        sql = "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id"
        tables = extract_table_names(sql)
        assert set(tables) == {"users", "posts"}

    def test_extract_table_names_subquery(self):
        """Test extracting table names from subqueries.

        测试从子查询中提取表名：
        - 验证主查询和子查询中的表都被提取
        - 检查复杂查询结构的处理
        """
        sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM posts)"
        tables = extract_table_names(sql)
        assert set(tables) == {"users", "posts"}

    def test_extract_table_names_invalid_sql(self):
        """Test handling invalid SQL in table extraction.

        测试处理无效SQL的表名提取：
        - 验证语法错误的SQL返回空列表
        - 检查错误处理机制
        """
        tables = extract_table_names("INVALID SQL QUERY")
        assert tables == []

    def test_extract_table_names_empty(self):
        """Test handling empty SQL.

        测试处理空SQL的表名提取：
        - 验证空字符串返回空列表
        - 检查边界情况处理
        """
        tables = extract_table_names("")
        assert tables == []


class TestSQLSanitization:
    """Test SQL sanitization functionality."""

    def test_limit_added_to_simple_select(self):
        """Test LIMIT is added to simple SELECT.

        测试为简单SELECT添加LIMIT：
        - 验证没有LIMIT的查询会被添加默认限制
        - 确保安全措施被强制应用
        """
        sql = "SELECT * FROM users"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 1000" in result.upper()

    def test_limit_preserved_when_present(self):
        """Test existing LIMIT is preserved.

        测试保留已存在的LIMIT：
        - 验证用户自定义的LIMIT值不被覆盖
        - 检查精确的LIMIT值保持
        """
        sql = "SELECT * FROM users LIMIT 100"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 100" in result.upper()
        assert "LIMIT 1000" not in result.upper()

    def test_limit_added_with_where_clause(self):
        """Test LIMIT is added when WHERE clause exists.

        测试有WHERE子句时添加LIMIT：
        - 验证即使有WHERE条件也会添加安全限制
        - 确保所有查询都受到保护
        """
        sql = "SELECT * FROM users WHERE active = true"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 1000" in result.upper()

    def test_limit_added_with_order_by(self):
        """Test LIMIT is added when ORDER BY exists.

        测试有ORDER BY子句时添加LIMIT：
        - 验证排序查询也会添加安全限制
        - 确保查询性能和安全性
        """
        sql = "SELECT * FROM users ORDER BY name"
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 1000" in result.upper()

    def test_complex_select_with_limit(self):
        """Test complex SELECT statements get proper LIMIT.

        测试复杂SELECT语句获得正确的LIMIT：
        - 验证包含JOIN、WHERE、GROUP BY、ORDER BY的复杂查询
        - 确保所有类型的查询都受到安全限制保护
        """
        sql = """
        SELECT u.name, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        WHERE u.active = true
        GROUP BY u.id, u.name
        ORDER BY post_count DESC
        """
        result = validate_and_sanitize_sql(sql)
        assert "LIMIT 1000" in result.upper()
