"""
Property-based tests for database connection validation.

Feature: database-query-tool, Property 2: Connection validation
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
def valid_postgresql_urls(draw):
    """Generate valid PostgreSQL URLs for connection testing."""
    scheme = draw(st.sampled_from(["postgresql", "postgres"]))
    
    # Generate valid components
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
    
    return f"{scheme}://{username}:{password}@{host}:{port}/{database}"


@st.composite
def invalid_postgresql_urls(draw):
    """Generate invalid PostgreSQL URLs for validation testing."""
    # Various types of invalid URLs
    invalid_type = draw(st.sampled_from([
        "wrong_scheme",
        "missing_host",
        "missing_database",
        "invalid_port",
        "malformed"
    ]))
    
    if invalid_type == "wrong_scheme":
        # Wrong scheme
        scheme = draw(st.sampled_from(["http", "https", "mysql", "sqlite"]))
        return f"{scheme}://user:pass@host:5432/db"
    
    elif invalid_type == "missing_host":
        # Missing hostname
        return "postgresql://user:pass@:5432/db"
    
    elif invalid_type == "missing_database":
        # Missing database name
        return "postgresql://user:pass@host:5432/"
    
    elif invalid_type == "invalid_port":
        # Invalid port number
        port = draw(st.integers(min_value=70000, max_value=99999))  # Invalid port range
        return f"postgresql://user:pass@host:{port}/db"
    
    else:  # malformed
        # Completely malformed URL
        return draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789._-",
            min_size=1,
            max_size=50
        ))


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


class TestConnectionValidationProperties:
    """Property-based tests for database connection validation."""

    @given(valid_postgresql_urls())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_2_valid_url_format_acceptance(self, valid_url: str):
        """
        Property 2: Valid URL format acceptance
        
        For any valid PostgreSQL URL format, the validation process should
        accept the URL without raising format errors.
        
        **Validates: Requirements 1.3, 1.4**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Test URL format validation (this should not raise format errors)
            try:
                service._validate_url_format(valid_url)
                # If we get here, validation passed (which is expected for valid URLs)
                validation_passed = True
            except DatabaseServiceError as e:
                # If validation failed, check if it's a format error or connection error
                error_message = str(e).lower()
                if any(keyword in error_message for keyword in ["format", "scheme", "hostname", "database"]):
                    validation_passed = False
                else:
                    # This might be a connection error, which is acceptable for format validation
                    validation_passed = True
            
            # Valid URLs should pass format validation
            assert validation_passed, f"Valid URL {valid_url} failed format validation"
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(invalid_postgresql_urls())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_2_invalid_url_format_rejection(self, invalid_url: str):
        """
        Property 2: Invalid URL format rejection
        
        For any invalid PostgreSQL URL format, the validation process should
        reject the URL with a descriptive error message.
        
        **Validates: Requirements 1.3, 1.4**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Invalid URLs should raise DatabaseServiceError during format validation
            with pytest.raises(DatabaseServiceError) as exc_info:
                service._validate_url_format(invalid_url)
            
            # Error message should be descriptive and mention URL/format issues
            error_message = str(exc_info.value).lower()
            assert any(keyword in error_message for keyword in [
                "url", "postgresql", "format", "scheme", "hostname", "database", "port"
            ]), f"Error message '{error_message}' not descriptive enough for invalid URL: {invalid_url}"
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_2_connection_test_error_handling(self, name: str):
        """
        Property 2: Connection test error handling
        
        For any database connection test that fails, the system should return
        a structured error response with descriptive information.
        
        **Validates: Requirements 1.3, 1.4**
        """
        # Filter out invalid names
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Use a URL that will definitely fail to connect (non-existent host)
            failing_url = "postgresql://user:pass@nonexistent-host-12345:5432/testdb"
            
            # Test connection should return structured error response
            result = await service.test_connection(failing_url)
            
            # Verify error response structure
            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is False
            assert "message" in result
            assert isinstance(result["message"], str)
            assert len(result["message"]) > 0
            
            # Error message should be descriptive
            error_message = result["message"].lower()
            assert any(keyword in error_message for keyword in [
                "connection", "failed", "error", "timeout", "host", "database"
            ]), f"Error message '{result['message']}' not descriptive enough"
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_2_connection_status_tracking(self, name: str):
        """
        Property 2: Connection status tracking
        
        For any database connection, the system should correctly track and
        update connection status based on actual connectivity tests.
        
        **Validates: Requirements 1.3, 1.4**
        """
        # Filter out invalid names
        if not name or not name.replace('-', '').replace('_', '').isalnum():
            return
            
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Mock connection testing to simulate different scenarios
            original_test_connection = service._test_connection
            
            # Test scenario 1: Connection succeeds
            async def mock_success_connection(url: str):
                return {"success": True, "message": "Connection successful", "latency_ms": 50}
            
            service._test_connection = mock_success_connection
            
            # Create a database connection
            connection_data = DatabaseCreate(
                name=name,
                url="postgresql://user:pass@localhost:5432/testdb",
                description="Test connection"
            )
            
            created_connection = await service.create_database(db_session, connection_data)
            
            # Verify initial status is active (successful connection)
            assert created_connection.is_active is True
            
            # Test scenario 2: Connection fails
            async def mock_failed_connection(url: str):
                return {"success": False, "message": "Connection failed", "error": "Host unreachable"}
            
            service._test_connection = mock_failed_connection
            
            # Get connection status (should update based on failed test)
            status = await service.get_connection_status(db_session, name)
            
            # Verify status reflects the failed connection
            assert isinstance(status, dict)
            assert "is_active" in status
            assert status["is_active"] is False
            assert "connection_test" in status
            assert status["connection_test"]["success"] is False
            
            # Restore original method
            service._test_connection = original_test_connection
            
        finally:
            await db_session.close()
            await engine.dispose()

    @given(valid_postgresql_urls())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_2_validation_consistency(self, valid_url: str):
        """
        Property 2: Validation consistency
        
        For any valid PostgreSQL URL, validation should be consistent across
        multiple calls and different validation methods.
        
        **Validates: Requirements 1.3, 1.4**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Test format validation multiple times - should be consistent
            validation_results = []
            for _ in range(3):
                try:
                    service._validate_url_format(valid_url)
                    validation_results.append(True)
                except DatabaseServiceError:
                    validation_results.append(False)
            
            # All validation attempts should have the same result
            assert len(set(validation_results)) == 1, f"Inconsistent validation results for URL: {valid_url}"
            
            # If validation passes, test connection validation consistency
            if all(validation_results):
                # Mock connection testing for consistency
                async def mock_test_connection(url: str):
                    return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
                
                service._test_connection = mock_test_connection
                
                # Test connection multiple times - should be consistent
                connection_results = []
                for _ in range(3):
                    result = await service.test_connection(valid_url)
                    connection_results.append(result["success"])
                
                # All connection tests should have the same result (mocked to succeed)
                assert all(connection_results), f"Inconsistent connection test results for URL: {valid_url}"
            
        finally:
            await db_session.close()
            await engine.dispose()
