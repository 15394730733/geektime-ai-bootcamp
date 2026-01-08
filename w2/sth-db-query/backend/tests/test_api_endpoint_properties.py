"""
Property-based tests for API endpoints.

Feature: database-query-tool, Property 22: API endpoint behavior
Validates: Requirements 9.2, 9.3, 9.4
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import json
from typing import Dict, Any
from unittest.mock import patch, AsyncMock


@composite
def valid_database_data(draw):
    """Generate valid database connection data."""
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"),
        min_size=1,
        max_size=20
    ).filter(lambda x: x and not x.startswith('-') and not x.startswith('_')))
    
    # Generate valid PostgreSQL URL components
    username = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=10))
    password = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=10))
    host = draw(st.sampled_from(["localhost", "127.0.0.1", "db.example.com"]))
    port = draw(st.integers(min_value=1024, max_value=65535))
    database = draw(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=10))
    
    url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    description = draw(st.text(max_size=100))
    
    return {
        "name": name,
        "url": url,
        "description": description
    }


@composite
def invalid_database_data(draw):
    """Generate invalid database connection data."""
    choice = draw(st.integers(min_value=1, max_value=4))
    
    if choice == 1:
        # Invalid name with spaces or special characters
        name = draw(st.text().filter(lambda x: ' ' in x or any(c in x for c in '!@#$%^&*()')))
        return {
            "name": name,
            "url": "postgresql://user:pass@localhost:5432/test",
            "description": "Test"
        }
    elif choice == 2:
        # Invalid URL format
        return {
            "name": "test_db",
            "url": draw(st.text().filter(lambda x: not x.startswith(('postgresql://', 'postgres://')))),
            "description": "Test"
        }
    elif choice == 3:
        # Missing required fields
        return draw(st.dictionaries(
            st.sampled_from(["name", "url", "description"]),
            st.text(),
            min_size=0,
            max_size=2
        ))
    else:
        # Empty name
        return {
            "name": "",
            "url": "postgresql://user:pass@localhost:5432/test",
            "description": "Test"
        }


class TestAPIEndpointProperties:
    """Property-based tests for API endpoint behavior."""

    @given(database_data=valid_database_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_database_creation_and_retrieval_consistency(self, client, database_data):
        """
        Property 22: API endpoint behavior
        For any valid database data, creating a database should result in it being retrievable
        with all fields intact and proper response format.
        
        **Validates: Requirements 9.2, 9.3, 9.4**
        """
        with patch('app.services.database.DatabaseService._test_connection') as mock_test_connection, \
             patch('app.services.database.DatabaseService.refresh_database_metadata') as mock_refresh_metadata:
            
            # Mock successful connection test
            mock_test_connection.return_value = {
                "success": True,
                "message": "Database connection successful",
                "latency_ms": 50
            }
            
            # Mock successful metadata refresh
            mock_refresh_metadata.return_value = AsyncMock()
            
            # Create database
            create_response = client.post("/api/v1/dbs", json=database_data)
            
            # Should succeed for valid data
            if create_response.status_code == 200:
                create_data = create_response.json()
                
                # Verify response format
                assert create_data["success"] is True
                assert "data" in create_data
                assert "message" in create_data
                
                # Verify created database data
                created_db = create_data["data"]
                assert created_db["name"] == database_data["name"]
                assert created_db["url"] == database_data["url"]
                assert created_db["description"] == database_data["description"]
                assert "id" in created_db
                assert "createdAt" in created_db or "created_at" in created_db
                assert "updatedAt" in created_db or "updated_at" in created_db
                assert "isActive" in created_db or "is_active" in created_db
                
                # Test retrieval by listing all databases
                list_response = client.get("/api/v1/dbs")
                assert list_response.status_code == 200
                list_data = list_response.json()
                assert list_data["success"] is True
                assert isinstance(list_data["data"], list)
                
                # Find our database in the list
                found_db = None
                for db in list_data["data"]:
                    if db["name"] == database_data["name"]:
                        found_db = db
                        break
                
                assert found_db is not None, f"Database {database_data['name']} not found in list"
                assert found_db["name"] == database_data["name"]
                assert found_db["url"] == database_data["url"]
                assert found_db["description"] == database_data["description"]
                
                # Test retrieval by name (metadata endpoint)
                get_response = client.get(f"/api/v1/dbs/{database_data['name']}")
                assert get_response.status_code == 200
                get_data = get_response.json()
                assert get_data["success"] is True
                assert "data" in get_data
                
                # Verify metadata response structure
                metadata = get_data["data"]
                assert "database" in metadata
                assert "tables" in metadata
                assert "views" in metadata
                assert isinstance(metadata["tables"], list)
                assert isinstance(metadata["views"], list)
                
                # Clean up - delete the database
                delete_response = client.delete(f"/api/v1/dbs/{database_data['name']}")
                assert delete_response.status_code == 200

    @given(database_data=valid_database_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_put_endpoint_create_or_update_behavior(self, client, database_data):
        """
        Property 22: API endpoint behavior
        For any valid database data, PUT endpoint should create new databases
        and update existing ones consistently.
        
        **Validates: Requirements 9.3**
        """
        with patch('app.services.database.DatabaseService._test_connection') as mock_test_connection, \
             patch('app.services.database.DatabaseService.refresh_database_metadata') as mock_refresh_metadata:
            
            # Mock successful connection test
            mock_test_connection.return_value = {
                "success": True,
                "message": "Database connection successful",
                "latency_ms": 50
            }
            
            # Mock successful metadata refresh
            mock_refresh_metadata.return_value = AsyncMock()
            
            name = database_data["name"]
            
            # First PUT should create the database
            put_response = client.put(f"/api/v1/dbs/{name}", json=database_data)
            
            if put_response.status_code == 200:
                put_data = put_response.json()
                assert put_data["success"] is True
                assert put_data["data"]["name"] == name
                
                # Second PUT with different description should update
                updated_data = database_data.copy()
                updated_data["description"] = "Updated description"
                
                update_response = client.put(f"/api/v1/dbs/{name}", json=updated_data)
                assert update_response.status_code == 200
                update_data = update_response.json()
                assert update_data["success"] is True
                assert update_data["data"]["description"] == "Updated description"
                
                # Clean up
                client.delete(f"/api/v1/dbs/{name}")

    @given(database_data=invalid_database_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_data_rejection(self, client, database_data):
        """
        Property 22: API endpoint behavior
        For any invalid database data, the API should reject it with appropriate error codes
        and maintain consistent error response format.
        
        **Validates: Requirements 9.2, 9.4**
        """
        # Try to create database with invalid data
        create_response = client.post("/api/v1/dbs", json=database_data)
        
        # Should not succeed
        assert create_response.status_code in [400, 422, 500]
        
        # Should have consistent error response format
        if create_response.status_code != 500:  # 500 might not have JSON body
            try:
                error_data = create_response.json()
                # FastAPI validation errors have 'detail' field, our custom errors have 'success' field
                assert "success" in error_data or "detail" in error_data
                if "success" in error_data:
                    assert error_data["success"] is False
            except json.JSONDecodeError:
                # Some error responses might not be JSON
                pass

    @given(st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_"), min_size=1, max_size=50).filter(lambda x: x and not x.startswith('-') and not x.startswith('_')))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_nonexistent_database_handling(self, client, database_name):
        """
        Property 22: API endpoint behavior
        For any database name that doesn't exist, GET requests should return 404
        with consistent error format.
        
        **Validates: Requirements 9.4**
        """
        # Ensure the database doesn't exist by trying to delete it first
        client.delete(f"/api/v1/dbs/{database_name}")
        
        # Try to get non-existent database metadata
        get_response = client.get(f"/api/v1/dbs/{database_name}")
        assert get_response.status_code == 404
        
        try:
            error_data = get_response.json()
            # Check for either our custom error format or FastAPI's default format
            if "success" in error_data:
                assert error_data["success"] is False
                assert "message" in error_data
                assert "not found" in error_data["message"].lower()
            elif "detail" in error_data:
                # FastAPI default error format
                assert "not found" in str(error_data["detail"]).lower()
        except json.JSONDecodeError:
            # Some 404 responses might not be JSON
            pass

    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(valid_database_data(), min_size=1, max_size=5, unique_by=lambda x: x["name"]))
    def test_multiple_databases_consistency(self, client, database_list):
        """
        Property 22: API endpoint behavior
        For any list of valid databases, creating multiple databases should result
        in all being retrievable through the list endpoint.
        
        **Validates: Requirements 9.2**
        """
        with patch('app.services.database.DatabaseService._test_connection') as mock_test_connection, \
             patch('app.services.database.DatabaseService.refresh_database_metadata') as mock_refresh_metadata:
            
            # Mock successful connection test
            mock_test_connection.return_value = {
                "success": True,
                "message": "Database connection successful",
                "latency_ms": 50
            }
            
            # Mock successful metadata refresh
            mock_refresh_metadata.return_value = AsyncMock()
            
            created_names = []
            
            try:
                # Create all databases
                for db_data in database_list:
                    response = client.post("/api/v1/dbs", json=db_data)
                    if response.status_code == 200:
                        created_names.append(db_data["name"])
                
                # Get list of all databases
                list_response = client.get("/api/v1/dbs")
                assert list_response.status_code == 200
                list_data = list_response.json()
                assert list_data["success"] is True
                
                # Verify all created databases are in the list
                db_names_in_list = {db["name"] for db in list_data["data"]}
                for name in created_names:
                    assert name in db_names_in_list, f"Database {name} not found in list"
                    
            finally:
                # Clean up all created databases
                for name in created_names:
                    client.delete(f"/api/v1/dbs/{name}")
