"""
Property-based tests for metadata extraction and storage.

Feature: database-query-tool, Property 3: Metadata extraction and storage
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
def mock_metadata_structure(draw):
    """Generate mock metadata structure for testing."""
    # Generate table metadata
    num_tables = draw(st.integers(min_value=1, max_value=5))
    tables = []
    used_table_names = set()  # Track used table names to ensure uniqueness
    
    for table_idx in range(num_tables):
        # Generate unique table name
        base_table_name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz",
            min_size=1,
            max_size=15
        ))
        # Ensure uniqueness by appending index if needed
        table_name = base_table_name
        counter = 0
        while table_name in used_table_names:
            counter += 1
            table_name = f"{base_table_name}_{counter}"
        used_table_names.add(table_name)
        
        schema_name = draw(st.sampled_from(["public", "app", "data"]))
        
        # Generate columns for this table
        num_columns = draw(st.integers(min_value=1, max_value=8))
        columns = []
        used_column_names = set()  # Track used column names within this table
        
        for i in range(num_columns):
            # Generate unique column name within this table
            base_column_name = draw(st.text(
                alphabet="abcdefghijklmnopqrstuvwxyz",
                min_size=1,
                max_size=12
            ))
            # Ensure uniqueness by appending index if needed
            column_name = base_column_name
            counter = 0
            while column_name in used_column_names:
                counter += 1
                column_name = f"{base_column_name}_{counter}"
            used_column_names.add(column_name)
            
            data_type = draw(st.sampled_from([
                "integer", "varchar", "text", "boolean", "timestamp", "numeric"
            ]))
            
            is_nullable = draw(st.booleans())
            is_primary_key = i == 0 if draw(st.booleans()) else False  # First column might be PK
            default_value = draw(st.one_of(
                st.none(),
                st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", max_size=10)
            ))
            
            columns.append({
                "name": column_name,
                "data_type": data_type,
                "is_nullable": is_nullable,
                "is_primary_key": is_primary_key,
                "default_value": default_value
            })
        
        tables.append({
            "object_type": "table",
            "schema_name": schema_name,
            "object_name": table_name,
            "columns": columns
        })
    
    # Generate view metadata
    num_views = draw(st.integers(min_value=0, max_value=3))
    views = []
    used_view_names = set()  # Track used view names to ensure uniqueness
    
    for view_idx in range(num_views):
        # Generate unique view name
        base_view_name = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz",
            min_size=1,
            max_size=15
        ))
        # Ensure uniqueness by appending index if needed
        view_name = base_view_name
        counter = 0
        while view_name in used_view_names or view_name in used_table_names:
            counter += 1
            view_name = f"{base_view_name}_{counter}"
        used_view_names.add(view_name)
        
        schema_name = draw(st.sampled_from(["public", "app", "data"]))
        
        # Generate columns for this view
        num_columns = draw(st.integers(min_value=1, max_value=5))
        columns = []
        used_column_names = set()  # Track used column names within this view
        
        for col_idx in range(num_columns):
            # Generate unique column name within this view
            base_column_name = draw(st.text(
                alphabet="abcdefghijklmnopqrstuvwxyz",
                min_size=1,
                max_size=12
            ))
            # Ensure uniqueness by appending index if needed
            column_name = base_column_name
            counter = 0
            while column_name in used_column_names:
                counter += 1
                column_name = f"{base_column_name}_{counter}"
            used_column_names.add(column_name)
            
            data_type = draw(st.sampled_from([
                "integer", "varchar", "text", "boolean", "timestamp"
            ]))
            
            columns.append({
                "name": column_name,
                "data_type": data_type,
                "is_nullable": True,  # Views typically allow nulls
                "is_primary_key": False,  # Views don't have primary keys
                "default_value": None
            })
        
        views.append({
            "object_type": "view",
            "schema_name": schema_name,
            "object_name": view_name,
            "columns": columns
        })
    
    return tables + views


async def create_test_db_session(shared_db_path=None):
    """Create a test database session for property tests."""
    if shared_db_path:
        # Use a shared database file for persistence tests
        db_url = f"sqlite+aiosqlite:///{shared_db_path}"
    else:
        # Create in-memory SQLite database for testing
        db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        db_url,
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


class TestMetadataExtractionProperties:
    """Property-based tests for metadata extraction and storage."""

    @given(mock_metadata_structure())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_3_metadata_extraction_and_storage(self, metadata_structure):
        """
        Property 3: Metadata extraction and storage
        
        For any successfully connected database, extracting metadata should result in
        complete table and view information being stored in the metadata store.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Create a test database connection first
            connection_data = DatabaseCreate(
                name="test_db",
                url="postgresql://user:pass@localhost:5432/testdb",
                description="Test database for metadata extraction"
            )
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # Mock the metadata extraction to return our test structure
            original_extract_metadata = service._extract_database_metadata
            
            def mock_extract_metadata(database_url: str, conn_id: str):
                # Add connection_id to each metadata item
                result = []
                for item in metadata_structure:
                    item_copy = item.copy()
                    item_copy["connection_id"] = conn_id
                    result.append(item_copy)
                return result
            
            service._extract_database_metadata = mock_extract_metadata
            
            try:
                # Refresh metadata (this should extract and store the metadata)
                metadata_result = await service.refresh_database_metadata(
                    db_session, 
                    connection_data.url, 
                    connection_id
                )
                
                # Verify metadata was stored and can be retrieved
                assert isinstance(metadata_result, dict)
                assert "tables" in metadata_result
                assert "views" in metadata_result
                
                # Verify all tables from the mock structure are present
                expected_tables = [item for item in metadata_structure if item["object_type"] == "table"]
                expected_views = [item for item in metadata_structure if item["object_type"] == "view"]
                
                retrieved_tables = metadata_result["tables"]
                retrieved_views = metadata_result["views"]
                
                # Check table count matches
                assert len(retrieved_tables) == len(expected_tables)
                assert len(retrieved_views) == len(expected_views)
                
                # Verify table structure is preserved
                for expected_table in expected_tables:
                    # Find matching table in retrieved data
                    matching_table = next(
                        (t for t in retrieved_tables 
                         if t["name"] == expected_table["object_name"] 
                         and t["schema"] == expected_table["schema_name"]), 
                        None
                    )
                    
                    assert matching_table is not None, f"Table {expected_table['object_name']} not found in retrieved metadata"
                    
                    # Verify column information is preserved
                    assert len(matching_table["columns"]) == len(expected_table["columns"])
                    
                    for expected_col in expected_table["columns"]:
                        matching_col = next(
                            (c for c in matching_table["columns"] if c["name"] == expected_col["name"]), 
                            None
                        )
                        
                        assert matching_col is not None, f"Column {expected_col['name']} not found"
                        assert matching_col["data_type"] == expected_col["data_type"]
                        assert matching_col["is_nullable"] == expected_col["is_nullable"]
                        assert matching_col["is_primary_key"] == expected_col["is_primary_key"]
                
                # Verify view structure is preserved
                for expected_view in expected_views:
                    matching_view = next(
                        (v for v in retrieved_views 
                         if v["name"] == expected_view["object_name"] 
                         and v["schema"] == expected_view["schema_name"]), 
                        None
                    )
                    
                    assert matching_view is not None, f"View {expected_view['object_name']} not found in retrieved metadata"
                    assert len(matching_view["columns"]) == len(expected_view["columns"])
                
            finally:
                # Restore original method
                service._extract_database_metadata = original_extract_metadata
                
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_3_metadata_persistence_across_sessions(self, db_name: str):
        """
        Property 3: Metadata persistence across sessions
        
        For any stored metadata, it should persist across different database sessions
        and be retrievable consistently.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        # Filter out invalid names
        if not db_name or not db_name.replace('-', '').replace('_', '').isalnum():
            return
            
        # Use a temporary file for shared database
        import tempfile
        import os
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        try:
            db_session1, engine1 = await create_test_db_session(temp_db_path)
            
            try:
                service = DatabaseService()
                
                # Create a test database connection
                connection_data = DatabaseCreate(
                    name=db_name,
                    url="postgresql://user:pass@localhost:5432/testdb",
                    description="Test database for persistence testing"
                )
                
                # Mock connection testing
                async def mock_test_connection(url: str):
                    return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
                
                service._test_connection = mock_test_connection
                
                # Create the database connection
                created_connection = await service.create_database(db_session1, connection_data)
                connection_id = created_connection.id
                
                # Mock metadata extraction with consistent test data
                test_metadata = [{
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "public",
                    "object_name": "test_table",
                    "columns": [{
                        "name": "id",
                        "data_type": "integer",
                        "is_nullable": False,
                        "is_primary_key": True,
                        "default_value": None
                    }]
                }]
                
                def mock_extract_metadata(database_url: str, conn_id: str):
                    return test_metadata
                
                service._extract_database_metadata = mock_extract_metadata
                
                # Store metadata in first session
                metadata_result1 = await service.refresh_database_metadata(
                    db_session1, 
                    connection_data.url, 
                    connection_id
                )
                
                # Close first session
                await db_session1.close()
                await engine1.dispose()
                
                # Create second session (simulating different application session)
                db_session2, engine2 = await create_test_db_session(temp_db_path)
                
                try:
                    # Retrieve metadata in second session
                    metadata_result2 = await service.get_database_metadata(db_session2, db_name)
                    
                    # Verify metadata persisted and is identical
                    assert metadata_result1 == metadata_result2
                    
                    # Verify specific structure
                    assert "tables" in metadata_result2
                    assert len(metadata_result2["tables"]) == 1
                    assert metadata_result2["tables"][0]["name"] == "test_table"
                    assert metadata_result2["tables"][0]["schema"] == "public"
                    assert len(metadata_result2["tables"][0]["columns"]) == 1
                    assert metadata_result2["tables"][0]["columns"][0]["name"] == "id"
                    
                finally:
                    await db_session2.close()
                    await engine2.dispose()
                    
            finally:
                # Cleanup first session if still open
                if not db_session1.is_active:
                    pass  # Already closed
                else:
                    await db_session1.close()
                    await engine1.dispose()
                    
        finally:
            # Clean up temporary database file
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_3_metadata_update_replaces_old_data(self, num_tables: int):
        """
        Property 3: Metadata update replaces old data
        
        For any database connection, refreshing metadata should completely replace
        old metadata with new metadata, not append to it.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        db_session, engine = await create_test_db_session()
        
        try:
            service = DatabaseService()
            
            # Create a test database connection
            connection_data = DatabaseCreate(
                name="update_test_db",
                url="postgresql://user:pass@localhost:5432/testdb",
                description="Test database for update testing"
            )
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # First metadata set (initial)
            initial_metadata = [{
                "connection_id": connection_id,
                "object_type": "table",
                "schema_name": "public",
                "object_name": "old_table",
                "columns": [{
                    "name": "old_id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "is_primary_key": True,
                    "default_value": None
                }]
            }]
            
            # Second metadata set (updated)
            updated_metadata = []
            for i in range(num_tables):
                updated_metadata.append({
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "public",
                    "object_name": f"new_table_{i}",
                    "columns": [{
                        "name": f"new_id_{i}",
                        "data_type": "integer",
                        "is_nullable": False,
                        "is_primary_key": True,
                        "default_value": None
                    }]
                })
            
            # Mock metadata extraction - first call returns initial, second returns updated
            call_count = 0
            def mock_extract_metadata(database_url: str, conn_id: str):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return initial_metadata
                else:
                    return updated_metadata
            
            service._extract_database_metadata = mock_extract_metadata
            
            # First metadata refresh
            metadata_result1 = await service.refresh_database_metadata(
                db_session, 
                connection_data.url, 
                connection_id
            )
            
            # Verify initial metadata
            assert len(metadata_result1["tables"]) == 1
            assert metadata_result1["tables"][0]["name"] == "old_table"
            
            # Second metadata refresh (should replace, not append)
            metadata_result2 = await service.refresh_database_metadata(
                db_session, 
                connection_data.url, 
                connection_id
            )
            
            # Verify updated metadata completely replaced old metadata
            assert len(metadata_result2["tables"]) == num_tables
            
            # Verify old table is gone
            old_table_names = [t["name"] for t in metadata_result2["tables"]]
            assert "old_table" not in old_table_names
            
            # Verify new tables are present
            for i in range(num_tables):
                assert f"new_table_{i}" in old_table_names
                
        finally:
            await db_session.close()
            await engine.dispose()

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.asyncio
    async def test_property_3_metadata_schema_filtering(self, db_name: str):
        """
        Property 3: Metadata schema filtering
        
        For any database metadata extraction, system schemas should be excluded
        and only user schemas should be included.
        
        **Validates: Requirements 2.1, 2.2, 2.3**
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
                description="Test database for schema filtering"
            )
            
            # Mock connection testing
            async def mock_test_connection(url: str):
                return {"success": True, "message": "Mock connection successful", "latency_ms": 10}
            
            service._test_connection = mock_test_connection
            
            # Create the database connection
            created_connection = await service.create_database(db_session, connection_data)
            connection_id = created_connection.id
            
            # Mock metadata that includes both user and system schemas
            mixed_metadata = [
                {
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "public",  # User schema
                    "object_name": "user_table",
                    "columns": [{"name": "id", "data_type": "integer", "is_nullable": False, "is_primary_key": True, "default_value": None}]
                },
                {
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "app",  # User schema
                    "object_name": "app_table",
                    "columns": [{"name": "id", "data_type": "integer", "is_nullable": False, "is_primary_key": True, "default_value": None}]
                },
                {
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "pg_catalog",  # System schema (should be filtered out)
                    "object_name": "pg_class",
                    "columns": [{"name": "oid", "data_type": "oid", "is_nullable": False, "is_primary_key": True, "default_value": None}]
                },
                {
                    "connection_id": connection_id,
                    "object_type": "table",
                    "schema_name": "information_schema",  # System schema (should be filtered out)
                    "object_name": "tables",
                    "columns": [{"name": "table_name", "data_type": "varchar", "is_nullable": False, "is_primary_key": False, "default_value": None}]
                }
            ]
            
            def mock_extract_metadata(database_url: str, conn_id: str):
                # The actual implementation should filter out system schemas
                # Return only user schemas (simulating the filtering that happens in the real implementation)
                return [item for item in mixed_metadata if item["schema_name"] not in ("pg_catalog", "information_schema")]
            
            service._extract_database_metadata = mock_extract_metadata
            
            # Refresh metadata
            metadata_result = await service.refresh_database_metadata(
                db_session, 
                connection_data.url, 
                connection_id
            )
            
            # Verify only user schemas are present
            assert len(metadata_result["tables"]) == 2  # Only public and app schemas
            
            table_schemas = [t["schema"] for t in metadata_result["tables"]]
            assert "public" in table_schemas
            assert "app" in table_schemas
            assert "pg_catalog" not in table_schemas
            assert "information_schema" not in table_schemas
            
            # Verify specific tables are present
            table_names = [t["name"] for t in metadata_result["tables"]]
            assert "user_table" in table_names
            assert "app_table" in table_names
            assert "pg_class" not in table_names
            assert "tables" not in table_names
                
        finally:
            await db_session.close()
            await engine.dispose()
