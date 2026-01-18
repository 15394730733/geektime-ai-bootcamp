"""
Comprehensive error handling and categorization system.

This module provides structured error handling with categorization,
descriptive messaging, and proper HTTP status code mapping.
"""

import re
from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
import asyncpg
from sqlglot.errors import ParseError, TokenError


class ErrorCategory(str, Enum):
    """Error categories for better error handling and user feedback."""
    
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    SYNTAX = "syntax"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    LLM_SERVICE = "llm_service"
    INTERNAL = "internal"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorDetail(BaseModel):
    """Detailed error information with categorization."""
    
    category: ErrorCategory
    severity: ErrorSeverity
    code: str
    message: str
    user_message: str
    technical_details: Optional[str] = None
    suggestions: Optional[list[str]] = None
    context: Optional[Dict[str, Any]] = None


class DatabaseQueryError(Exception):
    """Base exception for database query tool errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        code: Optional[str] = None,
        user_message: Optional[str] = None,
        technical_details: Optional[str] = None,
        suggestions: Optional[list[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.code = code or self._generate_error_code()
        self.user_message = user_message or self._generate_user_message()
        self.technical_details = technical_details
        self.suggestions = suggestions or []
        self.context = context or {}
        super().__init__(message)
    
    def _generate_error_code(self) -> str:
        """Generate error code based on category."""
        return f"{self.category.value.upper()}_ERROR"
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly message."""
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "userMessage": self.user_message,
            "technicalDetails": self.technical_details,
            "suggestions": self.suggestions,
            "context": self.context
        }


