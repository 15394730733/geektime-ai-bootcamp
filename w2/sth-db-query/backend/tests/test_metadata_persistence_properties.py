"""
Property-based tests for metadata persistence.

Feature: database-query-tool, Property 19: Metadata persistence
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

from app.services.database import DatabaseService
from app.models import Base
from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate, Database


# Generators for property-based testing
@st.composite
def database_connection_data(draw):
    """Generate database connection data for testing."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    name = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
        min_size=1,
        max_size=20
    ).filter(lambda x: x and x[0].isalnum() and x[-1].isalnum()))
    
    # Ensure unique names
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
    
    return DatabaseCreate(
        name=name,
        url=url,
        description=description
    )


@st.composite
def metadata_structure(draw):
    """Generate metadata structure for testing."""
    num_tables = draw(st.integers(min_value=1, max_value=3))
    num_views = draw(st.integers(min_value=0, max_value=2))
    
    tables = []
    for i in range(num_tables):
        table_name = f"table_{i}"
        num_columns = draw(st.integers(min_value=1, max_value=4))
        columns = []
        for j in range(num_columns):
            columns.append({
                "name": f"column_{j}",
                "data_type": draw(st.sampled_from(["varchar", "integer", "boolean", "timestamp"])),
                "is_nullable": draw(st.booleans()),
                "is_primary_key": j == 0,  # First column is PK
                "default_value": None
            })
        
        tables.append({
            "name": table_name,
            "schema": "public",
            "columns": columns
        })
    
    views = []
    for i in range(num_views):
        view_name = f"view_{i}"
        num_columns = draw(st.integers(min_value=1, max_value=3))
        columns = []
        for j in range(num_columns):
            columns.append({
                "name": f"view_column_{j}",
                "data_type": draw(st.sampled_from(["varchar", "integer", "boolean"])),
                "is_nullable": True,
                "is_primary_key": False,
                "default_value": None
            })
        
        views.append({
            "name": view_name,
            "schema": "public",
            "columns": columns
        })
    
    return {"tables": tables, "views": views}


async def create_test_db():
    """Create a test database session."""
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
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    return async_session, engine


