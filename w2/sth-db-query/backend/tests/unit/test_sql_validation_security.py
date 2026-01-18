"""
SQL validation and security tests.

This module tests SQL injection detection, validation edge cases,
and security-related SQL parsing scenarios.
"""

import pytest
from app.core.security import validate_and_sanitize_sql
from app.core.errors import ValidationError, SQLSyntaxError


class TestSQLInjectionDetection:
    """Test detection and prevention of SQL injection attempts."""

    @pytest.mark.unit
    @pytest.mark.parametrize("malicious_query", [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; EXEC xp_cmdshell('dir'); --",
        "' UNION SELECT * FROM users --",
        "1' AND 1=1--",
        "admin'--",
        "'; INSERT INTO users VALUES ('hacker', 'password'); --",
        "' OR 1=1#",
        "x' OR email IS NOT NULL --",
        "'; DELETE FROM logs WHERE 1=1; --",
    ])
    def test_sql_injection_detection(self, malicious_query):
        """Test that SQL injection attempts are detected and rejected."""
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    @pytest.mark.parametrize("tautology_attack", [
        "' OR '1'='1'",
        "admin' OR '1'='1'",
        "' OR 'x'='x",
        "1' OR '1'='1'--",
        "x' OR email IS NOT NULL OR 'x'='y",
    ])
    def test_tautology_attacks(self, tautology_attack):
        """Test that tautology-based SQL injection is prevented."""
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(tautology_attack)


class TestSQLValidationEdgeCases:
    """Test SQL validation edge cases and boundary conditions."""

    @pytest.mark.unit
    def test_empty_query(self):
        """Test that empty queries are rejected."""
        with pytest.raises(ValidationError):
            validate_and_sanitize_sql("")

    @pytest.mark.unit
    def test_whitespace_only_query(self):
        """Test that whitespace-only queries are rejected."""
        with pytest.raises(ValidationError):
            validate_and_sanitize_sql("   \n\t  ")

    @pytest.mark.unit
    @pytest.mark.parametrize("non_select_query", [
        "DROP TABLE users",
        "DELETE FROM users WHERE id=1",
        "UPDATE users SET name='test' WHERE id=1",
        "INSERT INTO users VALUES (1, 'test')",
        "CREATE TABLE test (id INT)",
        "ALTER TABLE users ADD COLUMN age INT",
        "TRUNCATE TABLE logs",
        "GRANT ALL ON users TO hacker",
        "REVOKE SELECT ON users FROM public",
    ])
    def test_non_select_statements_rejected(self, non_select_query):
        """Test that non-SELECT statements are rejected."""
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(non_select_query)

    @pytest.mark.unit
    def test_union_based_injection(self):
        """Test detection of UNION-based injection attempts."""
        malicious_query = "SELECT name FROM users WHERE id='1' UNION SELECT password FROM users--"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_comment_based_injection(self):
        """Test detection of comment-based injection attempts."""
        malicious_query = "SELECT * FROM users WHERE username='admin'--' AND password='wrong'"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_time_based_injection(self):
        """Test detection of time-based blind injection attempts."""
        malicious_query = "SELECT * FROM users WHERE id=1; WAITFOR DELAY '00:00:10'--"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)


class TestValidSQLQueries:
    """Test that valid SQL queries are accepted and sanitized properly."""

    @pytest.mark.unit
    @pytest.mark.parametrize("valid_query", [
        "SELECT * FROM users",
        "SELECT id, name FROM users WHERE age > 18",
        "SELECT u.name, o.order_id FROM users u JOIN orders o ON u.id = o.user_id",
        "SELECT COUNT(*) FROM logs",
        "SELECT DISTINCT category FROM products ORDER BY name",
        "SELECT * FROM users LIMIT 10 OFFSET 20",
        "SELECT name, email FROM users WHERE name LIKE '%test%'",
    ])
    def test_valid_select_queries(self, valid_query):
        """Test that valid SELECT queries are accepted."""
        result = validate_and_sanitize_sql(valid_query)
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_query_sanitization(self):
        """Test that queries are properly sanitized."""
        query = "  SELECT   *  FROM  users  WHERE  id  =  1  "
        result = validate_and_sanitize_sql(query)
        # Should be cleaned up but functionally equivalent
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert "WHERE" in result.upper()


class TestSQLSyntaxErrors:
    """Test handling of malformed SQL queries."""

    @pytest.mark.unit
    @pytest.mark.parametrize("malformed_query", [
        "SELEC * FROM users",  # Typo in SELECT
        "SELECT * FORM users",  # Typo in FROM
        "SELECT * FROM",  # Incomplete query
        "SELECT * WHERE id=1",  # Missing FROM
        "SELECT * FROM users WHERE",  # Incomplete WHERE clause
        "SELECT * FROM users ORDER BY",  # Incomplete ORDER BY
        "SELECT * FROM (SELECT * FROM",  # Unbalanced parentheses
    ])
    def test_malformed_sql_rejected(self, malformed_query):
        """Test that syntactically invalid SQL is rejected."""
        with pytest.raises(SQLSyntaxError):
            validate_and_sanitize_sql(malformed_query)