class NetworkError(DatabaseQueryError):
    """Network-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Check your network connection",
                "Verify the database server is running",
                "Confirm the database host and port are correct"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthenticationError(DatabaseQueryError):
    """Authentication-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Verify your username and password are correct",
                "Check if the user account exists in the database",
                "Ensure the user has login permissions"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ConfigurationError(DatabaseQueryError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Check your configuration settings",
                "Verify the database connection parameters",
                "Ensure all required fields are provided"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ValidationError(DatabaseQueryError):
    """Validation-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Check your input for errors",
                "Ensure all required fields are provided",
                "Verify the format of your input"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class SQLSyntaxError(DatabaseQueryError):
    """SQL syntax-related errors."""
    
    def __init__(self, message: str, sql: str = "", **kwargs):
        # Set context with SQL before calling parent constructor
        context = kwargs.get('context', {})
        context['sql'] = sql
        kwargs['context'] = context
        
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Check your SQL syntax for errors",
                "Ensure all keywords are spelled correctly",
                "Verify proper use of quotes and parentheses"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class PermissionError(DatabaseQueryError):
    """Permission-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Contact your database administrator for access",
                "Verify you have the required permissions",
                "Check if you're connecting to the correct database"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class TimeoutError(DatabaseQueryError):
    """Timeout-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Try a simpler query or add more specific filters",
                "Check if the database server is under heavy load",
                "Consider increasing the timeout limit if appropriate"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ResourceError(DatabaseQueryError):
    """Resource-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Try reducing the scope of your query",
                "Check available system resources",
                "Contact support if the issue persists"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class LLMServiceError(DatabaseQueryError):
    """LLM service-related errors."""
    
    def __init__(self, message: str, **kwargs):
        # Provide default suggestions if none given
        if 'suggestions' not in kwargs:
            kwargs['suggestions'] = [
                "Try rephrasing your question more clearly",
                "Use direct SQL input as an alternative",
                "Contact support if the issue persists"
            ]
        
        super().__init__(
            message=message,
            category=ErrorCategory.LLM_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


def categorize_asyncpg_error(error: asyncpg.PostgresError) -> DatabaseQueryError:
    """Categorize asyncpg errors into appropriate error types."""

    error_msg = str(error).lower()

    # Network errors
    if any(keyword in error_msg for keyword in [
        'connection refused', 'network is unreachable', 'timeout',
        'host is unreachable', 'no route to host', 'connection timed out',
        'broken pipe', 'connection reset'
    ]):
        return NetworkError(
            message=f"Database connection failed: {str(error)}",
            user_message="Unable to connect to the database. Please check your network connection and database server status.",
            suggestions=[
                "Verify the database server is running",
                "Check your network connection",
                "Confirm the database host and port are correct",
                "Check firewall settings"
            ],
            technical_details=str(error)
        )

    # Authentication errors
    if any(keyword in error_msg for keyword in [
        'authentication failed', 'password authentication failed',
        'role does not exist', 'invalid authorization', 'password error'
    ]):
        return AuthenticationError(
            message=f"Database authentication failed: {str(error)}",
            user_message="Authentication failed. Please check your username and password.",
            suggestions=[
                "Verify your username and password are correct",
                "Check if the user account exists in the database",
                "Ensure the user has login permissions"
            ],
            technical_details=str(error)
        )

    # Permission errors
    if any(keyword in error_msg for keyword in [
        'permission denied', 'insufficient privilege', 'access denied',
        'must be owner', 'must have', 'privilege'
    ]):
        return PermissionError(
            message=f"Database permission denied: {str(error)}",
            user_message="You don't have sufficient permissions to perform this operation.",
            suggestions=[
                "Contact your database administrator for access",
                "Verify you have the required permissions",
                "Check if you're connecting to the correct database"
            ],
            technical_details=str(error)
        )

    # Configuration errors
    if any(keyword in error_msg for keyword in [
        'database does not exist', 'relation does not exist',
        'column does not exist', 'invalid database name', 'table does not exist'
    ]):
        return ConfigurationError(
            message=f"Database configuration error: {str(error)}",
            user_message="The requested database, table, or column was not found.",
            suggestions=[
                "Verify the database name is correct",
                "Check if the table or column exists",
                "Refresh the database metadata"
            ],
            technical_details=str(error)
        )

    # Default to internal error
    return DatabaseQueryError(
        message=f"Database operation failed: {str(error)}",
        category=ErrorCategory.INTERNAL,
        user_message="An unexpected database error occurred. Please try again or contact support.",
        technical_details=str(error)
    )


def categorize_psycopg2_error(error) -> DatabaseQueryError:
    """Legacy wrapper for psycopg2 errors - redirects to asyncpg error categorization."""
    return categorize_asyncpg_error(error)


def categorize_sql_error(error: Union[ParseError, TokenError], sql: str = "") -> SQLSyntaxError:
    """Categorize SQL parsing errors with specific syntax highlighting."""
    
    error_msg = str(error)
    
    # Extract line and column information if available
    line_info = ""
    column_info = ""
    
    # Try to extract position information from sqlglot errors
    if hasattr(error, 'line') and error.line:
        line_info = f" at line {error.line}"
    if hasattr(error, 'col') and error.col:
        column_info = f", column {error.col}"
    
    position_info = f"{line_info}{column_info}" if line_info or column_info else ""
    
    # Common SQL syntax error patterns
    suggestions = []
    user_message = "SQL syntax error detected."
    
    if "unexpected token" in error_msg.lower():
        suggestions.extend([
            "Check for missing or extra commas, parentheses, or quotes",
            "Verify all keywords are spelled correctly",
            "Ensure proper spacing between SQL elements"
        ])
        user_message = f"Unexpected SQL token found{position_info}."
    
    elif "expected" in error_msg.lower():
        suggestions.extend([
            "Check for missing required SQL elements",
            "Verify the SQL statement structure is correct",
            "Ensure all opened parentheses are closed"
        ])
        user_message = f"Missing required SQL element{position_info}."
    
    elif "unterminated" in error_msg.lower():
        suggestions.extend([
            "Check for unclosed quotes or parentheses",
            "Ensure all string literals are properly terminated",
            "Verify comment blocks are properly closed"
        ])
        user_message = f"Unterminated SQL element{position_info}."
    
    else:
        suggestions.extend([
            "Review the SQL syntax documentation",
            "Check for typos in SQL keywords",
            "Verify the query structure is valid"
        ])
    
    return SQLSyntaxError(
        message=f"SQL syntax error: {error_msg}",
        sql=sql,
        user_message=user_message,
        suggestions=suggestions,
        technical_details=error_msg,
        context={
            "sql": sql,
            "position": position_info,
            "error_type": type(error).__name__
        }
    )


def categorize_timeout_error(operation: str, timeout_seconds: int) -> TimeoutError:
    """Create a categorized timeout error."""
    
    return TimeoutError(
        message=f"{operation} timed out after {timeout_seconds} seconds",
        user_message=f"The {operation.lower()} operation took too long and was cancelled.",
        suggestions=[
            "Try a simpler query or add more specific filters",
            "Check if the database server is under heavy load",
            "Consider increasing the timeout limit if appropriate",
            "Verify the query is optimized and uses proper indexes"
        ],
        context={
            "operation": operation,
            "timeout_seconds": timeout_seconds
        }
    )


def categorize_llm_error(error: Exception, prompt: str = "") -> LLMServiceError:
    """Categorize LLM service errors."""
    
    error_msg = str(error).lower()
    
    # API-related errors
    if any(keyword in error_msg for keyword in [
        'api key', 'unauthorized', '401', 'authentication'
    ]):
        return LLMServiceError(
            message=f"LLM API authentication failed: {str(error)}",
            user_message="Unable to authenticate with the AI service. Please check the API configuration.",
            suggestions=[
                "Verify the OpenAI API key is configured correctly",
                "Check if the API key has sufficient permissions",
                "Ensure the API key hasn't expired"
            ],
            technical_details=str(error),
            context={"prompt": prompt}
        )
    
    # Rate limiting
    if any(keyword in error_msg for keyword in [
        'rate limit', 'too many requests', '429'
    ]):
        return LLMServiceError(
            message=f"LLM API rate limit exceeded: {str(error)}",
            user_message="The AI service is currently busy. Please wait a moment and try again.",
            suggestions=[
                "Wait a few seconds before retrying",
                "Try simplifying your request",
                "Contact support if the issue persists"
            ],
            technical_details=str(error),
            context={"prompt": prompt}
        )
    
    # Service unavailable
    if any(keyword in error_msg for keyword in [
        'service unavailable', '503', 'server error', '500'
    ]):
        return LLMServiceError(
            message=f"LLM service unavailable: {str(error)}",
            user_message="The AI service is temporarily unavailable. Please try again later.",
            suggestions=[
                "Wait a few minutes and try again",
                "Check the service status page",
                "Use direct SQL input as an alternative"
            ],
            technical_details=str(error),
            context={"prompt": prompt}
        )
    
    # Default LLM error
    return LLMServiceError(
        message=f"LLM processing failed: {str(error)}",
        user_message="Unable to process your natural language query. Please try rephrasing or use direct SQL.",
        suggestions=[
            "Try rephrasing your question more clearly",
            "Use more specific terms related to your database",
            "Switch to direct SQL input for complex queries"
        ],
        technical_details=str(error),
        context={"prompt": prompt}
    )


# HTTP Status Code mappings for error categories
ERROR_HTTP_STATUS_CODES = {
    ErrorCategory.NETWORK: 503,
    ErrorCategory.AUTHENTICATION: 401,
    ErrorCategory.CONFIGURATION: 400,
    ErrorCategory.VALIDATION: 400,
    ErrorCategory.SYNTAX: 400,
    ErrorCategory.PERMISSION: 403,
    ErrorCategory.TIMEOUT: 408,
    ErrorCategory.RESOURCE: 507,
    ErrorCategory.LLM_SERVICE: 502,
    ErrorCategory.INTERNAL: 500,
}


def get_http_status_code(error: DatabaseQueryError) -> int:
    """Get appropriate HTTP status code for an error."""
    return ERROR_HTTP_STATUS_CODES.get(error.category, 500)