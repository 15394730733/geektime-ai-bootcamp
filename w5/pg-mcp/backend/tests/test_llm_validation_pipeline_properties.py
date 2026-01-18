"""
Property-based tests for LLM validation pipeline.

Feature: database-query-tool, Property 10: LLM-generated query validation
"""

import pytest
from hypothesis import given, strategies as st, settings
import sqlglot
from app.services.llm import LLMService


class TestLLMValidationPipelineProperties:
    """Property-based tests for LLM validation pipeline functionality."""

    def test_simple_validation_test(self):
        """Simple test to verify the test framework is working."""
        service = LLMService()
        assert service is not None

    def test_direct_validation_method(self):
        """Test the direct validate_generated_sql method."""
        service = LLMService()
        
        # Test valid SQL
        valid_sql = "SELECT * FROM users"
        try:
            result = service.validate_generated_sql(valid_sql)
            assert result is not None
            assert len(result.strip()) > 0
            assert "LIMIT" in result.upper()  # Should add LIMIT
        except Exception as e:
            pytest.fail(f"Valid SQL should not fail validation: {e}")
        
        # Test invalid SQL
        invalid_sql = "DROP TABLE users"
        try:
            service.validate_generated_sql(invalid_sql)
            pytest.fail("Invalid SQL should fail validation")
        except Exception as e:
            assert "validation failed" in str(e).lower() or "forbidden" in str(e).lower()

    @given(st.sampled_from([
        "SELECT * FROM users", 
        "SELECT id, name FROM products", 
        "SELECT COUNT(*) FROM orders",
        "SELECT u.id, u.name FROM users u",
        "SELECT * FROM customers WHERE active = true"
    ]))
    @settings(max_examples=5, deadline=None)
    def test_property_10_valid_sql_validation(self, valid_sql):
        """
        Property 10: LLM-generated query validation (valid SQL case)
        
        For any valid SQL, the validation pipeline should return sanitized SQL.
        
        **Validates: Requirements 4.3**
        """
        service = LLMService()
        
        try:
            result = service.validate_generated_sql(valid_sql)
            
            # Property 1: Result should not be empty
            assert result is not None
            assert len(result.strip()) > 0
            
            # Property 2: Result should be syntactically valid
            parsed = sqlglot.parse_one(result, dialect="postgres")
            assert parsed is not None
            
            # Property 3: Result should be a SELECT statement
            assert isinstance(parsed, sqlglot.expressions.Select)
            
            # Property 4: Result should have LIMIT added if not present
            if "LIMIT" not in valid_sql.upper():
                assert "LIMIT" in result.upper()
                
        except Exception as e:
            pytest.fail(f"Valid SQL failed validation: {valid_sql}. Error: {e}")

    @given(st.sampled_from([
        "DROP TABLE users", 
        "INSERT INTO users VALUES (1)", 
        "UPDATE users SET name='test'", 
        "DELETE FROM users",
        "CREATE TABLE test (id INT)",
        "ALTER TABLE users ADD COLUMN test VARCHAR(50)",
        "TRUNCATE TABLE users"
    ]))
    @settings(max_examples=5, deadline=None)
    def test_property_10_invalid_sql_validation(self, invalid_sql):
        """
        Property 10: LLM-generated query validation (invalid SQL case)
        
        For any invalid/dangerous SQL, the validation pipeline should reject it.
        
        **Validates: Requirements 4.3**
        """
        service = LLMService()
        
        try:
            service.validate_generated_sql(invalid_sql)
            pytest.fail(f"Dangerous SQL should not pass validation: {invalid_sql}")
        except Exception as e:
            # Invalid SQL should cause validation errors
            error_msg = str(e).lower()
            
            # Property 1: Error message should be descriptive
            assert len(error_msg) > 0
            
            # Property 2: Error message should indicate validation failure
            assert any(keyword in error_msg for keyword in [
                "validation", "invalid", "error", "syntax", "forbidden", "not allowed"
            ])

    def test_empty_and_whitespace_sql_handling(self):
        """Test handling of empty and whitespace-only SQL."""
        service = LLMService()
        
        # Test empty SQL
        try:
            service.validate_generated_sql("")
            pytest.fail("Empty SQL should fail validation")
        except Exception as e:
            assert "empty" in str(e).lower() or "validation failed" in str(e).lower()
        
        # Test whitespace-only SQL
        try:
            service.validate_generated_sql("   \n\t   ")
            pytest.fail("Whitespace-only SQL should fail validation")
        except Exception as e:
            assert "empty" in str(e).lower() or "validation failed" in str(e).lower()

    def test_sql_cleaning_and_validation_integration(self):
        """Test that SQL cleaning works with validation."""
        service = LLMService()
        
        # Test SQL with markdown formatting
        markdown_sql = "```sql\nSELECT * FROM users\n```"
        cleaned_sql = service._clean_sql_response(markdown_sql)
        
        # Should clean the SQL
        assert "```" not in cleaned_sql
        assert cleaned_sql.strip() == "SELECT * FROM users"
        
        # Cleaned SQL should validate successfully
        try:
            result = service.validate_generated_sql(cleaned_sql)
            assert result is not None
            assert "SELECT" in result.upper()
        except Exception as e:
            pytest.fail(f"Cleaned SQL should validate successfully: {e}")

    @given(st.sampled_from([
        "SELCT * FROM users",  # Typo
        "SELECT * FORM users",  # Typo
        "SELECT * FROM users WHERE",  # Incomplete WHERE
        "SELECT * FROM users WHERE id =",  # Incomplete condition
        "",  # Empty
        "   ",  # Whitespace only
    ]))
    @settings(max_examples=5, deadline=None)
    def test_property_10_syntax_error_validation(self, invalid_sql):
        """
        Property 10: LLM-generated query validation (syntax error case)
        
        For any syntactically invalid SQL, the validation pipeline should reject it.
        
        **Validates: Requirements 4.3**
        """
        service = LLMService()
        
        try:
            service.validate_generated_sql(invalid_sql)
            # If we get here without exception, the SQL somehow passed validation
            # This should not happen for syntactically invalid SQL
            if invalid_sql.strip() == "":
                pytest.fail("Empty SQL should not pass validation")
            elif "SELCT" in invalid_sql or "FORM" in invalid_sql:
                pytest.fail(f"Syntactically invalid SQL should not pass validation: {invalid_sql}")
            elif invalid_sql.endswith("WHERE") or invalid_sql.endswith("="):
                pytest.fail(f"Incomplete SQL should not pass validation: {invalid_sql}")
        except Exception as e:
            # Invalid SQL should cause validation errors
            error_msg = str(e).lower()
            
            # Property 1: Error message should be descriptive
            assert len(error_msg) > 0
            
            # Property 2: Error message should indicate validation failure
            assert any(keyword in error_msg for keyword in [
                "validation", "invalid", "error", "syntax", "empty", "cannot"
            ])
