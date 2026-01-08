"""
Property-based tests for query execution error handling.

Feature: database-query-tool, Property 8: Query execution error handling
**Validates: Requirements 3.6**
"""

from hypothesis import given, strategies as st, settings
import pytest
from unittest.mock import MagicMock, patch
import asyncio
import psycopg2

from app.services.query import QueryService, QueryExecutionError
from app.core.errors import ValidationError, SQLSyntaxError


class TestQueryExecutionProperties:
    """Property-based tests for query execution error handling."""

    @given(
        error_type=st.sampled_from([
            "OperationalError",
            "ProgrammingError", 
            "DataError",
            "IntegrityError",
            "InternalError",
            "InterfaceError",
            "GenericError"
        ]),
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha()),
        sql_query=st.just("SELECT * FROM users")
    )
    @settings(max_examples=5, deadline=5000)
    def test_database_errors_are_handled_gracefully(self, error_type, database_name, sql_query):
        """
        Property 8: Query execution error handling
        
        For any database error that occurs during query execution, the system should
        handle it gracefully and return a descriptive QueryExecutionError without crashing.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        # Create appropriate error based on type
        error_map = {
            "OperationalError": psycopg2.OperationalError("Connection failed"),
            "ProgrammingError": psycopg2.ProgrammingError("Syntax error in query"),
            "DataError": psycopg2.DataError("Invalid data type"),
            "IntegrityError": psycopg2.IntegrityError("Constraint violation"),
            "InternalError": psycopg2.InternalError("Internal database error"),
            "InterfaceError": psycopg2.InterfaceError("Interface error"),
            "GenericError": Exception("Generic database error")
        }
        
        error_instance = error_map[error_type]
        
        # Mock the database session and database service
        mock_db = MagicMock()
        mock_database_conn = MagicMock()
        mock_database_conn.url = "postgresql://user:pass@localhost:5432/testdb"
        
        async def run_test():
            with patch.object(query_service.database_service, 'get_database', return_value=mock_database_conn):
                with patch.object(query_service, '_execute_with_timeout', side_effect=error_instance):
                    
                    # The service should handle the error gracefully
                    with pytest.raises(QueryExecutionError) as exc_info:
                        await query_service.execute_query(mock_db, database_name, sql_query)
                    
                    # Should provide a descriptive error message
                    error = exc_info.value
                    assert isinstance(error.message, str)
                    assert len(error.message) > 0
                    
                    # Should include error details
                    assert hasattr(error, 'details')
                    assert isinstance(error.details, dict)
                    
                    # Should categorize the error type
                    if isinstance(error_instance, psycopg2.Error):
                        assert error.details.get('type') == 'database_error'
                    elif isinstance(error_instance, asyncio.TimeoutError):
                        assert error.details.get('type') == 'timeout_error'
                    else:
                        assert error.details.get('type') == 'execution_error'
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        invalid_sql=st.one_of(
            st.just("INSERT INTO users VALUES (1)"),
            st.just("UPDATE users SET name = 'test'"),
            st.just("DELETE FROM users"),
            st.just("DROP TABLE users"),
            st.just("INVALID SQL SYNTAX"),
            st.just("SELECT * FRM users"),  # Typo
            st.just("")  # Empty string
        ),
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha())
    )
    @settings(max_examples=5, deadline=5000)
    def test_sql_validation_errors_are_handled(self, invalid_sql, database_name):
        """
        Property 8: Query execution error handling - SQL validation errors
        
        For any invalid SQL that fails validation, the system should handle the
        validation error gracefully and return a QueryExecutionError with validation details.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock the database session
            mock_db = MagicMock()
            
            # The service should handle validation errors gracefully
            with pytest.raises(QueryExecutionError) as exc_info:
                await query_service.execute_query(mock_db, database_name, invalid_sql)
            
            # Should provide a descriptive error message about validation
            error = exc_info.value
            assert "validation" in error.message.lower()
            
            # Should include validation error details
            assert error.details.get('type') == 'validation_error'
            assert 'sql' in error.details
            assert error.details['sql'] == invalid_sql
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha()),
        sql_query=st.just("SELECT * FROM users")
    )
    @settings(max_examples=5, deadline=5000)
    def test_timeout_errors_are_handled(self, database_name, sql_query):
        """
        Property 8: Query execution error handling - Timeout handling
        
        For any query that times out during execution, the system should handle the
        timeout gracefully and return a QueryExecutionError with timeout details.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock the database session and database service
            mock_db = MagicMock()
            mock_database_conn = MagicMock()
            mock_database_conn.url = "postgresql://user:pass@localhost:5432/testdb"
            
            with patch.object(query_service.database_service, 'get_database', return_value=mock_database_conn):
                with patch.object(query_service, '_execute_with_timeout', side_effect=asyncio.TimeoutError()):
                    
                    # The service should handle timeout errors gracefully
                    with pytest.raises(QueryExecutionError) as exc_info:
                        await query_service.execute_query(mock_db, database_name, sql_query)
                    
                    # Should provide a descriptive timeout error message
                    error = exc_info.value
                    assert "timed out" in error.message.lower() or "timeout" in error.message.lower()
                    
                    # Should include timeout error details
                    assert error.details.get('type') == 'timeout_error'
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        nonexistent_database=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha()),
        sql_query=st.just("SELECT * FROM users")
    )
    @settings(max_examples=5, deadline=5000)
    def test_nonexistent_database_errors_are_handled(self, nonexistent_database, sql_query):
        """
        Property 8: Query execution error handling - Database not found
        
        For any query against a non-existent database connection, the system should
        handle the error gracefully and return a descriptive QueryExecutionError.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock the database session to return None (database not found)
            mock_db = MagicMock()
            
            with patch.object(query_service.database_service, 'get_database', return_value=None):
                
                # The service should handle missing database gracefully
                with pytest.raises(QueryExecutionError) as exc_info:
                    await query_service.execute_query(mock_db, nonexistent_database, sql_query)
                
                # Should provide a descriptive error message about missing database
                error = exc_info.value
                assert "not found" in error.message.lower()
                assert nonexistent_database in error.message
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        connection_error_type=st.sampled_from([
            "could not connect to server",
            "connection refused", 
            "timeout expired",
            "authentication failed",
            "database does not exist"
        ]),
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha()),
        sql_query=st.just("SELECT * FROM users")
    )
    @settings(max_examples=5, deadline=5000)
    def test_connection_errors_are_categorized_correctly(self, connection_error_type, database_name, sql_query):
        """
        Property 8: Query execution error handling - Connection error categorization
        
        For any connection-related database error, the system should categorize it
        correctly and provide appropriate error details for troubleshooting.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock the database session and database service
            mock_db = MagicMock()
            mock_database_conn = MagicMock()
            mock_database_conn.url = "postgresql://user:pass@localhost:5432/testdb"
            
            connection_error = psycopg2.OperationalError(connection_error_type)
            
            with patch.object(query_service.database_service, 'get_database', return_value=mock_database_conn):
                with patch.object(query_service, '_execute_with_timeout', side_effect=connection_error):
                    
                    # The service should handle connection errors gracefully
                    with pytest.raises(QueryExecutionError) as exc_info:
                        await query_service.execute_query(mock_db, database_name, sql_query)
                    
                    # Should categorize as database error
                    error = exc_info.value
                    assert error.details.get('type') == 'database_error'
                    
                    # Should preserve the original error message for debugging
                    assert 'error' in error.details
                    assert connection_error_type in str(error.details['error'])
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        valid_sql=st.sampled_from([
            "SELECT * FROM users",
            "SELECT id, name FROM users WHERE active = true",
            "SELECT COUNT(*) FROM users",
            "SELECT * FROM users ORDER BY created_at DESC"
        ]),
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha())
    )
    @settings(max_examples=5, deadline=5000)
    def test_successful_queries_return_formatted_results(self, valid_sql, database_name):
        """
        Property 8: Query execution error handling - Successful execution
        
        For any valid SQL query that executes successfully, the system should
        return properly formatted results without raising errors.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock successful query execution
            mock_db = MagicMock()
            mock_database_conn = MagicMock()
            mock_database_conn.url = "postgresql://user:pass@localhost:5432/testdb"
            
            mock_result = {
                "columns": ["id", "name"],
                "rows": [{"id": 1, "name": "test"}],
                "row_count": 1,
                "execution_time_ms": 100,
                "query": valid_sql
            }
            
            with patch.object(query_service.database_service, 'get_database', return_value=mock_database_conn):
                with patch.object(query_service, '_execute_with_timeout', return_value=mock_result):
                    
                    # Should execute successfully without raising errors
                    result = await query_service.execute_query(mock_db, database_name, valid_sql)
                    
                    # Should return formatted results
                    assert isinstance(result, dict)
                    assert 'columns' in result
                    assert 'rows' in result
                    assert 'rowCount' in result  # camelCase formatting
                    assert 'executionTime' in result  # camelCase formatting
                    assert 'query' in result
                    
                    # Should preserve data integrity
                    assert result['rowCount'] == mock_result['row_count']
                    assert result['executionTime'] == mock_result['execution_time_ms']
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        error_message=st.text(min_size=1, max_size=50),
        database_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
            min_size=1,
            max_size=20
        ).filter(lambda x: x.isalpha()),
        sql_query=st.just("SELECT * FROM users")
    )
    @settings(max_examples=5, deadline=5000)
    def test_error_messages_are_descriptive_and_safe(self, error_message, database_name, sql_query):
        """
        Property 8: Query execution error handling - Error message safety
        
        For any error that occurs during query execution, the error messages should
        be descriptive for debugging but not expose sensitive information.
        
        **Validates: Requirements 3.6**
        """
        query_service = QueryService()
        
        async def run_test():
            # Mock the database session and database service
            mock_db = MagicMock()
            mock_database_conn = MagicMock()
            mock_database_conn.url = "postgresql://user:pass@localhost:5432/testdb"
            
            custom_error = Exception(error_message)
            
            with patch.object(query_service.database_service, 'get_database', return_value=mock_database_conn):
                with patch.object(query_service, '_execute_with_timeout', side_effect=custom_error):
                    
                    # The service should handle the error gracefully
                    with pytest.raises(QueryExecutionError) as exc_info:
                        await query_service.execute_query(mock_db, database_name, sql_query)
                    
                    # Error message should be a string
                    error = exc_info.value
                    assert isinstance(error.message, str)
                    assert len(error.message) > 0
                    
                    # Should not expose sensitive connection details in the main message
                    assert "password" not in error.message.lower()
                    assert "pass@" not in error.message.lower()
                    
                    # Should include the SQL query in details for debugging
                    assert error.details.get('sql') == sql_query
        
        # Run the async test
        asyncio.run(run_test())
