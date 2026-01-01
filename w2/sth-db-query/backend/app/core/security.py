"""
SQL validation and security utilities.

This module provides SQL parsing, validation, and security checks using sqlglot.
Ensures only SELECT statements are allowed and automatically adds LIMIT clauses.
"""

import re
from typing import Optional, Tuple
from sqlglot import parse_one, exp
from sqlglot.errors import ParseError

from ..core.config import settings


class SQLValidationError(Exception):
    """Exception raised when SQL validation fails."""

    def __init__(self, message: str, sql: str = ""):
        self.message = message
        self.sql = sql
        super().__init__(f"{message}: {sql}")


def validate_and_sanitize_sql(sql: str) -> str:
    """
    Validate SQL query and ensure it meets security requirements.

    Args:
        sql: The SQL query string to validate

    Returns:
        Sanitized SQL query with LIMIT added if needed

    Raises:
        SQLValidationError: If validation fails
    """
    if not sql or not sql.strip():
        raise SQLValidationError("SQL query cannot be empty")

    sql = sql.strip()

    # Parse the SQL to validate syntax and structure
    try:
        parsed = parse_one(sql, dialect="postgres")
    except ParseError as e:
        raise SQLValidationError(f"Invalid SQL syntax: {str(e)}", sql)

    # Check if it's a SELECT statement
    if not isinstance(parsed, exp.Select):
        raise SQLValidationError("Only SELECT statements are allowed", sql)

    # Check for potentially dangerous operations
    _check_for_dangerous_operations(parsed)

    # Add LIMIT if not present and not already limited
    sql = _add_limit_if_needed(sql, parsed)

    return sql


def _check_for_dangerous_operations(parsed_sql: exp.Expression) -> None:
    """
    Check for potentially dangerous SQL operations.

    Args:
        parsed_sql: Parsed SQL expression

    Raises:
        SQLValidationError: If dangerous operations are found
    """
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'BULK'
    ]

    sql_upper = str(parsed_sql).upper()

    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            raise SQLValidationError(f"Statement contains forbidden keyword: {keyword}")


def _add_limit_if_needed(sql: str, parsed_sql: exp.Select) -> str:
    """
    Add LIMIT clause if not present and result might be large.

    Args:
        sql: Original SQL string
        parsed_sql: Parsed SQL expression

    Returns:
        SQL with LIMIT clause added if needed
    """
    # Check if LIMIT is already present
    if parsed_sql.find(exp.Limit):
        return sql

    # Check if it's a simple SELECT without aggregation that might return many rows
    # Add LIMIT for safety
    limit_clause = f" LIMIT {settings.max_query_results}"

    # If the SQL ends with a semicolon, insert LIMIT before it
    if sql.rstrip().endswith(';'):
        sql = sql.rstrip()[:-1] + limit_clause + ';'
    else:
        sql = sql + limit_clause

    return sql


def extract_table_names(sql: str) -> list[str]:
    """
    Extract table names referenced in the SQL query.

    Args:
        sql: SQL query string

    Returns:
        List of table names found in the query
    """
    try:
        parsed = parse_one(sql, dialect="postgres")
        tables = []

        # Find all table references
        for table in parsed.find_all(exp.Table):
            if table.name:
                tables.append(table.name)

        return list(set(tables))  # Remove duplicates
    except (ParseError, AttributeError):
        return []


def is_select_statement(sql: str) -> bool:
    """
    Check if the SQL is a SELECT statement.

    Args:
        sql: SQL query string

    Returns:
        True if it's a SELECT statement, False otherwise
    """
    try:
        parsed = parse_one(sql, dialect="postgres")
        return isinstance(parsed, exp.Select)
    except ParseError:
        return False


def validate_sql_syntax(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SQL syntax without security checks.

    Args:
        sql: SQL query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parse_one(sql, dialect="postgres")
        return True, None
    except ParseError as e:
        return False, str(e)
