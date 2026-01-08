"""
Full system integration tests.

Tests the complete system including database persistence, API endpoints,
and cross-component interactions.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3

from app.main import app
from app.core.config import settings
from app.services.database import DatabaseService


class TestFullSystemIntegration:
    """Test complete system integration with real database persistence."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_system.db"
            yield str(db_path)

    @pytest.fixture
    def client_with_real_db(self, temp_db_path):
        """Create test client with real SQLite database."""
        with patch.object(settings, 'database_url', f"sqlite:///{temp_db_path}"):
            
            client = TestClient(app)
            
            # Initialize database
            db_service = DatabaseService()
            db_service.init_db()
            
            yield client

    @pytest.fixture
    def mock_postgres_connection(self):
        """Mock PostgreSQL connection with realistic responses."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock successful connection test
        mock_cursor.execute.return_value = None
        mock_cursor.fetchone.return_value = (1,)
        
        # Mock metadata extraction
        mock_cursor.fetchall.return_value = [
            ('public', 'users', 'id', 'integer', False, True, None),
            ('public', 'users', 'username', 'varchar', False, False, None),
            ('public', 'users', 'email', 'varchar', False, False, None),
            ('public', 'users', 'created_at', 'timestamp', False, False, 'now()'),
            ('public', 'orders', 'id', 'integer', False, True, None),
            ('public', 'orders', 'user_id', 'integer', False, False, None),
            ('public', 'orders', 'total_amount', 'decimal', False, False, None),
            ('public', 'orders', 'order_date', 'timestamp', False, False, 'now()'),
            ('public', 'products', 'id', 'integer', False, True, None),
            ('public', 'products', 'name', 'varchar', False, False, None),
            ('public', 'products', 'price', 'decimal', False, False, None),
        ]
        
        return mock_conn

    def test_complete_system_workflow(self, client_with_real_db, mock_postgres_connection, temp_db_path):
        """Test complete system workflow with database persistence."""
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            client = client_with_real_db
            
            # Step 1: Verify empty system
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            assert len(response.json()) == 0
            
            # Step 2: Add multiple databases
            databases = [
                {
                    "name": "production",
                    "url": "postgresql://user:pass@prod.example.com:5432/proddb",
                    "description": "Production database",
                },
                {
                    "name": "staging", 
                    "url": "postgresql://user:pass@staging.example.com:5432/stagingdb",
                    "description": "Staging database",
                },
                {
                    "name": "analytics",
                    "url": "postgresql://user:pass@analytics.example.com:5432/analyticsdb", 
                    "description": "Analytics database",
                }
            ]
            
            for db in databases:
                response = client.put(f"/api/v1/dbs/{db['name']}", json={
                    "url": db["url"],
                    "description": db["description"],
                    "is_active": True
                })
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                assert result["data"]["name"] == db["name"]
            
            # Step 3: Verify databases are persisted
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            db_list = response.json()
            assert len(db_list) == 3
            
            db_names = [db["name"] for db in db_list]
            assert "production" in db_names
            assert "staging" in db_names
            assert "analytics" in db_names
            
            # Step 4: Verify metadata extraction for each database
            for db in databases:
                response = client.get(f"/api/v1/dbs/{db['name']}")
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                
                metadata = result["data"]
                assert metadata["database"] == db["name"]
                assert len(metadata["tables"]) == 3  # users, orders, products
                
                # Verify table structure
                table_names = [table["name"] for table in metadata["tables"]]
                assert "users" in table_names
                assert "orders" in table_names
                assert "products" in table_names
                
                # Verify users table structure
                users_table = next(t for t in metadata["tables"] if t["name"] == "users")
                assert len(users_table["columns"]) == 4
                column_names = [col["name"] for col in users_table["columns"]]
                assert "id" in column_names
                assert "username" in column_names
                assert "email" in column_names
                assert "created_at" in column_names
            
            # Step 5: Test query execution on different databases
            mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                (1, "john_doe", "john@example.com", "2024-01-01 10:00:00"),
                (2, "jane_smith", "jane@example.com", "2024-01-02 11:00:00"),
            ]
            mock_postgres_connection.cursor.return_value.description = [
                ("id",), ("username",), ("email",), ("created_at",)
            ]
            
            for db_name in ["production", "staging", "analytics"]:
                query_data = {"sql": f"SELECT * FROM users WHERE id <= 2"}
                response = client.post(f"/api/v1/dbs/{db_name}/query", json=query_data)
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                
                query_result = result["data"]
                assert query_result["columns"] == ["id", "username", "email", "created_at"]
                assert len(query_result["rows"]) == 2
                assert query_result["row_count"] == 2
            
            # Step 6: Test database updates
            update_data = {
                "url": "postgresql://user:newpass@prod.example.com:5432/proddb",
                "description": "Updated production database",
                "is_active": True
            }
            response = client.put("/api/v1/dbs/production", json=update_data)
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["data"]["description"] == "Updated production database"
            
            # Step 7: Verify persistence after updates
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            db_list = response.json()
            production_db = next(db for db in db_list if db["name"] == "production")
            assert production_db["description"] == "Updated production database"
            
            # Step 8: Test database deletion
            response = client.delete("/api/v1/dbs/staging")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            
            # Verify deletion
            response = client.get("/api/v1/dbs/")
            assert response.status_code == 200
            db_list = response.json()
            assert len(db_list) == 2
            db_names = [db["name"] for db in db_list]
            assert "staging" not in db_names
            
            # Step 9: Verify SQLite database contains expected data
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # Check database_connections table
            cursor.execute("SELECT name, description FROM database_connections WHERE is_active = 1")
            active_dbs = cursor.fetchall()
            assert len(active_dbs) == 2
            
            active_db_names = [db[0] for db in active_dbs]
            assert "production" in active_db_names
            assert "analytics" in active_db_names
            
            # Check metadata tables
            cursor.execute("SELECT DISTINCT database_name FROM database_metadata")
            metadata_dbs = [row[0] for row in cursor.fetchall()]
            assert "production" in metadata_dbs
            assert "analytics" in metadata_dbs
            
            conn.close()

    def test_system_error_recovery(self, client_with_real_db, temp_db_path):
        """Test system behavior during error conditions and recovery."""
        
        client = client_with_real_db
        
        # Test 1: Connection failure during database addition
        with patch('psycopg2.connect', side_effect=Exception("Connection timeout")):
            db_data = {
                "url": "postgresql://user:pass@unreachable:5432/db",
                "description": "Unreachable database",
                "is_active": True
            }
            
            response = client.put("/api/v1/dbs/unreachable", json=db_data)
            assert response.status_code == 400
            result = response.json()
            assert result["success"] is False
            assert "Connection timeout" in result["message"]
        
        # Verify no partial data was saved
        response = client.get("/api/v1/dbs/")
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # Test 2: Recovery after fixing connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('public', 'test_table', 'id', 'integer', False, True, None),
        ]
        
        with patch('psycopg2.connect', return_value=mock_conn):
            response = client.put("/api/v1/dbs/recovered", json={
                "url": "postgresql://user:pass@localhost:5432/recovereddb",
                "description": "Recovered database",
                "is_active": True
            })
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
        
        # Verify database was added successfully
        response = client.get("/api/v1/dbs/")
        assert response.status_code == 200
        db_list = response.json()
        assert len(db_list) == 1
        assert db_list[0]["name"] == "recovered"

    def test_concurrent_database_operations(self, client_with_real_db, mock_postgres_connection):
        """Test concurrent database operations."""
        
        client = client_with_real_db
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Add database
            response = client.put("/api/v1/dbs/concurrent_test", json={
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Concurrent test database",
                "is_active": True
            })
            assert response.status_code == 200
            
            # Simulate concurrent operations
            operations = []
            
            # Concurrent metadata requests
            for i in range(5):
                response = client.get("/api/v1/dbs/concurrent_test")
                operations.append(response)
            
            # All should succeed
            for response in operations:
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
            
            # Concurrent query executions
            mock_postgres_connection.cursor.return_value.fetchall.return_value = [
                (i, f"user_{i}") for i in range(10)
            ]
            mock_postgres_connection.cursor.return_value.description = [
                ("id",), ("username",)
            ]
            
            query_operations = []
            for i in range(3):
                response = client.post("/api/v1/dbs/concurrent_test/query", json={
                    "sql": f"SELECT * FROM users WHERE id > {i} LIMIT 10"
                })
                query_operations.append(response)
            
            # All queries should succeed
            for response in query_operations:
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                assert len(result["data"]["rows"]) == 10

    def test_system_data_consistency(self, client_with_real_db, mock_postgres_connection, temp_db_path):
        """Test data consistency across operations."""
        
        client = client_with_real_db
        
        with patch('psycopg2.connect', return_value=mock_postgres_connection):
            # Add database
            response = client.put("/api/v1/dbs/consistency_test", json={
                "url": "postgresql://user:pass@localhost:5432/testdb",
                "description": "Consistency test database",
                "is_active": True
            })
            assert response.status_code == 200
            
            # Get metadata multiple times
            metadata_responses = []
            for _ in range(3):
                response = client.get("/api/v1/dbs/consistency_test")
                metadata_responses.append(response.json())
            
            # All metadata should be identical
            first_metadata = metadata_responses[0]["data"]
            for metadata in metadata_responses[1:]:
                assert metadata["data"] == first_metadata
            
            # Verify SQLite consistency
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # Check that metadata is stored correctly
            cursor.execute("""
                SELECT table_name, column_name, data_type 
                FROM database_metadata 
                WHERE database_name = 'consistency_test'
                ORDER BY table_name, column_name
            """)
            stored_metadata = cursor.fetchall()
            
            # Should have metadata for all tables and columns
            assert len(stored_metadata) > 0
            
            # Verify table names match API response
            api_tables = {table["name"] for table in first_metadata["tables"]}
            stored_tables = {row[0] for row in stored_metadata}
            assert api_tables == stored_tables
            
            conn.close()
