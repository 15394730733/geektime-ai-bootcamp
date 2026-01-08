"""
Property-based tests for metadata extraction error handling.

Feature: database-query-tool, Property 4: Metadata extraction error handling
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.services.database import DatabaseService, DatabaseServiceError
from app.schemas.database import DatabaseCreate
from app.models import Base


# Generators for property-based testing
@st.composite
def invalid_connection_urls(draw):
    """Generate invalid connection URLs that will cause connection failures."""
    invalid_type = draw(st.sampled_from([
        "nonexistent_host",
        "invalid_port",
        "invalid_credentials",
        "invalid_database"
    ]))
    
    if invalid_type == "nonexistent_host":
        # Non-existent hostname
        host = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz",
            min_size=10,
            max_size=30
        )) + "-nonexistent-host-12345"
        return f"postgresql://user:pass@{host}:5432/testdb"
    
    elif invalid_type == "invalid_port":
        # Port that's likely to be closed
        port = draw(st.integers(min_value=60000, max_value=65000))
        return f"postgresql://user:pass@localhost:{port}/testdb"
    
    elif invalid_type == "invalid_credentials":
        # Invalid username/password
        username = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz",
            min_size=10,
            max_size=20
        )) + "_invalid_user"
        password = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
            min_size=10,
            max_size=20
        )) + "_invalid_pass"
        return f"postgresql://{username}:{password}@localhost:5432/testdb"
    
    else:  # invalid_database
        # Non-existent database name
        database = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz",
            min_size=10,
            max_size=20
        )) + "_nonexistent_db_12345"
        return f"postgresql://user:pass@localhost:5432/{database}"


async def create_test_db_session():
    """Create a test database session for property tests."""
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    session = async_session()
    return session, engine


class TestMetadataErrorHandlingProperties:
    """Property-based tests for metadata extraction error handling."""

    @given(invalid_connection_urls())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_4_connection_failure_error_handling(self, invalid_url: str):
        """
        Property 4: Connection failure error handling
        
        For any database connection that fails during metadata extraction,
        the system should return an error without storing incomplete data.
        
        **Validates: Requirements 2.5**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Create a test database connection with invalid URL
            connection_data = DatabaseCreate(
                name="error_test_db",
                url=invalid_url,
                description="Test database for error handling"
            )
            
            # Mock connection testing to succeed initially (to allow creation)
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # Restore original method so metadata extraction will fail with real connection
            service._test_connection = service.__class__._test_connection.__get__(service, service.__class__)
            
            # Attempt to refresh metadata (this should fail due to connection issues)
            with pytest.raises(DatabaseServiceError) as exc_info:
                await service.refresh_database_metadata(
                    db_session, 
                    invalid_url, 
                    connection_id
                )
            
            # Verify error message is descriptive
            error_message = str(exc_info.value).lower()
            assert len(error_message) > 0
            assert any(keyword in error_message for keyword in [
                "failed", "extract", "metadata", "connection", "error"
            ]), f"Error message '{error_message}' not descriptive enough"
            
            # Verify no incomplete metadata was stored
            metadata_result = await service.get_database_metadata(db_session, "error_test_db")
            
            # Should have empty tables and views (no partial data stored)
            assert len(metadata_result["tables"]) == 0
            assert len(metadata_result["views"]) == 0
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_4_extraction_exception_handling(self, db_name: str):
        """
        Property 4: Extraction exception handling
        
        For any exception that occurs during metadata extraction,
        the system should handle it gracefully and return a descriptive error.
        
        **Validates: Requirements 2.5**
        """
        # Filter out invalid names
        if not db_name or not db_name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Create a test database connection
            connection_data = DatabaseCreate(
                name=db_name,
                url="postgresql://user:pass@localhost:5432/testdb",
                description="Test database for exception handling"
            )
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # Mock metadata extraction to raise an exception
            def mock_extract_metadata_with_exception(database_url: str, conn_id: str):
                raise Exception("Simulated extraction failure - database query error")
            
            service._extract_database_metadata = mock_extract_metadata_with_exception
            
            # Attempt to refresh metadata (should handle exception gracefully)
            with pytest.raises(DatabaseServiceError) as exc_info:
                await service.refresh_database_metadata(
                    db_session, 
                    connection_data.url, 
                    connection_id
                )
            
            # Verify error is wrapped in DatabaseServiceError with descriptive message
            error_message = str(exc_info.value)
            assert "Failed to refresh database metadata" in error_message
            assert "Simulated extraction failure" in error_message
            
            # Verify no partial metadata was stored
            metadata_result = await service.get_database_metadata(db_session, db_name)
            assert len(metadata_result["tables"]) == 0
            assert len(metadata_result["views"]) == 0
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_4_partial_failure_cleanup(self, db_name: str):
        """
        Property 4: Partial failure cleanup
        
        For any metadata extraction that fails partway through,
        the system should clean up any partially stored data.
        
        **Validates: Requirements 2.5**
        """
        # Filter out invalid names
        if not db_name or not db_name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Create a test database connection
            connection_data = DatabaseCreate(
                name=db_name,
                url="postgresql://user:pass@localhost:5432/testdb",
                description="Test database for partial failure cleanup"
            )
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # First, store some initial metadata successfully
            initial_metadata = [{
                "connection_id": connection_id,
                "object_type": "table",
                "schema_name": "public",
                "object_name": "initial_table",
                "columns": [{
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "is_primary_key": True,
                    "default_value": None
                }]
            }]
            
            def mock_extract_initial_metadata(database_url: str, conn_id: str):
                return initial_metadata
            
            service._extract_database_metadata = mock_extract_initial_metadata
            
            # Store initial metadata
            await service.refresh_database_metadata(
                db_session, 
                connection_data.url, 
                connection_id
            )
            
            # Verify initial metadata was stored
            metadata_before = await service.get_database_metadata(db_session, db_name)
            assert len(metadata_before["tables"]) == 1
            assert metadata_before["tables"][0]["name"] == "initial_table"
            
            # Now mock extraction to fail 
            def mock_extract_with_failure(database_url: str, conn_id: str):
                raise Exception("Simulated failure during metadata refresh")
            
            service._extract_database_metadata = mock_extract_with_failure
            
            # Attempt to refresh metadata (should fail and cleanup)
            with pytest.raises(DatabaseServiceError):
                await service.refresh_database_metadata(
                    db_session, 
                    connection_data.url, 
                    connection_id
                )
            
            # Verify that old metadata was cleaned up (no partial state)
            metadata_after = await service.get_database_metadata(db_session, db_name)
            assert len(metadata_after["tables"]) == 0  # Should be cleaned up
            assert len(metadata_after["views"]) == 0
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_4_nonexistent_database_error_handling(self, db_name: str):
        """
        Property 4: Nonexistent database error handling
        
        For any request to get metadata for a nonexistent database,
        the system should return a clear error message.
        
        **Validates: Requirements 2.5**
        """
        # Filter out invalid names
        if not db_name or not db_name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Attempt to get metadata for a database that doesn't exist
            with pytest.raises(DatabaseServiceError) as exc_info:
                await service.get_database_metadata(db_session, f"nonexistent_{db_name}")
            
            # Verify error message is clear and descriptive
            error_message = str(exc_info.value)
            assert "not found" in error_message.lower()
            assert f"nonexistent_{db_name}" in error_message
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_4_error_message_consistency(self, db_name: str):
        """
        Property 4: Error message consistency
        
        For any type of metadata extraction error, the system should
        return consistent error message formats and structures.
        
        **Validates: Requirements 2.5**
        """
        # Filter out invalid names
        if not db_name or not db_name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Test different types of errors and verify consistent format
            error_scenarios = [
                ("nonexistent_database", lambda: service.get_database_metadata(db_session, f"nonexistent_{db_name}")),
            ]
            
            for scenario_name, error_func in error_scenarios:
                with pytest.raises(DatabaseServiceError) as exc_info:
                    await error_func()
                
                # Verify error is wrapped in DatabaseServiceError
                assert isinstance(exc_info.value, DatabaseServiceError)
                
                # Verify error message is not empty and is descriptive
                error_message = str(exc_info.value)
                assert len(error_message) > 0
                assert not error_message.isspace()
                
                # Verify error message contains relevant context
                if scenario_name == "nonexistent_database":
                    assert any(keyword in error_message.lower() for keyword in [
                        "not found", "database", "metadata"
                    ])
            
        finally:
            await db_session.close()
            await engine.dispose()