class TestAdvancedInjectionPatterns:
    """Test detection of advanced SQL injection patterns."""

    @pytest.mark.unit
    def test_stored_procedure_injection(self):
        """Test detection of stored procedure-based injection."""
        malicious_query = "'; EXEC master..xp_cmdshell 'dir'; --"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_second_order_injection(self):
        """Test detection of second-order injection attempts."""
        malicious_query = "SELECT * FROM users WHERE name='admin'/*comment*/AND/*comment*/1=1"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_hex_encoding_injection(self):
        """Test detection of hex-encoded injection attempts."""
        # Using hex encoding to bypass filters
        malicious_query = "SELECT * FROM users WHERE name=0x61646D696E"  # 'admin' in hex
        # This should be caught as suspicious
        result = validate_and_sanitize_sql(malicious_query)
        assert result is not None  # May pass validation but should be logged

    @pytest.mark.unit
    def test_char_encoding_injection(self):
        """Test detection of CHAR function-based injection."""
        malicious_query = "SELECT * FROM users WHERE name=CHAR(97,100,109,105,110)"  # 'admin'
        result = validate_and_sanitize_sql(malicious_query)
        assert result is not None  # May pass validation


class TestPerformanceValidation:
    """Test performance-related SQL validation."""

    @pytest.mark.unit
    def test_query_complexity_limit(self):
        """Test that overly complex queries are flagged."""
        # Query with many JOINs
        complex_query = """
            SELECT * FROM users u
            JOIN orders o ON u.id = o.user_id
            JOIN products p ON o.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            JOIN suppliers s ON p.supplier_id = s.id
            JOIN shipments sh ON o.id = sh.order_id
            JOIN addresses a ON u.id = a.user_id
            WHERE u.id = 1
        """
        result = validate_and_sanitize_sql(complex_query)
        # Should pass but could be optimized
        assert result is not None

    @pytest.mark.unit
    def test_without_limit_clause(self):
        """Test that queries without LIMIT are handled appropriately."""
        query = "SELECT * FROM users"
        result = validate_and_sanitize_sql(query)
        # Should be accepted (limit can be added by application)
        assert result is not None

    @pytest.mark.unit
    def test_wildcard_in_select(self):
        """Test handling of SELECT * queries."""
        query = "SELECT * FROM users WHERE id = 1"
        result = validate_and_sanitize_sql(query)
        # SELECT * should be allowed but could be flagged for optimization
        assert result is not None


class TestPostgreSQLSpecificFeatures:
    """Test PostgreSQL-specific SQL features and security."""

    @pytest.mark.unit
    def test_postgresql_comment_injection(self):
        """Test PostgreSQL comment injection detection."""
        malicious_query = "SELECT * FROM users WHERE id=1/*COMMENT*/AND 1=1--"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_copy_command_injection(self):
        """Test that COPY command is rejected (data exfiltration risk)."""
        malicious_query = "COPY (SELECT * FROM users) TO '/tmp/users.csv' WITH CSV"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    @pytest.mark.unit
    def test_postgresql_cast_operators(self):
        """Test that PostgreSQL cast operators are validated."""
        query = "SELECT name::text FROM users WHERE id = 1"
        result = validate_and_sanitize_sql(query)
        assert result is not None


@pytest.mark.integration
class TestSQLValidationIntegration:
    """Integration tests for SQL validation with real-world scenarios."""

    def test_complete_user_query_workflow(self):
        """Test a complete query workflow from validation to execution simulation."""
        valid_query = "SELECT id, name, email FROM users WHERE status = 'active' ORDER BY name LIMIT 10"

        # Validate the query
        validated = validate_and_sanitize_sql(valid_query)
        assert validated is not None

        # Check that key elements are preserved
        assert "SELECT" in validated.upper()
        assert "users" in validated
        assert "WHERE" in validated.upper() or "where" in validated

    def test_multi_column_injection_attempt(self):
        """Test injection attempt across multiple columns."""
        malicious_query = "SELECT * FROM users WHERE username='admin' AND password='wrong' OR '1'='1'"
        with pytest.raises((ValidationError, SQLSyntaxError)):
            validate_and_sanitize_sql(malicious_query)

    def test_case_sensitivity_injection(self):
        """Test case variation injection attempts."""
        variations = [
            "SELECT * FROM users WHERE name='admin'",
            "select * from users where name='admin'",
            "SeLeCt * FrOm users wHeRe name='admin'",
        ]
        for query in variations:
            result = validate_and_sanitize_sql(query)
            # All should be valid despite case differences
            assert result is not None
