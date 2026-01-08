"""
Database initialization module.

This module provides functions to initialize the SQLite database schema
using SQLAlchemy models. It ensures the database is created with proper
tables, indexes, and constraints.
"""

import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from .config import settings
from ..models import Base


async def ensure_db_directory():
    """Ensure the database directory exists."""
    # Extract directory from database URL
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    db_dir = Path(db_path).parent
    
    # Create directory if it doesn't exist
    db_dir.mkdir(parents=True, exist_ok=True)
    
    return db_path


async def init_database():
    """
    Initialize the SQLite database with required schema.
    
    Creates all tables defined in SQLAlchemy models and sets up
    necessary indexes for optimal performance.
    """
    try:
        # Ensure database directory exists
        db_path = await ensure_db_directory()
        
        # Create async engine
        engine = create_async_engine(
            settings.database_url,
            echo=settings.DEBUG,
            future=True,
        )
        
        # Create all tables
        async with engine.begin() as conn:
            # Drop all tables first (for clean initialization)
            await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Create additional indexes for performance
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_db_connections_name 
                ON database_connections(name)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_db_connections_active 
                ON database_connections(is_active)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_metadata_connection_object 
                ON database_metadata(connection_id, object_name)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_metadata_schema_type 
                ON database_metadata(schema_name, object_type)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_query_exec_connection_status 
                ON query_executions(connection_id, execution_status)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_query_exec_created_at 
                ON query_executions(created_at DESC)
            """))
        
        await engine.dispose()
        
        print(f"✅ Database initialized successfully at: {db_path}")
        print("📊 Created tables:")
        print("   - database_connections")
        print("   - database_metadata") 
        print("   - query_executions")
        print("   - query_results")
        print("📈 Created indexes for optimal performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


async def check_database_exists():
    """
    Check if the database exists and has the required tables.
    
    Returns:
        bool: True if database exists with all required tables, False otherwise.
    """
    try:
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        
        # Check if database file exists
        if not Path(db_path).exists():
            return False
            
        # Create engine and check tables
        engine = create_async_engine(settings.database_url, echo=False)
        
        async with engine.begin() as conn:
            # Check if all required tables exist
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'database_connections', 
                    'database_metadata', 
                    'query_executions', 
                    'query_results'
                )
            """))
            
            tables = [row[0] for row in result.fetchall()]
            required_tables = ['database_connections', 'database_metadata', 'query_executions', 'query_results']
            
        await engine.dispose()
        
        return len(tables) == len(required_tables)
        
    except Exception:
        return False


async def init_database_if_needed():
    """
    Initialize database only if it doesn't exist or is incomplete.
    
    This function is safe to call during application startup as it
    only initializes the database if needed.
    """
    if not await check_database_exists():
        print("🔧 Database not found or incomplete, initializing...")
        await init_database()
    else:
        print("✅ Database already exists and is complete")


if __name__ == "__main__":
    # Allow running this module directly for database initialization
    asyncio.run(init_database())