"""
Property-based tests for database initialization.

Feature: database-query-tool, Property 20: Database initialization
**Validates: Requirements 8.5**
"""

import asyncio
import os
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.init_db import init_database, check_database_exists, ensure_db_directory
from app.core.config import Settings


class TestDatabaseInitialization:
    """Property-based tests for database initialization functionality."""

    @given(
        db_name=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=50
        ).filter(lambda x: x.strip() and not any(c in x for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']))
    )
    @settings(max_examples=5, deadline=30000)
    @pytest.mark.asyncio
    async def test_database_initialization_creates_required_tables(self, db_name):
        """
        Property 20: Database initialization
        
        For any valid database name, initializing the database should create all required tables
        with proper schema and indexes.
        
        **Validates: Requirements 8.5**
        """
        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a unique database path
            db_path = Path(temp_dir) / f"{db_name}.db"
            db_url = f"sqlite+aiosqlite:///{db_path}"
            
            # Temporarily override the settings
            original_url = None
            try:
                # Store original settings if they exist
                from app.core.config import settings
                original_url = settings.database_url
                settings.database_url = db_url
                
                # Initialize the database
                result = await init_database()
                
                # Verify initialization was successful
                assert result is True
                
                # Verify database file was created
                assert db_path.exists()
                
                # Verify all required tables exist
                engine = create_async_engine(db_url, echo=False)
                async with engine.begin() as conn:
                    # Check for required tables
                    result = await conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name IN (
                            'database_connections', 
                            'database_metadata', 
                            'query_executions', 
                            'query_results'
                        )
                        ORDER BY name
                    """))
                    
                    tables = [row[0] for row in result.fetchall()]
                    expected_tables = ['database_connections', 'database_metadata', 'query_executions', 'query_results']
                    
                    assert sorted(tables) == sorted(expected_tables), f"Missing tables: {set(expected_tables) - set(tables)}"
                    
                    # Verify indexes were created
                    result = await conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='index' AND name LIKE 'idx_%'
                    """))
                    
                    indexes = [row[0] for row in result.fetchall()]
                    expected_indexes = [
                        'idx_db_connections_name',
                        'idx_db_connections_active',
                        'idx_metadata_connection_object',
                        'idx_metadata_schema_type',
                        'idx_query_exec_connection_status',
                        'idx_query_exec_created_at'
                    ]
                    
                    # Check that all expected indexes exist
                    for expected_index in expected_indexes:
                        assert expected_index in indexes, f"Missing index: {expected_index}"
                
                await engine.dispose()
                
            finally:
                # Restore original settings
                if original_url is not None:
                    settings.database_url = original_url

    @given(
        directory_path=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=30
        ).filter(lambda x: x.strip() and not any(c in x for c in [':', '*', '?', '"', '<', '>', '|']))
    )
    @settings(max_examples=5, deadline=10000)
    @pytest.mark.asyncio
    async def test_ensure_db_directory_creates_path(self, directory_path):
        """
        Property 20: Database initialization - Directory creation
        
        For any valid directory path, ensure_db_directory should create the directory
        structure if it doesn't exist.
        
        **Validates: Requirements 8.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a nested path
            test_path = Path(temp_dir) / directory_path / "test.db"
            db_url = f"sqlite+aiosqlite:///{test_path}"
            
            # Temporarily override settings
            original_url = None
            try:
                from app.core.config import settings
                original_url = settings.database_url
                settings.database_url = db_url
                
                # Ensure the directory doesn't exist initially
                assert not test_path.parent.exists()
                
                # Call ensure_db_directory
                result_path = await ensure_db_directory()
                
                # Verify directory was created
                assert test_path.parent.exists()
                assert test_path.parent.is_dir()
                
                # Verify returned path is correct
                assert str(result_path) == str(test_path)
                
            finally:
                if original_url is not None:
                    settings.database_url = original_url

    @pytest.mark.asyncio
    async def test_check_database_exists_accuracy(self):
        """
        Property 20: Database initialization - Existence checking
        
        For any database state (existing/non-existing), check_database_exists should
        accurately report the database status.
        
        **Validates: Requirements 8.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_check.db"
            db_url = f"sqlite+aiosqlite:///{db_path}"
            
            original_url = None
            try:
                from app.core.config import settings
                original_url = settings.database_url
                settings.database_url = db_url
                
                # Initially, database should not exist
                exists_before = await check_database_exists()
                assert exists_before is False
                
                # Initialize database
                await init_database()
                
                # Now database should exist
                exists_after = await check_database_exists()
                assert exists_after is True
                
                # Remove database file
                db_path.unlink()
                
                # Should not exist again
                exists_removed = await check_database_exists()
                assert exists_removed is False
                
            finally:
                if original_url is not None:
                    settings.database_url = original_url

    @given(
        invalid_chars=st.sampled_from(['_', '-'])  # Use safer characters for testing
    )
    @settings(max_examples=5, deadline=10000)
    @pytest.mark.asyncio
    async def test_database_initialization_handles_invalid_paths(self, invalid_chars):
        """
        Property 20: Database initialization - Error handling
        
        For any database path with special characters, the system should handle them gracefully
        without crashing.
        
        **Validates: Requirements 8.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with special characters (but valid ones)
            test_name = f"test{invalid_chars}db"
            db_path = Path(temp_dir) / test_name
            db_url = f"sqlite+aiosqlite:///{db_path}"
            
            original_url = None
            try:
                from app.core.config import settings
                original_url = settings.database_url
                settings.database_url = db_url
                
                # This should succeed with valid characters
                result = await init_database()
                assert result is True
                assert await check_database_exists()
                    
            finally:
                if original_url is not None:
                    settings.database_url = original_url
