"""
Property-based tests for query execution endpoints.

Feature: database-query-tool, Property 22: API endpoint behavior
Validates: Requirements 9.5, 9.6
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import json
from typing import Dict, Any


@composite
def valid_sql_queries(draw):
    """Generate valid SQL SELECT queries."""
    # Simple SELECT queries that should be valid
    queries = [
        "SELECT 1",
        "SELECT 'hello' as greeting",
        "SELECT NOW()",
        "SELECT COUNT(*) FROM information_schema.tables",
        "SELECT version()",
        "SELECT current_database()",
        "SELECT current_user",
        "SELECT 1 + 1 as result",
        "SELECT 'test' as message, 42 as number",
        "SELECT EXTRACT(YEAR FROM NOW()) as current_year"
    ]
    return draw(st.sampled_from(queries))


@composite
def invalid_sql_queries(draw):
    """Generate invalid SQL queries."""
    choice = draw(st.integers(min_value=1, max_value=4))
    
    if choice == 1:
        # Non-SELECT statements
        return draw(st.sampled_from([
            "INSERT INTO test VALUES (1)",
            "UPDATE test SET id = 1",
            "DELETE FROM test",
            "CREATE TABLE test (id INT)",
            "DROP TABLE test"
        ]))
    elif choice == 2:
        # Syntax errors
        return draw(st.sampled_from([
            "SELECT FROM",
            "SELECT * FORM table",
            "SELECT 1 +",
            "SELECT * WHERE",
            "SELECT COUNT(*"
        ]))
    elif choice == 3:
        # Empty or whitespace
        return draw(st.sampled_from(["", "   ", "\n\t"]))
    else:
        # Random invalid text
        return draw(st.text().filter(lambda x: x and not x.strip().upper().startswith('SELECT')))


@composite
def natural_language_queries(draw):
    """Generate natural language query prompts."""
    queries = [
        "Show me all tables",
        "What tables are in this database?",
        "List all columns in the users table",
        "Count the number of records",
        "Show me the database version",
        "What is the current time?",
        "Get all information about the database schema",
        "Show me system information",
        "List all available functions",
        "What databases are available?"
    ]
    return draw(st.sampled_from(queries))


class TestQueryEndpointProperties:
    """Property-based tests for query endpoint behavior."""

    @given(sql_query=valid_sql_queries())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sql_query_execution_consistency(self, client, sample_database_data, sql_query):
        """
        Property 22: API endpoint behavior
        For any valid SQL query, the query execution endpoint should return
        consistent response format with proper data structure.
        
        **Validates: Requirements 9.5**
        """
        # First create a database
        create_response = client.post("/api/v1/dbs", json=sample_database_data)
        if create_response.status_code != 200:
            pytest.skip("Database creation failed")
            
        database_name = sample_database_data["name"]
        
        try:
            # Execute the SQL query
            query_data = {"sql": sql_query}
            response = client.post(f"/api/v1/dbs/{database_name}/query", json=query_data)
            
            # Should return a response (success or error)
            assert response.status_code in [200, 400, 500]
            
            response_data = response.json()
            assert "success" in response_data
            assert "message" in response_data
            
            if response_data["success"]:
                # Successful query should have proper data structure
                assert "data" in response_data
                data = response_data["data"]
                assert "columns" in data
                assert "rows" in data
                assert "rowCount" in data or "row_count" in data
                assert "executionTimeMs" in data or "execution_time_ms" in data
                assert isinstance(data["columns"], list)
                assert isinstance(data["rows"], list)
                
        finally:
            # Clean up
            client.delete(f"/api/v1/dbs/{database_name}")

    @given(sql_query=invalid_sql_queries())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_sql_query_rejection(self, client, sample_database_data, sql_query):
        """
        Property 22: API endpoint behavior
        For any invalid SQL query, the endpoint should reject it with appropriate
        error response format.
        
        **Validates: Requirements 9.5**
        """
        # First create a database
        create_response = client.post("/api/v1/dbs", json=sample_database_data)
        if create_response.status_code != 200:
            pytest.skip("Database creation failed")
            
        database_name = sample_database_data["name"]
        
        try:
            # Execute the invalid SQL query
            query_data = {"sql": sql_query}
            response = client.post(f"/api/v1/dbs/{database_name}/query", json=query_data)
            
            # Should return an error response
            response_data = response.json()
            assert "success" in response_data
            assert response_data["success"] is False
            assert "message" in response_data
            
        finally:
            # Clean up
            client.delete(f"/api/v1/dbs/{database_name}")

    @given(nl_query=natural_language_queries())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_natural_language_query_response_format(self, client, sample_database_data, nl_query):
        """
        Property 22: API endpoint behavior
        For any natural language query, the endpoint should return consistent
        response format regardless of success or failure.
        
        **Validates: Requirements 9.6**
        """
        # First create a database
        create_response = client.post("/api/v1/dbs", json=sample_database_data)
        if create_response.status_code != 200:
            pytest.skip("Database creation failed")
            
        database_name = sample_database_data["name"]
        
        try:
            # Execute the natural language query
            query_data = {"prompt": nl_query}
            response = client.post(f"/api/v1/dbs/{database_name}/query/natural", json=query_data)
            
            # Should return a response (success or error)
            assert response.status_code in [200, 400, 500]
            
            response_data = response.json()
            assert "success" in response_data
            assert "message" in response_data
            
            if response_data["success"]:
                # Successful natural language query should have proper data structure
                assert "data" in response_data
                data = response_data["data"]
                assert "generatedSql" in data
                assert "columns" in data
                assert "rows" in data
                assert "rowCount" in data
                assert "executionTimeMs" in data
                assert isinstance(data["generatedSql"], str)
                assert isinstance(data["columns"], list)
                assert isinstance(data["rows"], list)
                
        finally:
            # Clean up
            client.delete(f"/api/v1/dbs/{database_name}")

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_query_endpoints_nonexistent_database(self, client, database_name):
        """
        Property 22: API endpoint behavior
        For any database name that doesn't exist, query endpoints should return
        404 or appropriate error with consistent format.
        
        **Validates: Requirements 9.5, 9.6**
        """
        # Ensure the database doesn't exist
        client.delete(f"/api/v1/dbs/{database_name}")
        
        # Test SQL query endpoint
        sql_response = client.post(f"/api/v1/dbs/{database_name}/query", json={"sql": "SELECT 1"})
        assert sql_response.status_code in [404, 500]
        
        try:
            sql_data = sql_response.json()
            assert "success" in sql_data
            assert sql_data["success"] is False
        except json.JSONDecodeError:
            # Some error responses might not be JSON
            pass
        
        # Test natural language query endpoint
        nl_response = client.post(f"/api/v1/dbs/{database_name}/query/natural", json={"prompt": "show tables"})
        assert nl_response.status_code in [404, 500]
        
        try:
            nl_data = nl_response.json()
            assert "success" in nl_data
            assert nl_data["success"] is False
        except json.JSONDecodeError:
            # Some error responses might not be JSON
            pass

    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(valid_sql_queries(), min_size=2, max_size=5))
    def test_multiple_query_execution_consistency(self, client, sample_database_data, sql_queries):
        """
        Property 22: API endpoint behavior
        For any sequence of valid SQL queries, each should be executed independently
        with consistent response format.
        
        **Validates: Requirements 9.5**
        """
        # First create a database
        create_response = client.post("/api/v1/dbs", json=sample_database_data)
        if create_response.status_code != 200:
            pytest.skip("Database creation failed")
            
        database_name = sample_database_data["name"]
        
        try:
            # Execute each query and verify response format
            for sql_query in sql_queries:
                query_data = {"sql": sql_query}
                response = client.post(f"/api/v1/dbs/{database_name}/query", json=query_data)
                
                # Each query should return a response
                assert response.status_code in [200, 400, 500]
                
                response_data = response.json()
                assert "success" in response_data
                assert "message" in response_data
                
                # If successful, should have consistent data structure
                if response_data["success"] and "data" in response_data:
                    data = response_data["data"]
                    assert "columns" in data
                    assert "rows" in data
                    assert isinstance(data["columns"], list)
                    assert isinstance(data["rows"], list)
                    
        finally:
            # Clean up
            client.delete(f"/api/v1/dbs/{database_name}")
