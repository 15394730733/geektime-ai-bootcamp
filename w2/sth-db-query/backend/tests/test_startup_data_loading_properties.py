"""
Property-based tests for application startup data loading.

Feature: database-query-tool, Property 18: Application startup data loading
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime, timezone
from uuid import uuid4

from app.services.startup import StartupService
from app.models import Base
from app.models.database import DatabaseConnection
from app.schemas.database import Database


# Generators for property-based testing
@st.composite
def database_connection_record(draw):
    """Generate a database connection record for testing."""
    # Use a counter to ensure unique names
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
        min_size=1,
        max_size=20
    ).filter(lambda x: x and x[0].isalnum() and x[-1].isalnum()))
    
    # Ensure unique names by appending UUID suffix
    name = f"{name}_{unique_suffix}"
    
    # Generate valid PostgreSQL URLs
    host = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=20
    ))
    
    port = draw(st.integers(min_value=1024, max_value=65535))
    username = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=1,
        max_size=20
    ))
    password = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=20
    ))
    database = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=1,
        max_size=20
    ))
    
    url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    description = draw(st.one_of(
        st.none(),
        st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._-", max_size=200)
    ))
    
    is_active = draw(st.booleans())
    
    # Generate timestamps
    created_at = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2024, 12, 31)
    ))
    
    return DatabaseConnection(
        id=str(uuid4()),
        name=name,
        url=url,
        description=description,
        is_active=is_active,
        created_at=created_at
    )


async def create_test_db_with_connections(connections):
    """Create a test database session with pre-populated connections."""
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
    
    # Create session and populate with test data
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Add test connections to the database
        for connection in connections:
            session.add(connection)
        
        await session.commit()
    
    return async_session, engine


class TestStartupDataLoadingProperties:
    """Property-based tests for application startup data loading."""

    @given(st.lists(database_connection_record(), min_size=0, max_size=3))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_18_startup_data_loading(self, stored_connections):
        """
        Property 18: Application startup data loading
        
        For any set of stored database connections, application startup should
        load all connections from the metadata store with all fields intact.
        
        **Validates: Requirements 8.2**
        """
        # Create test database with stored connections
        async_session_factory, engine = await create_test_db_with_connections(stored_connections)
        
        try:
            # Create a fresh startup service instance
            startup_service = StartupService()
            
            # Mock the async_session to use our test database
            import app.services.startup
            original_session = app.services.startup.async_session
            app.services.startup.async_session = async_session_factory
            
            try:
                # Load stored connections
                loaded_connections = await startup_service.load_stored_connections()
                
                # Verify all connections were loaded
                assert len(loaded_connections) == len(stored_connections)
                
                # Create lookup maps for comparison
                stored_by_name = {conn.name: conn for conn in stored_connections}
                loaded_by_name = {conn.name: conn for conn in loaded_connections}
                
                # Verify all stored connections are present in loaded connections
                for stored_conn in stored_connections:
                    assert stored_conn.name in loaded_by_name
                    loaded_conn = loaded_by_name[stored_conn.name]
                    
                    # Verify all fields are intact
                    assert loaded_conn.name == stored_conn.name
                    assert loaded_conn.url == stored_conn.url
                    assert loaded_conn.description == stored_conn.description
                    assert loaded_conn.is_active == stored_conn.is_active
                    assert loaded_conn.id == stored_conn.id
                    
                    # Verify timestamps are preserved (allowing for minor precision differences)
                    if stored_conn.created_at:
                        assert loaded_conn.created_at is not None
                        # Compare timestamps with tolerance for microsecond differences
                        time_diff = abs((loaded_conn.created_at - stored_conn.created_at).total_seconds())
                        assert time_diff < 1.0  # Less than 1 second difference
                
                # Verify no extra connections were loaded
                for loaded_conn in loaded_connections:
                    assert loaded_conn.name in stored_by_name
                    
            finally:
                # Restore original session
                app.services.startup.async_session = original_session
                
        finally:
            await engine.dispose()

    @given(st.lists(database_connection_record(), min_size=1, max_size=2))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_18_startup_validation_identifies_issues(self, stored_connections):
        """
        Property 18 (Validation): Startup validation identifies connection issues
        
        For any set of stored connections, startup validation should correctly
        identify valid and invalid connections.
        
        **Validates: Requirements 8.2**
        """
        # Introduce some invalid connections by corrupting data
        corrupted_connections = []
        valid_count = 0
        invalid_count = 0
        
        for i, conn in enumerate(stored_connections):
            if i % 3 == 0:  # Corrupt every third connection
                # Create invalid connection (missing required fields)
                corrupted_conn = DatabaseConnection(
                    id=conn.id,
                    name="",  # Invalid empty name
                    url=conn.url,
                    description=conn.description,
                    is_active=conn.is_active,
                    created_at=conn.created_at
                )
                corrupted_connections.append(corrupted_conn)
                invalid_count += 1
            elif i % 3 == 1:  # Corrupt URL for some connections
                corrupted_conn = DatabaseConnection(
                    id=conn.id,
                    name=conn.name,
                    url="invalid-url-format",  # Invalid URL
                    description=conn.description,
                    is_active=conn.is_active,
                    created_at=conn.created_at
                )
                corrupted_connections.append(corrupted_conn)
                invalid_count += 1
            else:
                # Keep connection valid
                corrupted_connections.append(conn)
                valid_count += 1
        
        # Create test database with corrupted connections
        async_session_factory, engine = await create_test_db_with_connections(corrupted_connections)
        
        try:
            startup_service = StartupService()
            
            # Mock the async_session to use our test database
            import app.services.startup
            original_session = app.services.startup.async_session
            app.services.startup.async_session = async_session_factory
            
            try:
                # Load connections (should handle invalid ones gracefully)
                loaded_connections = await startup_service.load_stored_connections()
                
                # Should only load valid connections
                assert len(loaded_connections) == valid_count
                
                # Validate the loaded connections
                validation_result = await startup_service.validate_loaded_connections()
                
                # All loaded connections should be valid
                assert validation_result["valid_connections"] == len(loaded_connections)
                assert validation_result["invalid_connections"] == 0
                
                # Verify all loaded connections have required fields
                for conn in loaded_connections:
                    assert conn.name and len(conn.name.strip()) > 0
                    assert conn.url and len(conn.url.strip()) > 0
                    # Basic URL format check
                    assert "://" in conn.url
                    
            finally:
                # Restore original session
                app.services.startup.async_session = original_session
                
        finally:
            await engine.dispose()

    @pytest.mark.asyncio
    async def test_property_18_empty_database_startup(self):
        """
        Property 18 (Edge case): Empty database startup
        
        For an empty metadata store, startup should complete successfully
        with zero connections loaded.
        
        **Validates: Requirements 8.2**
        """
        # Create empty test database
        async_session_factory, engine = await create_test_db_with_connections([])
        
        try:
            startup_service = StartupService()
            
            # Mock the async_session to use our test database
            import app.services.startup
            original_session = app.services.startup.async_session
            app.services.startup.async_session = async_session_factory
            
            try:
                # Load connections from empty database
                loaded_connections = await startup_service.load_stored_connections()
                
                # Should return empty list
                assert len(loaded_connections) == 0
                assert isinstance(loaded_connections, list)
                
                # Validation should also work with empty list
                validation_result = await startup_service.validate_loaded_connections()
                assert validation_result["valid_connections"] == 0
                assert validation_result["invalid_connections"] == 0
                assert len(validation_result["warnings"]) == 0
                
            finally:
                # Restore original session
                app.services.startup.async_session = original_session
                
        finally:
            await engine.dispose()

    @given(st.lists(database_connection_record(), min_size=1, max_size=2))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_18_startup_status_tracking(self, stored_connections):
        """
        Property 18 (Status): Startup status tracking works correctly
        
        For any startup process, the service should correctly track
        startup completion status and loaded connection information.
        
        **Validates: Requirements 8.2**
        """
        # Create test database with connections
        async_session_factory, engine = await create_test_db_with_connections(stored_connections)
        
        try:
            # Create a fresh startup service instance for this test
            startup_service = StartupService()
            
            # Initially, startup should not be completed
            assert not startup_service.is_startup_completed()
            assert len(startup_service.get_startup_errors()) == 0
            assert len(startup_service.get_loaded_connections()) == 0
            
            # Mock the async_session to use our test database
            import app.services.startup
            original_session = app.services.startup.async_session
            app.services.startup.async_session = async_session_factory
            
            try:
                # Perform startup initialization (mock database init success)
                # We'll test just the connection loading part
                loaded_connections = await startup_service.load_stored_connections()
                
                # Manually update the startup service's internal state to simulate full startup
                startup_service._loaded_connections = loaded_connections
                
                # Verify status tracking
                status = await startup_service.get_startup_status()
                
                # Should track loaded connections correctly
                assert len(status["loaded_connections"]) == len(stored_connections)
                
                # Verify loaded connection information is complete
                for loaded_info in status["loaded_connections"]:
                    assert "name" in loaded_info
                    assert "description" in loaded_info
                    assert "is_active" in loaded_info
                    assert "created_at" in loaded_info
                    
                    # Find corresponding stored connection
                    stored_conn = next(
                        (conn for conn in stored_connections if conn.name == loaded_info["name"]),
                        None
                    )
                    assert stored_conn is not None
                    
                    # Verify information matches
                    assert loaded_info["name"] == stored_conn.name
                    assert loaded_info["description"] == stored_conn.description
                    assert loaded_info["is_active"] == stored_conn.is_active
                    
            finally:
                # Restore original session
                app.services.startup.async_session = original_session
                
        finally:
            await engine.dispose()

    @given(st.lists(database_connection_record(), min_size=0, max_size=2))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_18_startup_idempotency(self, stored_connections):
        """
        Property 18 (Idempotency): Multiple startup calls are idempotent
        
        For any set of stored connections, calling startup loading multiple
        times should produce consistent results.
        
        **Validates: Requirements 8.2**
        """
        # Create test database with connections
        async_session_factory, engine = await create_test_db_with_connections(stored_connections)
        
        try:
            startup_service = StartupService()
            
            # Mock the async_session to use our test database
            import app.services.startup
            original_session = app.services.startup.async_session
            app.services.startup.async_session = async_session_factory
            
            try:
                # Load connections multiple times
                first_load = await startup_service.load_stored_connections()
                second_load = await startup_service.load_stored_connections()
                third_load = await startup_service.load_stored_connections()
                
                # All loads should return the same data
                assert len(first_load) == len(second_load) == len(third_load)
                
                # Create comparison sets by name for easier verification
                first_names = {conn.name for conn in first_load}
                second_names = {conn.name for conn in second_load}
                third_names = {conn.name for conn in third_load}
                
                assert first_names == second_names == third_names
                
                # Verify detailed data consistency
                for i in range(len(first_load)):
                    first_conn = first_load[i]
                    second_conn = next(conn for conn in second_load if conn.name == first_conn.name)
                    third_conn = next(conn for conn in third_load if conn.name == first_conn.name)
                    
                    # All fields should be identical
                    assert first_conn.name == second_conn.name == third_conn.name
                    assert first_conn.url == second_conn.url == third_conn.url
                    assert first_conn.description == second_conn.description == third_conn.description
                    assert first_conn.is_active == second_conn.is_active == third_conn.is_active
                    assert first_conn.id == second_conn.id == third_conn.id
                    
            finally:
                # Restore original session
                app.services.startup.async_session = original_session
                
        finally:
            await engine.dispose()
