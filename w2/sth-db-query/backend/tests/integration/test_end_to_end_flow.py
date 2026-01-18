"""
Integration tests for end-to-end database query tool functionality.

Tests the complete flow from database connection to query execution.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
from pathlib import Path

from app.main import app
from app.core.config import settings
from app.services.database import DatabaseService
from app.services.query import QueryService
from app.services.llm import LLMService


class TestEndToEndFlow:
    """Test complete end-to-end workflows."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_db.db"
            yield str(db_path)

    @pytest.fixture
    def mock_postgres_connection(self):
        """Mock PostgreSQL connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock metadata query results
        mock_cursor.fetchall.return_value = [
            ('public', 'users', 'id', 'integer', False, True, None),
            ('public', 'users', 'name', 'varchar', False, False, None),
            ('public', 'users', 'email', 'varchar', False, False, None),
            ('public', 'orders', 'id', 'integer', False, True, None),
            ('public', 'orders', 'user_id', 'integer', False, False, None),
            ('public', 'orders', 'total', 'decimal', False, False, None),
        ]
        
        return mock_conn

    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service."""
        with patch('app.services.llm.LLMService') as mock_llm:
            mock_instance = MagicMock()
            mock_instance.generate_sql.return_value = "SELECT * FROM users LIMIT 10"
            mock_llm.return_value = mock_instance
            yield mock_instance

    def test_complete_database_workflow(self, client, temp_db_path, mock_postgres_connection):
        """Test complete workflow: add database -> extract metadata -> execute query."""
        
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            with patch('psycopg2.connect', return_value=mock_postgres_connection):
                # Step 1: Add database connection
                db_data = {
                    "url": "postgresql://user:pass@localhost:5432/testdb",
                    "description": "Test database for integration testing",
                    "is_active": True
                }
                
                response = client.put("/api/v1/dbs/test_db", json=db_data)
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                assert result["data"]["name"] == "test_db"
                
                # Step 2: Get database metadata
                response = client.get("/api/v1/dbs/test_db")
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                metadata = result["data"]
                assert metadata["database"] == "test_db"
                assert len(metadata["tables"]) == 2  # users and orders
                
                # Verify table structure
                users_table = next(t for t in metadata["tables"] if t["name"] == "users")
                assert len(users_table["columns"]) == 3
                assert any(c["name"] == "id" and c["is_primary_key"] for c in users_table["columns"])
                
                # Step 3: Execute SQL query
                query_data = {"sql": "SELECT * FROM users WHERE id = 1"}
                
                # Mock query execution
                mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                    (1, "John Doe", "john@example.com")
                ]
                mock_postgres_connection.cursor.return_value.description = [
                    ("id",), ("name",), ("email",)
                ]
                
                response = client.post("/api/v1/dbs/test_db/query", json=query_data)
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                query_result = result["data"]
                assert query_result["columns"] == ["id", "name", "email"]
                assert len(query_result["rows"]) == 1
                assert query_result["rows"][0] == [1, "John Doe", "john@example.com"]

    def test_natural_language_query_workflow(self, client, temp_db_path, mock_postgres_connection, mock_llm_service):
        """Test natural language query processing workflow."""
        
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            with patch('psycopg2.connect', return_value=mock_postgres_connection):
                # Setup: Add database and extract metadata
                db_data = {
                    "url": "postgresql://user:pass@localhost:5432/testdb",
                    "description": "Test database",
                    "is_active": True
                }
                client.put("/api/v1/dbs/test_db", json=db_data)
                
                # Test natural language query
                nl_query = {"prompt": "Show me all users"}
                
                # Mock LLM response and query execution
                mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                    (1, "John Doe", "john@example.com"),
                    (2, "Jane Smith", "jane@example.com")
                ]
                mock_postgres_connection.cursor.return_value.description = [
                    ("id",), ("name",), ("email",)
                ]
                
                response = client.post("/api/v1/dbs/test_db/query/natural", json=nl_query)
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                
                query_result = result["data"]
                assert query_result["generated_sql"] == "SELECT * FROM users LIMIT 10"
                assert query_result["columns"] == ["id", "name", "email"]
                assert len(query_result["rows"]) == 2

    def test_error_propagation_workflow(self, client, temp_db_path):
        """Test error propagation from backend to frontend."""
        
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            # Test 1: Database connection error
            with patch('psycopg2.connect', side_effect=Exception("Connection failed")):
                db_data = {
                    "url": "postgresql://user:pass@localhost:5432/testdb",
                    "description": "Test database",
                    "is_active": True
                }
                
                response = client.put("/api/v1/dbs/test_db", json=db_data)
                assert response.status_code == 400
                result = response.json()
                assert result["success"] is False
                assert "Connection failed" in result["message"]
            
            # Test 2: Query execution error
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.execute.side_effect = Exception("SQL error")
            
            with patch('psycopg2.connect', return_value=mock_conn):
                # First add a database successfully
                mock_conn.cursor.return_value.execute.side_effect = None
                mock_conn.cursor.return_value.fetchall.return_value = []
                client.put("/api/v1/dbs/test_db", json=db_data)
                
                # Then try to execute a query that fails
                mock_conn.cursor.return_value.execute.side_effect = Exception("SQL error")
                query_data = {"sql": "SELECT * FROM nonexistent_table"}
                
                response = client.post("/api/v1/dbs/test_db/query", json=query_data)
                assert response.status_code == 400
                result = response.json()
                assert result["success"] is False
                assert "SQL error" in result["message"]

    def test_database_list_and_metadata_consistency(self, client, temp_db_path, mock_postgres_connection):
        """Test consistency between database list and metadata operations."""
        
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            with patch('psycopg2.connect', return_value=mock_postgres_connection):
                # Add multiple databases
                databases = [
                    {"name": "db1", "url": "postgresql://user:pass@localhost:5432/db1", "description": "Database 1"},
                    {"name": "db2", "url": "postgresql://user:pass@localhost:5432/db2", "description": "Database 2"},
                ]
                
                for db in databases:
                    response = client.put(f"/api/v1/dbs/{db['name']}", json={
                        "url": db["url"],
                        "description": db["description"],
                        "is_active": True
                    })
                    assert response.status_code == 200
                
                # Get database list
                response = client.get("/api/v1/dbs/")
                assert response.status_code == 200
                db_list = response.json()
                assert len(db_list) == 2
                
                # Verify each database has metadata
                for db in db_list:
                    response = client.get(f"/api/v1/dbs/{db['name']}")
                    assert response.status_code == 200
                    result = response.json()
                    assert result["success"] is True
                    assert result["data"]["database"] == db["name"]

    def test_concurrent_operations(self, client, temp_db_path, mock_postgres_connection):
        """Test concurrent database operations."""
        
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            with patch('psycopg2.connect', return_value=mock_postgres_connection):
                # Add database
                db_data = {
                    "url": "postgresql://user:pass@localhost:5432/testdb",
                    "description": "Test database",
                    "is_active": True
                }
                client.put("/api/v1/dbs/test_db", json=db_data)
                
                # Mock concurrent query results
                mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                    (1, "Result 1"), (2, "Result 2")
                ]
                mock_postgres_connection.cursor.return_value.description = [
                    ("id",), ("value",)
                ]
                
                # Execute multiple queries concurrently (simulated)
                queries = [
                    {"sql": "SELECT * FROM table1 LIMIT 5"},
                    {"sql": "SELECT * FROM table2 LIMIT 5"},
                    {"sql": "SELECT * FROM table3 LIMIT 5"},
                ]
                
                results = []
                for query in queries:
                    response = client.post("/api/v1/dbs/test_db/query", json=query)
                    assert response.status_code == 200
                    result = response.json()
                    assert result["success"] is True
                    results.append(result["data"])
                
                # Verify all queries executed successfully
                assert len(results) == 3
                for result in results:
                    assert result["columns"] == ["id", "value"]
                    assert len(result["rows"]) == 2