class TestMetadataPersistenceProperties:
    """Property-based tests for metadata persistence."""

    @given(database_connection_data(), metadata_structure())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_19_metadata_persistence_on_create(self, db_data, metadata_structure):
        """
        Property 19: Metadata persistence on database creation
        
        For any database connection created, metadata should be automatically
        extracted and persisted to the SQLite database.
        
        **Validates: Requirements 8.3**
        """
        async_session_factory, engine = await create_test_db()
        
        try:
            service = DatabaseService()
            
            # Mock connection test to always succeed
            async def mock_test_connection(url):
                return {"success": True, "message": "Connection successful"}
            
            service._test_connection = mock_test_connection
            
            # Mock metadata extraction
            def mock_extract_metadata(database_url: str, conn_id: str):
                result = []
                for table in metadata_structure["tables"]:
                    result.append({
                        "connection_id": conn_id,
                        "object_type": "table",
                        "object_name": table["name"],
                        "schema_name": table["schema"],
                        "columns": table["columns"]
                    })
                for view in metadata_structure["views"]:
                    result.append({
                        "connection_id": conn_id,
                        "object_type": "view",
                        "object_name": view["name"],
                        "schema_name": view["schema"],
                        "columns": view["columns"]
                    })
                return result
            
            service._extract_database_metadata = mock_extract_metadata
            
            async with async_session_factory() as db_session:
                # Create database connection
                created_db = await service.create_database(db_session, db_data)
                
                # Verify database was created
                assert created_db is not None
                assert created_db.name == db_data.name
                
                # Trigger metadata extraction (simulating what happens in the API)
                await service.refresh_database_metadata(db_session, created_db.url, created_db.id)
                
                # Verify metadata was persisted
                metadata_result = await service.get_database_metadata(db_session, created_db.name)
                
                # Verify metadata structure matches what was extracted
                assert metadata_result is not None
                assert "tables" in metadata_result
                assert "views" in metadata_result
                
                # Verify table count and structure
                assert len(metadata_result["tables"]) == len(metadata_structure["tables"])
                for i, table in enumerate(metadata_result["tables"]):
                    expected_table = metadata_structure["tables"][i]
                    assert table["name"] == expected_table["name"]
                    assert table["schema"] == expected_table["schema"]
                    assert len(table["columns"]) == len(expected_table["columns"])
                
                # Verify view count and structure
                assert len(metadata_result["views"]) == len(metadata_structure["views"])
                for i, view in enumerate(metadata_result["views"]):
                    expected_view = metadata_structure["views"][i]
                    assert view["name"] == expected_view["name"]
                    assert view["schema"] == expected_view["schema"]
                    assert len(view["columns"]) == len(expected_view["columns"])
                
        finally:
            await engine.dispose()

    @given(database_connection_data(), metadata_structure())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_19_metadata_persistence_on_update(self, db_data, metadata_structure):
        """
        Property 19: Metadata persistence on database update
        
        For any database connection that is updated with a new URL,
        metadata should be refreshed and persisted to the SQLite database.
        
        **Validates: Requirements 8.3**
        """
        async_session_factory, engine = await create_test_db()
        
        try:
            service = DatabaseService()
            
            # Mock connection test to always succeed
            async def mock_test_connection(url):
                return {"success": True, "message": "Connection successful"}
            
            service._test_connection = mock_test_connection
            
            # Mock metadata extraction - different metadata for different URLs
            def mock_extract_metadata(database_url: str, conn_id: str):
                # Return different metadata based on URL to simulate different databases
                if "updated" in database_url:
                    # Return updated metadata structure
                    result = []
                    for table in metadata_structure["tables"]:
                        # Add an extra column to simulate schema change
                        updated_columns = table["columns"] + [{
                            "name": "updated_column",
                            "data_type": "varchar",
                            "is_nullable": True,
                            "is_primary_key": False,
                            "default_value": None
                        }]
                        result.append({
                            "connection_id": conn_id,
                            "object_type": "table",
                            "object_name": table["name"],
                            "schema_name": table["schema"],
                            "columns": updated_columns
                        })
                    return result
                else:
                    # Return original metadata
                    result = []
                    for table in metadata_structure["tables"]:
                        result.append({
                            "connection_id": conn_id,
                            "object_type": "table",
                            "object_name": table["name"],
                            "schema_name": table["schema"],
                            "columns": table["columns"]
                        })
                    return result
            
            service._extract_database_metadata = mock_extract_metadata
            
            async with async_session_factory() as db_session:
                # Create initial database connection
                created_db = await service.create_database(db_session, db_data)
                await service.refresh_database_metadata(db_session, created_db.url, created_db.id)
                
                # Get initial metadata
                initial_metadata = await service.get_database_metadata(db_session, created_db.name)
                initial_column_count = len(initial_metadata["tables"][0]["columns"]) if initial_metadata["tables"] else 0
                
                # Update database with new URL
                updated_data = DatabaseCreate(
                    name=db_data.name,
                    url=db_data.url.replace("://", "://updated_"),  # Change URL to trigger metadata refresh
                    description=db_data.description
                )
                
                updated_db = await service.update_database(db_session, db_data.name, updated_data)
                
                # Verify database was updated
                assert updated_db is not None
                assert updated_db.url == updated_data.url
                
                # Get updated metadata
                updated_metadata = await service.get_database_metadata(db_session, created_db.name)
                
                # Verify metadata was refreshed and persisted
                assert updated_metadata is not None
                if updated_metadata["tables"]:
                    updated_column_count = len(updated_metadata["tables"][0]["columns"])
                    # Should have one more column due to our mock implementation
                    assert updated_column_count == initial_column_count + 1
                
        finally:
            await engine.dispose()

    @given(database_connection_data(), metadata_structure())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_19_metadata_persistence_across_sessions(self, db_data, metadata_structure):
        """
        Property 19: Metadata persistence across database sessions
        
        For any persisted metadata, it should remain available across
        different database sessions, ensuring true persistence.
        
        **Validates: Requirements 8.3**
        """
        async_session_factory, engine = await create_test_db()
        
        try:
            service = DatabaseService()
            
            # Mock connection test to always succeed
            async def mock_test_connection(url):
                return {"success": True, "message": "Connection successful"}
            
            service._test_connection = mock_test_connection
            
            # Mock metadata extraction
            def mock_extract_metadata(database_url: str, conn_id: str):
                result = []
                for table in metadata_structure["tables"]:
                    result.append({
                        "connection_id": conn_id,
                        "object_type": "table",
                        "object_name": table["name"],
                        "schema_name": table["schema"],
                        "columns": table["columns"]
                    })
                return result
            
            service._extract_database_metadata = mock_extract_metadata
            
            # First session - create and persist metadata
            async with async_session_factory() as db_session1:
                created_db = await service.create_database(db_session1, db_data)
                await service.refresh_database_metadata(db_session1, created_db.url, created_db.id)
                
                # Get metadata in first session
                metadata_session1 = await service.get_database_metadata(db_session1, created_db.name)
                
                # Verify metadata exists
                assert metadata_session1 is not None
                assert len(metadata_session1["tables"]) == len(metadata_structure["tables"])
            
            # Second session - verify metadata persisted
            async with async_session_factory() as db_session2:
                # Get metadata in second session (different session object)
                metadata_session2 = await service.get_database_metadata(db_session2, db_data.name)
                
                # Verify metadata persisted across sessions
                assert metadata_session2 is not None
                assert len(metadata_session2["tables"]) == len(metadata_structure["tables"])
                
                # Verify metadata content is identical
                assert metadata_session1["database"] == metadata_session2["database"]
                assert len(metadata_session1["tables"]) == len(metadata_session2["tables"])
                
                # Verify table details match
                for i, table in enumerate(metadata_session1["tables"]):
                    session2_table = metadata_session2["tables"][i]
                    assert table["name"] == session2_table["name"]
                    assert table["schema"] == session2_table["schema"]
                    assert len(table["columns"]) == len(session2_table["columns"])
                
        finally:
            await engine.dispose()

    @given(database_connection_data())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_19_ensure_metadata_persistence_method(self, db_data):
        """
        Property 19: Ensure metadata persistence method works correctly
        
        For any database connection, the ensure_metadata_persistence method
        should correctly identify missing metadata and refresh it.
        
        **Validates: Requirements 8.3**
        """
        async_session_factory, engine = await create_test_db()
        
        try:
            service = DatabaseService()
            
            # Mock connection test to always succeed
            async def mock_test_connection(url):
                return {"success": True, "message": "Connection successful"}
            
            service._test_connection = mock_test_connection
            
            # Mock metadata extraction
            def mock_extract_metadata(database_url: str, conn_id: str):
                return [{
                    "connection_id": conn_id,
                    "object_type": "table",
                    "object_name": "test_table",
                    "schema_name": "public",
                    "columns": [{
                        "name": "id",
                        "data_type": "integer",
                        "is_nullable": False,
                        "is_primary_key": True,
                        "default_value": None
                    }]
                }]
            
            service._extract_database_metadata = mock_extract_metadata
            
            async with async_session_factory() as db_session:
                # Create database connection without metadata
                created_db = await service.create_database(db_session, db_data)
                
                # Verify no metadata exists initially
                initial_metadata = await service.get_database_metadata(db_session, created_db.name)
                assert not initial_metadata or not initial_metadata.get("tables")
                
                # Use ensure_metadata_persistence method
                result = await service.ensure_metadata_persistence(db_session, created_db.name)
                
                # Verify method detected missing metadata and refreshed it
                assert result["metadata_refreshed"] is True
                assert result["tables_count"] == 1
                assert "missing" in result["message"]
                
                # Verify metadata now exists
                final_metadata = await service.get_database_metadata(db_session, created_db.name)
                assert final_metadata is not None
                assert len(final_metadata["tables"]) == 1
                assert final_metadata["tables"][0]["name"] == "test_table"
                
                # Call ensure_metadata_persistence again - should not refresh
                result2 = await service.ensure_metadata_persistence(db_session, created_db.name)
                assert result2["metadata_refreshed"] is False
                assert "already exists" in result2["message"]
                
        finally:
            await engine.dispose()
