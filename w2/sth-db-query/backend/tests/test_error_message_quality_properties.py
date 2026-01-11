"""
Property-based tests for error message quality.

Feature: database-query-tool, Property 24: Error message quality
Validates: Requirements 10.1, 10.2, 10.3, 10.4

Tests that error messages are descriptive, categorized correctly, and provide
helpful information for different types of failures.
"""

import pytest
from hypothesis import given, strategies as st, assume
import asyncpg
from sqlglot.errors import ParseError, TokenError

from app.core.errors import (
    DatabaseQueryError, NetworkError, AuthenticationError, ConfigurationError,
    ValidationError, SQLSyntaxError, PermissionError, TimeoutError, LLMServiceError,
    categorize_asyncpg_error, categorize_sql_error, categorize_timeout_error,
    categorize_llm_error, ErrorCategory, ErrorSeverity
)


class TestErrorMessageQuality:
    """Test error message quality across different error categories."""

    @given(
        error_message=st.text(min_size=1, max_size=200),
        category=st.sampled_from(list(ErrorCategory)),
        severity=st.sampled_from(list(ErrorSeverity))
    )
    def test_database_query_error_has_required_fields(self, error_message, category, severity):
        """
        Property 24a: All DatabaseQueryError instances have required fields.
        
        For any error message, category, and severity, creating a DatabaseQueryError
        should result in an error with all required fields populated.
        """
        error = DatabaseQueryError(
            message=error_message,
            category=category,
            severity=severity
        )
        
        # Check that all required fields are present
        assert error.message == error_message
        assert error.category == category
        assert error.severity == severity
        assert error.code is not None
        assert error.user_message is not None
        assert isinstance(error.suggestions, list)
        assert isinstance(error.context, dict)
        
        # Check that error can be converted to dict
        error_dict = error.to_dict()
        assert "category" in error_dict
        assert "severity" in error_dict
        assert "code" in error_dict
        assert "message" in error_dict
        assert "userMessage" in error_dict
        assert "suggestions" in error_dict
        assert "context" in error_dict

    @given(
        network_errors=st.sampled_from([
            "connection refused",
            "network is unreachable", 
            "timeout",
            "host is unreachable",
            "no route to host",
            "connection timed out"
        ])
    )
    def test_psycopg2_network_error_categorization(self, network_errors):
        """
        Property 24b: Network-related psycopg2 errors are properly categorized.
        
        For any network error message, categorizing it should result in a NetworkError
        with appropriate user message and suggestions.
        """
        # Create a mock psycopg2 error
        mock_error = Exception(f"Database error: {network_errors}")

        categorized = categorize_asyncpg_error(mock_error)
        
        assert isinstance(categorized, NetworkError)
        assert categorized.category == ErrorCategory.NETWORK
        assert categorized.severity == ErrorSeverity.HIGH
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0
        assert "network" in categorized.user_message.lower() or "connect" in categorized.user_message.lower()

    @given(
        auth_errors=st.sampled_from([
            "authentication failed",
            "password authentication failed",
            "role does not exist",
            "invalid authorization"
        ])
    )
    def test_psycopg2_auth_error_categorization(self, auth_errors):
        """
        Property 24c: Authentication-related psycopg2 errors are properly categorized.
        
        For any authentication error message, categorizing it should result in an 
        AuthenticationError with appropriate user message and suggestions.
        """
        mock_error = Exception(f"Database error: {auth_errors}")

        categorized = categorize_asyncpg_error(mock_error)
        
        assert isinstance(categorized, AuthenticationError)
        assert categorized.category == ErrorCategory.AUTHENTICATION
        assert categorized.severity == ErrorSeverity.HIGH
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0
        assert any(word in categorized.user_message.lower() 
                  for word in ["authentication", "password", "username", "login"])

    @given(
        permission_errors=st.sampled_from([
            "permission denied",
            "insufficient privilege",
            "access denied",
            "must be owner",
            "must have"
        ])
    )
    def test_psycopg2_permission_error_categorization(self, permission_errors):
        """
        Property 24d: Permission-related psycopg2 errors are properly categorized.
        
        For any permission error message, categorizing it should result in a 
        PermissionError with appropriate user message and suggestions.
        """
        mock_error = Exception(f"Database error: {permission_errors}")

        categorized = categorize_asyncpg_error(mock_error)
        
        assert isinstance(categorized, PermissionError)
        assert categorized.category == ErrorCategory.PERMISSION
        assert categorized.severity == ErrorSeverity.HIGH
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0
        assert any(word in categorized.user_message.lower() 
                  for word in ["permission", "access", "privilege"])

    @given(
        config_errors=st.sampled_from([
            "database does not exist",
            "relation does not exist",
            "column does not exist",
            "invalid database name"
        ])
    )
    def test_psycopg2_config_error_categorization(self, config_errors):
        """
        Property 24e: Configuration-related psycopg2 errors are properly categorized.
        
        For any configuration error message, categorizing it should result in a 
        ConfigurationError with appropriate user message and suggestions.
        """
        mock_error = Exception(f"Database error: {config_errors}")

        categorized = categorize_asyncpg_error(mock_error)
        
        assert isinstance(categorized, ConfigurationError)
        assert categorized.category == ErrorCategory.CONFIGURATION
        assert categorized.severity == ErrorSeverity.MEDIUM
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0

    @given(
        sql_text=st.text(min_size=1, max_size=100),
        error_msg=st.text(min_size=1, max_size=100)
    )
    def test_sql_syntax_error_categorization(self, sql_text, error_msg):
        """
        Property 24f: SQL syntax errors are properly categorized with context.
        
        For any SQL text and error message, categorizing it should result in a 
        SQLSyntaxError with the SQL included in context.
        """
        # Create a mock ParseError
        mock_error = ParseError(error_msg)
        
        categorized = categorize_sql_error(mock_error, sql_text)
        
        assert isinstance(categorized, SQLSyntaxError)
        assert categorized.category == ErrorCategory.SYNTAX
        assert categorized.severity == ErrorSeverity.MEDIUM
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0
        assert categorized.context["sql"] == sql_text
        assert "sql" in categorized.user_message.lower() or "syntax" in categorized.user_message.lower()

    @given(
        operation=st.text(min_size=1, max_size=50),
        timeout_seconds=st.integers(min_value=1, max_value=300)
    )
    def test_timeout_error_categorization(self, operation, timeout_seconds):
        """
        Property 24g: Timeout errors provide clear information about the operation and timeout.
        
        For any operation and timeout duration, creating a timeout error should result
        in clear messaging about what timed out and suggestions for resolution.
        """
        timeout_error = categorize_timeout_error(operation, timeout_seconds)
        
        assert isinstance(timeout_error, TimeoutError)
        assert timeout_error.category == ErrorCategory.TIMEOUT
        assert timeout_error.severity == ErrorSeverity.HIGH
        assert str(timeout_seconds) in timeout_error.message
        assert operation.lower() in timeout_error.user_message.lower()
        assert len(timeout_error.suggestions) > 0
        assert timeout_error.context["operation"] == operation
        assert timeout_error.context["timeout_seconds"] == timeout_seconds

    @given(
        prompt=st.text(min_size=1, max_size=200),
        error_msg=st.text(min_size=1, max_size=100)
    )
    def test_llm_error_categorization(self, prompt, error_msg):
        """
        Property 24h: LLM service errors are properly categorized with context.
        
        For any prompt and error message, categorizing it should result in an 
        LLMServiceError with the prompt included in context and helpful suggestions.
        """
        mock_error = Exception(error_msg)
        
        categorized = categorize_llm_error(mock_error, prompt)
        
        assert isinstance(categorized, LLMServiceError)
        assert categorized.category == ErrorCategory.LLM_SERVICE
        assert categorized.severity == ErrorSeverity.MEDIUM
        assert len(categorized.user_message) > 0
        assert len(categorized.suggestions) > 0
        assert categorized.context["prompt"] == prompt

    @given(
        api_errors=st.sampled_from([
            "api key invalid",
            "unauthorized access", 
            "401 authentication failed"
        ])
    )
    def test_llm_api_error_categorization(self, api_errors):
        """
        Property 24i: LLM API authentication errors provide specific guidance.
        
        For any API authentication error, the categorized error should provide
        specific guidance about API key configuration.
        """
        mock_error = Exception(api_errors)
        
        categorized = categorize_llm_error(mock_error, "test prompt")
        
        assert isinstance(categorized, LLMServiceError)
        assert "api" in categorized.user_message.lower() or "key" in categorized.user_message.lower()
        assert any("api key" in suggestion.lower() for suggestion in categorized.suggestions)

    @given(
        rate_limit_errors=st.sampled_from([
            "rate limit exceeded",
            "too many requests",
            "429 rate limited"
        ])
    )
    def test_llm_rate_limit_error_categorization(self, rate_limit_errors):
        """
        Property 24j: LLM rate limit errors provide appropriate wait guidance.
        
        For any rate limit error, the categorized error should provide guidance
        about waiting and retrying.
        """
        mock_error = Exception(rate_limit_errors)
        
        categorized = categorize_llm_error(mock_error, "test prompt")
        
        assert isinstance(categorized, LLMServiceError)
        assert "busy" in categorized.user_message.lower() or "wait" in categorized.user_message.lower()
        assert any("wait" in suggestion.lower() for suggestion in categorized.suggestions)

    def test_error_message_descriptiveness(self):
        """
        Property 24k: All error messages are descriptive and non-empty.
        
        Error messages should provide meaningful information to help users
        understand and resolve issues.
        """
        # Test various error types
        errors = [
            NetworkError("Connection failed"),
            AuthenticationError("Login failed"),
            ConfigurationError("Invalid config"),
            ValidationError("Validation failed"),
            SQLSyntaxError("Syntax error", "SELECT * FROM"),
            PermissionError("Access denied"),
            TimeoutError("Operation timed out"),
            LLMServiceError("LLM failed")
        ]
        
        for error in errors:
            # Message should be non-empty and descriptive
            assert len(error.message.strip()) > 0
            assert len(error.user_message.strip()) > 0
            
            # User message should be different from technical message (more user-friendly)
            assert error.user_message != error.message or len(error.message) < 50
            
            # Should have suggestions
            assert len(error.suggestions) > 0
            assert all(len(suggestion.strip()) > 0 for suggestion in error.suggestions)
            
            # Code should be meaningful
            assert len(error.code.strip()) > 0
            assert error.category.value.upper() in error.code

    def test_error_suggestions_quality(self):
        """
        Property 24l: Error suggestions are actionable and relevant.
        
        All error suggestions should provide actionable guidance that users
        can follow to resolve the issue.
        """
        # Test that suggestions contain actionable verbs
        actionable_verbs = [
            "check", "verify", "ensure", "confirm", "try", "use", "contact",
            "refresh", "update", "remove", "add", "configure", "install"
        ]
        
        errors = [
            NetworkError("Connection failed"),
            AuthenticationError("Login failed"),
            ConfigurationError("Invalid config"),
            ValidationError("Validation failed"),
            SQLSyntaxError("Syntax error", "SELECT * FROM"),
            PermissionError("Access denied"),
            TimeoutError("Operation timed out"),
            LLMServiceError("LLM failed")
        ]
        
        for error in errors:
            assert len(error.suggestions) > 0
            
            # At least one suggestion should contain an actionable verb
            has_actionable_suggestion = False
            for suggestion in error.suggestions:
                suggestion_lower = suggestion.lower()
                if any(verb in suggestion_lower for verb in actionable_verbs):
                    has_actionable_suggestion = True
                    break
            
            assert has_actionable_suggestion, f"No actionable suggestions found for {type(error).__name__}: {error.suggestions}"


if __name__ == "__main__":
    pytest.main([__file__])
