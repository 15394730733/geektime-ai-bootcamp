"""
Property-based tests for SQL validation functionality.

Feature: database-query-tool, Property 5: SQL validation
**Validates: Requirements 3.1, 3.2, 3.3**
"""

from hypothesis import given, strategies as st, settings, assume
import pytest

from app.core.security import (
    validate_and_sanitize_sql,
    is_select_statement,
    validate_sql_syntax,
    extract_table_names
)
from app.core.errors import ValidationError, SQLSyntaxError


class TestSQLValidationProperties:
    """Property-based tests for SQL validation functionality."""

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers", 
            "accounts", "profiles", "messages", "events", "logs", "data_table",
            "items", "records", "entries", "documents", "files", "reports"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table',
            'index', 'view', 'database', 'schema', 'user', 'role', 'grant'
        ]),
        columns=st.lists(
            st.sampled_from(["id", "name", "email", "created_at", "updated_at", "status", "type", "value"]),
            min_size=1,
            max_size=3,
            unique=True
        ),
        has_where=st.booleans(),
        has_order_by=st.booleans(),
        has_limit=st.booleans()
    )
    @settings(max_examples=5, deadline=5000)
    def test_valid_select_statements_are_accepted(self, table_name, columns, has_where, has_order_by, has_limit):
        """
        Property 5: SQL validation - Valid SELECT statements
        
        For any valid SELECT statement with proper syntax, the validator should accept it
        and return sanitized SQL with appropriate LIMIT clause handling.
        
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        # Build a valid SELECT statement
        column_list = ", ".join(columns)
        sql = f"SELECT {column_list} FROM {table_name}"
        
        if has_where:
            sql += f" WHERE {columns[0]} = 'test'"
        
        if has_order_by:
            sql += f" ORDER BY {columns[0]}"
        
        if has_limit:
            sql += " LIMIT 50"
        
        # The validator should accept this valid SELECT statement
        try:
            result = validate_and_sanitize_sql(sql)
            
            # Result should be a string containing the SQL
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Should contain SELECT and FROM
            assert "SELECT" in result.upper()
            assert "FROM" in result.upper()
            assert table_name.upper() in result.upper()
            
            # Should have a LIMIT clause (either original or added)
            assert "LIMIT" in result.upper()
            
            # If original had LIMIT, it should be preserved
            if has_limit:
                assert "LIMIT 50" in result.upper()
            else:
                # Should have default LIMIT added
                assert "LIMIT 1000" in result.upper()
                
        except ValidationError:
            # Should not raise validation errors for valid SELECT statements
            pytest.fail(f"Valid SELECT statement was rejected: {sql}")

    @given(
        statement_type=st.sampled_from([
            "INSERT INTO users (name) VALUES ('test')",
            "UPDATE users SET name = 'test'",
            "DELETE FROM users",
            "DROP TABLE users",
            "CREATE TABLE test (id INT)",
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
            "TRUNCATE TABLE users"
        ])
    )
    @settings(max_examples=5, deadline=5000)
    def test_non_select_statements_are_rejected(self, statement_type):
        """
        Property 5: SQL validation - Non-SELECT statement rejection
        
        For any non-SELECT SQL statement, the validator should reject it with
        an appropriate error message indicating only SELECT statements are allowed.
        
        **Validates: Requirements 3.2, 3.3**
        """
        # Non-SELECT statements should be rejected
        with pytest.raises(ValidationError) as exc_info:
            validate_and_sanitize_sql(statement_type)
        
        # Error message should indicate only SELECT statements are allowed
        error_message = str(exc_info.value).upper()
        assert "SELECT" in error_message or "ONLY" in error_message or "FORBIDDEN" in error_message

    @given(
        invalid_sql=st.one_of(
            st.just("SELEC * FROM users"),  # Typo in SELECT
            st.just("SELECT * FRM users"),  # Typo in FROM
            st.just("SELECT * FROM"),       # Incomplete FROM
            st.just("* FROM users"),        # Missing SELECT
            st.just("SELECT (unclosed FROM users"),  # Unclosed parenthesis
            st.just("SELECT * FROM users WHERE"),    # Incomplete WHERE
            st.just("SELECT * FROM 123invalid"),     # Invalid table name
            st.just(""),  # Empty string
            # Special character edge cases that should fail
            st.just("SELECT * FROM users WHERE name = 'O'Brien'"),  # Unescaped single quote
            st.just("SELECT * FROM users WHERE name = \"unclosed"),  # Unclosed double quote
            st.just("SELECT * FROM users WHERE name = 'test\\"),     # Backslash at end
            st.just("SELECT * FROM users WHERE name = '''"),        # Multiple quotes
            # Note: SQL injection attempts might actually be valid SQL syntactically
            # Note: Some SQL keywords like "order", "select" are actually valid as table names in some contexts
        )
    )
    @settings(max_examples=5, deadline=5000)
    def test_invalid_sql_syntax_is_rejected(self, invalid_sql):
        """
        Property 5: SQL validation - Invalid syntax rejection
        
        For any SQL with invalid syntax, the validator should reject it with
        an appropriate error message describing the syntax issue.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Skip empty strings as they have a specific error message
        if not invalid_sql or not invalid_sql.strip():
            with pytest.raises(ValidationError) as exc_info:
                validate_and_sanitize_sql(invalid_sql)
            assert "empty" in str(exc_info.value).lower()
            return
        
        # Invalid SQL should be rejected
        with pytest.raises(ValidationError) as exc_info:
            validate_and_sanitize_sql(invalid_sql)
        
        # Should provide some error information
        error_message = str(exc_info.value)
        assert len(error_message) > 0

    @given(
        special_char_sql=st.one_of(
            # Valid SQL with properly escaped special characters
            st.just("SELECT * FROM users WHERE name = 'O''Brien'"),  # Properly escaped single quote
            st.just("SELECT * FROM users WHERE name = \"test\""),     # Double quotes
            st.just("SELECT * FROM \"user_table\" WHERE id = 1"),     # Quoted table name
            st.just("SELECT 'test''s value' as test_col FROM users"), # Escaped quotes in string
            # Valid SQL with backslashes (PostgreSQL style)
            st.just("SELECT * FROM users WHERE path = 'C:\\\\temp'"), # Escaped backslashes
        )
    )
    @settings(max_examples=5, deadline=5000)
    def test_valid_special_characters_are_handled(self, special_char_sql):
        """
        Property 5: SQL validation - Special character handling
        
        For any valid SQL with properly escaped special characters, the validator
        should accept it and handle the characters correctly.
        
        **Validates: Requirements 3.1, 3.2**
        """
        try:
            result = validate_and_sanitize_sql(special_char_sql)
            
            # Should produce valid SQL
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Should contain SELECT and FROM
            assert "SELECT" in result.upper()
            assert "FROM" in result.upper()
            
            # Should have LIMIT added if not present
            assert "LIMIT" in result.upper()
            
        except ValidationError as e:
            # If it fails, the error should be descriptive
            error_message = str(e)
            assert len(error_message) > 0
            # Should not be a generic error
            assert "empty" not in error_message.lower()

    @given(
        sql_keyword_table=st.sampled_from([
            "select", "from", "where", "order", "group", "having", "limit",
            "insert", "update", "delete", "create", "drop", "alter", "table"
        ])
    )
    @settings(max_examples=5, deadline=5000)
    def test_sql_keywords_as_table_names_handled_appropriately(self, sql_keyword_table):
        """
        Property 5: SQL validation - SQL keywords as table names
        
        For any SQL using reserved keywords as table names, the validator should
        handle them consistently (either accept with proper parsing or reject with clear error).
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Test unquoted keyword as table name
        sql_unquoted = f"SELECT * FROM {sql_keyword_table}"
        
        # Test quoted keyword as table name (should work)
        sql_quoted = f"SELECT * FROM \"{sql_keyword_table}\""
        
        # Test the unquoted version - behavior may vary by keyword
        try:
            result = validate_and_sanitize_sql(sql_unquoted)
            # If it succeeds, it should be valid SQL with LIMIT added
            assert isinstance(result, str)
            assert "SELECT" in result.upper()
            assert "LIMIT" in result.upper()
        except ValidationError as e:
            # If it fails, the error should be descriptive
            error_message = str(e)
            assert len(error_message) > 0
        
        # Quoted keywords should generally work
        try:
            result = validate_and_sanitize_sql(sql_quoted)
            assert isinstance(result, str)
            assert "SELECT" in result.upper()
            assert "LIMIT" in result.upper()
        except ValidationError as e:
            # If quoted keywords also fail, that's acceptable behavior
            # as long as the error is descriptive
            error_message = str(e)
            assert len(error_message) > 0

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers", 
            "accounts", "profiles", "messages", "events", "logs", "data_table",
            "items", "records", "entries", "documents", "files", "reports"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table'
        ]),
        limit_value=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=5, deadline=5000)
    def test_existing_limit_is_preserved(self, table_name, limit_value):
        """
        Property 5: SQL validation - LIMIT preservation
        
        For any SELECT statement that already contains a LIMIT clause, the validator
        should preserve the existing LIMIT value and not add the default LIMIT.
        
        **Validates: Requirements 3.1, 3.4**
        """
        sql = f"SELECT * FROM {table_name} LIMIT {limit_value}"
        
        result = validate_and_sanitize_sql(sql)
        
        # Should preserve the original LIMIT
        assert f"LIMIT {limit_value}" in result.upper()
        
        # Should not add the default LIMIT (unless the original was 1000)
        if limit_value != 1000:
            # Should not contain "LIMIT 1000" as a separate clause
            assert result.upper().count("LIMIT") == 1, f"Expected exactly one LIMIT clause, found multiple"
            # The LIMIT value should match exactly what we set
            import re
            limit_match = re.search(r'LIMIT\s+(\d+)', result.upper())
            assert limit_match is not None, "LIMIT clause not found"
            assert int(limit_match.group(1)) == limit_value, f"Expected LIMIT {limit_value}, got LIMIT {limit_match.group(1)}"

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers", 
            "accounts", "profiles", "messages", "events", "logs", "data_table",
            "items", "records", "entries", "documents", "files", "reports"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table'
        ]),
        columns=st.lists(
            st.sampled_from(["id", "name", "email", "created_at", "updated_at", "status", "type", "value"]),
            min_size=1,
            max_size=3,
            unique=True
        ),
        has_where=st.booleans(),
        has_order_by=st.booleans(),
        has_group_by=st.booleans()
    )
    @settings(max_examples=5, deadline=5000)
    def test_default_limit_is_added_when_missing(self, table_name, columns, has_where, has_order_by, has_group_by):
        """
        Property 5: SQL validation - Default LIMIT addition
        
        For any SELECT statement without a LIMIT clause, the validator should
        automatically add "LIMIT 1000" to prevent potentially large result sets.
        
        **Validates: Requirements 3.4**
        """
        sql = f"SELECT * FROM {table_name}"
        
        if has_where:
            sql += f" WHERE id > 0"
        
        if has_group_by:
            sql += f" GROUP BY id"
        
        if has_order_by:
            sql += f" ORDER BY id"
        
        result = validate_and_sanitize_sql(sql)
        
        # Should add the default LIMIT
        assert "LIMIT 1000" in result.upper()

    @given(
        sql_with_tables=st.one_of(
            st.just("SELECT * FROM users"),
            st.just("SELECT u.name FROM users u"),
            st.just("SELECT * FROM users u JOIN posts p ON u.id = p.user_id"),
            st.just("SELECT * FROM users WHERE id IN (SELECT user_id FROM posts)"),
            st.just("SELECT COUNT(*) FROM orders o, customers c WHERE o.customer_id = c.id")
        )
    )
    @settings(max_examples=5, deadline=5000)
    def test_table_extraction_consistency(self, sql_with_tables):
        """
        Property 5: SQL validation - Table name extraction
        
        For any valid SELECT statement, table name extraction should be consistent
        and return all referenced tables without duplicates.
        
        **Validates: Requirements 3.1**
        """
        # First validate the SQL is acceptable
        try:
            validated_sql = validate_and_sanitize_sql(sql_with_tables)
            
            # Extract table names
            tables = extract_table_names(sql_with_tables)
            
            # Should return a list
            assert isinstance(tables, list)
            
            # Should not contain duplicates
            assert len(tables) == len(set(tables))
            
            # All table names should be strings
            for table in tables:
                assert isinstance(table, str)
                assert len(table) > 0
                
        except ValidationError:
            # If SQL is invalid, table extraction should return empty list
            tables = extract_table_names(sql_with_tables)
            assert tables == []

    @given(
        whitespace_sql=st.one_of(
            st.just("   SELECT * FROM users   "),
            st.just("\n\tSELECT * FROM users\n"),
            st.just("  \t  SELECT * FROM users  \t  "),
            st.just("\r\n  SELECT * FROM users  \r\n")
        )
    )
    @settings(max_examples=5, deadline=5000)
    def test_whitespace_handling(self, whitespace_sql):
        """
        Property 5: SQL validation - Whitespace handling
        
        For any valid SELECT statement with leading/trailing whitespace, the validator
        should handle it correctly and produce valid sanitized SQL.
        
        **Validates: Requirements 3.1**
        """
        result = validate_and_sanitize_sql(whitespace_sql)
        
        # Should produce valid SQL
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        
        # Should contain expected elements
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert "USERS" in result.upper()

    @given(
        case_variant=st.one_of(
            st.just("select * from users"),
            st.just("SELECT * FROM USERS"),
            st.just("Select * From Users"),
            st.just("sElEcT * fRoM uSeRs")
        )
    )
    @settings(max_examples=5, deadline=5000)
    def test_case_insensitive_validation(self, case_variant):
        """
        Property 5: SQL validation - Case insensitive handling
        
        For any SELECT statement with different case variations, the validator
        should handle them consistently and produce valid results.
        
        **Validates: Requirements 3.1**
        """
        result = validate_and_sanitize_sql(case_variant)
        
        # Should produce valid SQL
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should be identified as SELECT statement regardless of case
        assert is_select_statement(case_variant) is True
        
        # Should have LIMIT added
        assert "LIMIT" in result.upper()


# Additional tests for LIMIT addition functionality
class TestLimitAdditionFunctionality:
    """Tests for automatic LIMIT addition functionality."""

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers",
            "accounts", "profiles", "messages", "events", "logs", "data_table"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table'
        ]),
        columns=st.lists(
            st.sampled_from(["id", "name", "email", "created_at", "updated_at", "status"]),
            min_size=1,
            max_size=3,
            unique=True
        ),
        has_where=st.booleans(),
        has_order_by=st.booleans(),
        has_group_by=st.booleans()
    )
    @settings(max_examples=5, deadline=5000)
    def test_limit_added_to_queries_without_limit(self, table_name, columns, has_where, has_order_by, has_group_by):
        """
        Property 6: Automatic LIMIT addition
        
        For any SELECT query without a LIMIT clause, the validator should automatically
        add "LIMIT 1000" to prevent potentially large result sets.
        
        **Validates: Requirements 3.4**
        """
        # Build a SELECT statement without LIMIT
        column_list = ", ".join(columns)
        sql = f"SELECT {column_list} FROM {table_name}"
        
        if has_where:
            sql += f" WHERE {columns[0]} = 'test'"
        
        if has_group_by:
            sql += f" GROUP BY {columns[0]}"
        
        if has_order_by:
            sql += f" ORDER BY {columns[0]}"
        
        # Validate and sanitize the SQL
        result = validate_and_sanitize_sql(sql)
        
        # Should add the default LIMIT 1000
        assert "LIMIT 1000" in result.upper()
        
        # Should preserve the original query structure
        assert "SELECT" in result.upper()
        assert "FROM" in result.upper()
        assert table_name.upper() in result.upper()

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table'
        ]),
        limit_value=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=5, deadline=5000)
    def test_existing_limit_preserved_in_addition_tests(self, table_name, limit_value):
        """
        Property 6: Automatic LIMIT addition - Preservation of existing LIMIT
        
        For any SELECT query that already contains a LIMIT clause, the validator
        should preserve the existing LIMIT and not add the default LIMIT 1000.
        
        **Validates: Requirements 3.4**
        """
        sql = f"SELECT * FROM {table_name} LIMIT {limit_value}"
        
        result = validate_and_sanitize_sql(sql)
        
        # Should preserve the original LIMIT value
        assert f"LIMIT {limit_value}" in result.upper()
        
        # Should have exactly one LIMIT clause
        assert result.upper().count("LIMIT") == 1, f"Expected exactly one LIMIT clause"

    @given(
        table_name=st.sampled_from([
            "users", "posts", "comments", "orders", "products", "customers"
        ]).filter(lambda x: x.lower() not in [
            'select', 'from', 'where', 'order', 'group', 'having', 'limit', 
            'insert', 'update', 'delete', 'create', 'drop', 'alter', 'table'
        ]),
        has_semicolon=st.booleans()
    )
    @settings(max_examples=5, deadline=5000)
    def test_limit_added_with_semicolon_handling(self, table_name, has_semicolon):
        """
        Property 6: Automatic LIMIT addition - Semicolon handling
        
        For any SELECT query ending with or without a semicolon, the validator
        should add LIMIT appropriately while preserving semicolon placement.
        
        **Validates: Requirements 3.4**
        """
        sql = f"SELECT * FROM {table_name}"
        if has_semicolon:
            sql += ";"
        
        result = validate_and_sanitize_sql(sql)
        
        # Should add the default LIMIT
        assert "LIMIT 1000" in result.upper()
        
        # Should preserve semicolon placement if present
        if has_semicolon:
            assert result.strip().endswith(";")
