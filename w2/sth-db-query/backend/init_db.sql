-- Database Query Tool Schema
-- This file contains the SQLite database schema

-- Database connections table
CREATE TABLE IF NOT EXISTS database_connections (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Database metadata table
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
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_metadata_connection_id ON database_metadata(connection_id);
CREATE INDEX IF NOT EXISTS idx_metadata_object_type ON database_metadata(object_type);
CREATE INDEX IF NOT EXISTS idx_metadata_schema_object ON database_metadata(schema_name, object_name);

-- Query history table
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
);

-- Indexes for query history
CREATE INDEX IF NOT EXISTS idx_query_history_connection_id ON query_history(connection_id);
CREATE INDEX IF NOT EXISTS idx_query_history_status ON query_history(execution_status);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at DESC);
