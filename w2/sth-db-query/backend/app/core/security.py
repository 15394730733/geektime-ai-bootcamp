"""
SQL validation and security utilities.

This module provides SQL parsing, validation, and security checks using sqlglot.
Ensures only SELECT statements are allowed and automatically adds LIMIT clauses.
"""

import re
from typing import Optional, Tuple
from sqlglot import parse_one, exp
from sqlglot.errors import ParseError, TokenError

from ..core.config import settings
from ..core.errors import SQLSyntaxError, ValidationError, categorize_sql_error


def validate_and_sanitize_sql(sql: str) -> str:
    """
    Validate SQL query and ensure it meets security requirements.

    Args:
        sql: The SQL query string to validate

    Returns:
        Sanitized SQL query with LIMIT added if needed

    Raises:
        SQLSyntaxError: If SQL syntax is invalid
        ValidationError: If validation fails for security reasons
    """
    if not sql or not sql.strip():
        raise ValidationError(
            message="SQL query cannot be empty",
            user_message="Please enter a SQL query to execute.",
            suggestions=["Enter a valid SELECT statement"]
        )

    sql = sql.strip()

    # Parse the SQL to validate syntax and structure
    try:
        parsed = parse_one(sql, dialect="postgres")
    except (ParseError, TokenError) as e:
        raise categorize_sql_error(e, sql)

    # Check if it's a SELECT statement
    if not isinstance(parsed, exp.Select):
        raise ValidationError(
            message="Only SELECT statements are allowed",
            user_message="Only SELECT queries are permitted for security reasons.",
            suggestions=[
                "Use SELECT statements to query data",
                "Remove any INSERT, UPDATE, DELETE, or DDL statements",
                "Contact an administrator for data modification requests"
            ],
            context={"sql": sql, "statement_type": type(parsed).__name__}
        )

    # Check for potentially dangerous operations
    _check_for_dangerous_operations(parsed, sql)

    # Add LIMIT if not present and not already limited
    sql = _add_limit_if_needed(sql, parsed)

    return sql


def _check_for_dangerous_operations(parsed_sql: exp.Expression, sql: str) -> None:
    """
    Check for potentially dangerous SQL operations.

    Args:
        parsed_sql: Parsed SQL expression
        sql: Original SQL string

    Raises:
        ValidationError: If dangerous operations are found
    """
    dangerous_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'BULK'
    ]

    sql_upper = str(parsed_sql).upper()

    for keyword in dangerous_keywords:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            raise ValidationError(
                message=f"Statement contains forbidden keyword: {keyword}",
                user_message=f"The '{keyword}' operation is not allowed for security reasons.",
                suggestions=[
                    "Use SELECT statements to query data only",
                    "Contact an administrator for data modification requests",
                    "Remove any data modification or schema change operations"
                ],
                context={"sql": sql, "forbidden_keyword": keyword}
            )


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
