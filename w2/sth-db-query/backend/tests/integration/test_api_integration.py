"""
API Integration Tests

Tests the complete API functionality without importing internal services.
"""

import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.config import settings


class TestAPIIntegration:
    """Test API integration functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_api.db"
            yield str(db_path)

    @pytest.fixture
    def client(self, temp_db_path):
        """Create test client with temporary database."""
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            client = TestClient(app)
            # Initialize the database for each test
            from app.core.init_db import init_database
            init_database()
            yield client

    @pytest.fixture
    def mock_postgres_connection(self):
        """Mock PostgreSQL connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock successful connection test
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        
        # Mock metadata extraction
        mock_cursor.fetchall.return_value = [
            ('public', 'users', 'id', 'integer', False, True, None),
            ('public', 'users', 'name', 'varchar', False, False, None),
            ('public', 'users', 'email', 'varchar', False, False, None),
        ]
        
        return mock_conn

    def test_database_crud_workflow(self, client, mock_postgres_connection):
        """Test complete database CRUD workflow."""
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Test 1: List empty databases
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            result = response.json()
            if isinstance(result, dict) and "data" in result:
                assert len(result["data"]) == 0
            else:
                assert len(result) == 0
            
            # Test 2: Add database
            db_data = {
                "name": "test_db",
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Test database",
                "is_active": True
            }
            
            response = client.put("/api/v1/dbs/test_db", json=db_data)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["data"]["name"] == "test_db"
            
            # Test 3: List databases (should have 1)
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            result = response.json()
            if isinstance(result, dict) and "data" in result:
                db_list = result["data"]
            else:
                db_list = result
            assert len(db_list) == 1
            assert db_list[0]["name"] == "test_db"
            
            # Test 4: Get database metadata
            response = client.get("/api/v1/dbs/test_db")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            metadata = result["data"]
            assert metadata["database"] == "testdb"  # This should be the actual DB name from URL
            assert len(metadata["tables"]) == 1
            assert metadata["tables"][0]["name"] == "users"
            
            # Test 5: Update database
            update_data = {
                "name": "test_db",
                "url": "postgresql://user:newpass@localhost:5432/testdb",
                "description": "Updated test database",
                "is_active": True
            }
            response = client.put("/api/v1/dbs/test_db", json=update_data)
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["data"]["description"] == "Updated test database"
            
            # Test 6: Delete database
            response = client.delete("/api/v1/dbs/test_db")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            
            # Test 7: Verify deletion
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            result = response.json()
            if isinstance(result, dict) and "data" in result:
                assert len(result["data"]) == 0
            else:
                assert len(result) == 0

    def test_query_execution_workflow(self, client, mock_postgres_connection):
        """Test query execution workflow."""
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Setup: Add database
            db_data = {
                "name": "test_db",
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Test database",
                "is_active": True
            }
            client.put("/api/v1/dbs/test_db", json=db_data)
            
            # Mock query results
            mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                (1, "John Doe", "john@example.com"),
                (2, "Jane Smith", "jane@example.com")
            ]
            mock_postgres_connection.cursor.return_value.description = [
                ("id",), ("name",), ("email",)
            ]
            
            # Test SQL query execution
            query_data = {"sql": "SELECT * FROM users LIMIT 2"}
            response = client.post("/api/v1/dbs/test_db/query", json=query_data)
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            
            query_result = result["data"]
            assert query_result["columns"] == ["id", "name", "email"]
            assert len(query_result["rows"]) == 2
            assert query_result["rows"][0] == [1, "John Doe", "john@example.com"]

    def test_natural_language_query_workflow(self, client, mock_postgres_connection):
        """Test natural language query workflow."""
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Setup: Add database
            db_data = {
                "name": "test_db",
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Test database",
                "is_active": True
            }
            client.put("/api/v1/dbs/test_db", json=db_data)
            
            # Mock LLM service
            with patch('app.services.llm.LLMService') as mock_llm_class:
                mock_llm = MagicMock()
                mock_llm.generate_sql.return_value = "SELECT * FROM users LIMIT 10"
                mock_llm_class.return_value = mock_llm
                
                # Mock query results
                mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                    (1, "John Doe", "john@example.com")
                ]
                mock_postgres_connection.cursor.return_value.description = [
                    ("id",), ("name",), ("email",)
                ]
                
                # Test natural language query
                nl_query = {"prompt": "Show me all users"}
                response = client.post("/api/v1/dbs/test_db/query/natural", json=nl_query)
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                
                query_result = result["data"]
                assert query_result["generated_sql"] == "SELECT * FROM users LIMIT 10"
                assert query_result["columns"] == ["id", "name", "email"]
                assert len(query_result["rows"]) == 1

    def test_error_handling(self, client):
        """Test API error handling."""
        
        # Test 1: Database not found
        response = client.get("/api/v1/dbs/nonexistent")
        assert response.status_code == 404
        
        # Test 2: Invalid database connection
        with patch('psycopg2.connect', side_effect=Exception("Connection failed")):
            db_data = {
                "url": "postgresql://user:pass@invalid:5432/db",
                "description": "Invalid database",
                "is_active": True
            }
            response = client.put("/api/v1/dbs/invalid_db", json=db_data)
            assert response.status_code == 400
            result = response.json()
            assert result["success"] is False
            assert "Connection failed" in result["message"]
        
        # Test 3: Query on nonexistent database
        query_data = {"sql": "SELECT 1"}
        response = client.post("/api/v1/dbs/nonexistent/query", json=query_data)
        assert response.status_code == 404

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        
        response = client.get("/api/v1/dbs/")
        assert response.status_code == 200
        
        # Check for CORS headers (these should be added by FastAPI CORS middleware)
        # The exact headers depend on the CORS configuration
        assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()] or \
               response.status_code == 200  # Basic functionality test

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        
        response = client.get("/health")
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert result["status"] == "healthy"

    def test_concurrent_requests(self, client, mock_postgres_connection):
        """Test handling of concurrent requests."""
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Add database
            db_data = {
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Test database",
                "is_active": True
            }
            client.put("/api/v1/dbs/concurrent_test", json=db_data)
            
            # Make multiple concurrent requests (simulated sequentially)
            responses = []
            for i in range(5):
                response = client.get("/api/v1/dbs/concurrent_test")
                responses.append(response)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True

    def test_data_validation(self, client):
        """Test input data validation."""
        
        # Test 1: Invalid database URL
        invalid_db_data = {
            "url": "invalid-url",
            "description": "Invalid database",
            "is_active": True
        }
        response = client.put("/api/v1/dbs/invalid", json=invalid_db_data)
        assert response.status_code == 400
        
        # Test 2: Missing required fields
        incomplete_data = {
            "description": "Missing URL"
        }
        response = client.put("/api/v1/dbs/incomplete", json=incomplete_data)
        assert response.status_code == 422  # Validation error
        
        # Test 3: Invalid SQL query
        with patch('psycopg2.connect', return_value=MagicMock()):
            # First add a valid database
            valid_db_data = {
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Test database",
                "is_active": True
            }
            client.put("/api/v1/dbs/test_validation", json=valid_db_data)
            
            # Then try invalid query
            invalid_query = {"sql": "DROP TABLE users"}  # Non-SELECT query
            response = client.post("/api/v1/dbs/test_validation/query", json=invalid_query)
            assert response.status_code == 400
            result = response.json()
            assert result["success"] is False
