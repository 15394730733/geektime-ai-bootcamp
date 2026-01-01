#!/usr/bin/env python3
"""
Database initialization script for the Database Query Tool.
Creates the necessary SQLite database schema.
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the SQLite database with required schema."""

    # Create .db_query directory if it doesn't exist
    db_dir = Path(__file__).parent / ".db_query"
    db_dir.mkdir(exist_ok=True)

    # Database file path
    db_path = db_dir / "db_query.db"

    # Connect to SQLite database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Create database_connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_connections (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # Create database_metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_metadata (
                id TEXT PRIMARY KEY,
                connection_id TEXT NOT NULL,
                object_type TEXT NOT NULL CHECK (object_type IN ('table', 'view')),
                schema_name TEXT DEFAULT 'public',
                object_name TEXT NOT NULL,
                columns TEXT NOT NULL,  -- JSON string containing column definitions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (connection_id) REFERENCES database_connections(id) ON DELETE CASCADE
            )
        ''')

        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metadata_connection_id
            ON database_metadata(connection_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metadata_object_type
            ON database_metadata(object_type)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metadata_schema_object
            ON database_metadata(schema_name, object_name)
        ''')

        # Create query_history table for future use
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id TEXT PRIMARY KEY,
                connection_id TEXT NOT NULL,
                query_type TEXT NOT NULL CHECK (query_type IN ('manual', 'natural_language')),
                original_input TEXT NOT NULL,
                generated_sql TEXT,  -- Only for natural language queries
                final_sql TEXT NOT NULL,
                execution_status TEXT NOT NULL CHECK (execution_status IN ('pending', 'success', 'error', 'timeout')),
                error_message TEXT,
                execution_time_ms INTEGER,
                result_row_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (connection_id) REFERENCES database_connections(id) ON DELETE CASCADE
            )
        ''')

        # Create indexes for query_history
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query_history_connection_id
            ON query_history(connection_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query_history_status
            ON query_history(execution_status)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query_history_created_at
            ON query_history(created_at DESC)
        ''')

        # Commit all changes
        conn.commit()

        print(f"✅ Database initialized successfully at: {db_path}")
        print("📊 Created tables:"
        print("   - database_connections")
        print("   - database_metadata")
        print("   - query_history")
        print("📈 Created indexes for optimal performance")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
