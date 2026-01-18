-- Database Query Tool Schema for MySQL
-- This file contains the MySQL database schema

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE test_db;

-- Database connections table
CREATE TABLE IF NOT EXISTS database_connections (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Database metadata table
CREATE TABLE IF NOT EXISTS database_metadata (
    id VARCHAR(36) PRIMARY KEY,
    connection_id VARCHAR(36) NOT NULL,
    object_type VARCHAR(20) NOT NULL CHECK (object_type IN ('table', 'view')),
    schema_name VARCHAR(255) DEFAULT 'public',
    object_name VARCHAR(255) NOT NULL,
    columns JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES database_connections(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_metadata_connection_id ON database_metadata(connection_id);
CREATE INDEX IF NOT EXISTS idx_metadata_object_type ON database_metadata(object_type);
CREATE INDEX IF NOT EXISTS idx_metadata_schema_object ON database_metadata(schema_name, object_name);

-- Query history table
CREATE TABLE IF NOT EXISTS query_history (
    id VARCHAR(36) PRIMARY KEY,
    connection_id VARCHAR(36) NOT NULL,
    query_type VARCHAR(50) NOT NULL CHECK (query_type IN ('manual', 'natural_language')),
    original_input TEXT NOT NULL,
    generated_sql TEXT,
    final_sql TEXT NOT NULL,
    execution_status VARCHAR(20) NOT NULL CHECK (execution_status IN ('pending', 'success', 'error', 'timeout')),
    error_message TEXT,
    execution_time_ms INT,
    result_row_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES database_connections(id) ON DELETE CASCADE
);

-- Indexes for query history
CREATE INDEX IF NOT EXISTS idx_query_history_connection_id ON query_history(connection_id);
CREATE INDEX IF NOT EXISTS idx_query_history_status ON query_history(execution_status);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at DESC);
