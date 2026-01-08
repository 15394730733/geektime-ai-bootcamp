"""
Property-based tests for database connection management.

Feature: database-query-tool, Property 1: Database connection storage
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from pydantic import ValidationError
from app.services.database import DatabaseService, DatabaseServiceError
from app.schemas.database import DatabaseCreate
from app.models import Base


# Generators for property-based testing
@st.composite
def valid_database_connection_data(draw):
    """Generate valid database connection data."""
    # Generate valid name (alphanumeric, hyphens, underscores only)
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
        min_size=1,
        max_size=50
    ).filter(lambda x: x and x[0].isalnum() and x[-1].isalnum()))
    
    # Generate valid PostgreSQL URLs with simple ASCII characters
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
    
    return DatabaseCreate(
        name=name,
        url=url,
        description=description
    )


@st.composite
def invalid_database_urls(draw):
    """Generate invalid database URLs for testing validation."""
    invalid_schemes = ["http://", "https://", "mysql://", "sqlite://"]
    scheme = draw(st.sampled_from(invalid_schemes))
    
    rest = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789._-",
        min_size=1,
        max_size=50
    ))
    return f"{scheme}{rest}"


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


class TestDatabaseConnectionProperties:
    """Property-based tests for database connection management."""

    @given(valid_database_connection_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_1_database_connection_storage(self, connection_data: DatabaseCreate):
        """
        Property 1: Database connection storage
        
        For any valid database connection data (name, URL, description), 
        storing the connection should result in the data being retrievable 
        from the metadata store with all fields intact.
        
        **Validates: Requirements 1.1, 1.2**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Skip actual connection testing for property tests by mocking the connection test
            original_test_connection = service._test_connection
            
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            try:
                # Store the connection
                stored_connection = await service.create_database(db_session, connection_data)
                
                # Retrieve the connection
                retrieved_connection = await service.get_database(db_session, connection_data.name)
                
                # Verify all fields are intact
                assert retrieved_connection is not None
                assert retrieved_connection.name == connection_data.name
                assert retrieved_connection.url == connection_data.url
                assert retrieved_connection.description == connection_data.description
                assert retrieved_connection.id == stored_connection.id
                assert retrieved_connection.is_active is True  # Should default to active
                
                # Verify it appears in the list
                all_connections = await service.list_databases(db_session)
                connection_names = [conn.name for conn in all_connections]
                assert connection_data.name in connection_names
                
            finally:
                # Restore original method
                service._test_connection = original_test_connection
                
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50), invalid_database_urls())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_1_invalid_url_rejection(self, name: str, invalid_url: str):
        """
        Property 1 (Error case): Invalid URL rejection
        
        For any invalid database URL, the system should reject the connection
        with a descriptive error message.
        
        **Validates: Requirements 1.1, 1.2**
        """
        # Filter out valid names to avoid name validation errors
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            return
        
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Should raise ValidationError for invalid URLs (either at Pydantic or service level)
            with pytest.raises((DatabaseServiceError, ValidationError)) as exc_info:
                connection_data = DatabaseCreate(
                    name=name,
                    url=invalid_url,
                    description="Test connection"
                )
                await service.create_database(db_session, connection_data)
            
            # Error message should be descriptive
            error_message = str(exc_info.value)
            assert len(error_message) > 0
            assert any(keyword in error_message.lower() for keyword in [
                "url", "postgresql", "invalid", "format", "required", "postgres"
            ])
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(valid_database_connection_data(), valid_database_connection_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_1_name_uniqueness_enforcement(self, connection1: DatabaseCreate, 
                                                         connection2: DatabaseCreate):
        """
        Property 1 (Uniqueness): Name uniqueness enforcement
        
        For any two database connections with the same name, 
        the system should reject the second one.
        
        **Validates: Requirements 1.1, 1.2**
        """
        # Make sure both connections have the same name but different URLs
        connection2.name = connection1.name
        if connection2.url == connection1.url:
            connection2.url = connection2.url.replace("5432", "5433")  # Change port
        
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            try:
                # First connection should succeed
                await service.create_database(db_session, connection1)
                
                # Second connection with same name should fail
                with pytest.raises(DatabaseServiceError) as exc_info:
                    await service.create_database(db_session, connection2)
                
                # Error should mention name uniqueness
                error_message = str(exc_info.value)
                assert "already exists" in error_message.lower() or "unique" in error_message.lower()
                
            finally:
                # Restore original method
                service._test_connection = mock_test_connection
                
        finally:
            await db_session.close()
            await engine.dispose()

    @given(valid_database_connection_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_1_connection_update_preserves_data(self, connection_data: DatabaseCreate):
        """
        Property 1 (Update): Connection updates preserve data integrity
        
        For any valid database connection, updating it should preserve
        the connection ID and maintain data consistency.
        
        **Validates: Requirements 1.1, 1.2**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            try:
                # Create initial connection
                original_connection = await service.create_database(db_session, connection_data)
                original_id = original_connection.id
                
                # Update the connection
                updated_data = DatabaseCreate(
                    name=connection_data.name,
                    url=connection_data.url.replace("5432", "5433"),  # Change port
                    description="Updated description"
                )
                
                updated_connection = await service.update_database(db_session, connection_data.name, updated_data)
                
                # Verify update preserved ID and updated fields correctly
                assert updated_connection is not None
                assert updated_connection.id == original_id  # ID should be preserved
                assert updated_connection.name == updated_data.name
                assert updated_connection.url == updated_data.url
                assert updated_connection.description == updated_data.description
                
            finally:
                # Restore original method
                service._test_connection = mock_test_connection
                
        finally:
            await db_session.close()
            await engine.dispose()

    @given(valid_database_connection_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_1_connection_deletion_removes_data(self, connection_data: DatabaseCreate):
        """
        Property 1 (Deletion): Connection deletion removes all data
        
        For any stored database connection, deleting it should completely
        remove it from the metadata store.
        
        **Validates: Requirements 1.1, 1.2**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            try:
                # Create connection
                await service.create_database(db_session, connection_data)
                
                # Verify it exists
                retrieved = await service.get_database(db_session, connection_data.name)
                assert retrieved is not None
                
                # Delete the connection
                deletion_result = await service.delete_database(db_session, connection_data.name)
                assert deletion_result is True
                
                # Verify it no longer exists
                retrieved_after_deletion = await service.get_database(db_session, connection_data.name)
                assert retrieved_after_deletion is None
                
                # Verify it's not in the list
                all_connections = await service.list_databases(db_session)
                connection_names = [conn.name for conn in all_connections]
                assert connection_data.name not in connection_names
                
            finally:
                # Restore original method
                service._test_connection = mock_test_connection
                
        finally:
            await db_session.close()
            await engine.dispose()
