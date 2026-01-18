-- Database Query Tool Schema for MySQL (Fixed)
-- This file contains the MySQL database schema with fixed index syntax

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

-- Create indexes (MySQL doesn't support IF NOT EXISTS for indexes, so we use stored procedure)
DELIMITER $$

DROP PROCEDURE IF EXISTS create_index_if_not_exists$$

CREATE PROCEDURE create_index_if_not_exists(
    IN table_name VARCHAR(255),
    IN index_name VARCHAR(255),
    IN index_definition TEXT
)
BEGIN
    DECLARE index_count INT;
    
    SELECT COUNT(*) INTO index_count
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
    AND table_name = table_name
    AND index_name = index_name;
    
    IF index_count = 0 THEN
        SET @sql = CONCAT('CREATE INDEX ', index_name, ' ON ', table_name, ' ', index_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$

DELIMITER ;

-- Create indexes for database_metadata
CALL create_index_if_not_exists('database_metadata', 'idx_metadata_connection_id', '(connection_id)');
CALL create_index_if_not_exists('database_metadata', 'idx_metadata_object_type', '(object_type)');
CALL create_index_if_not_exists('database_metadata', 'idx_metadata_schema_object', '(schema_name, object_name)');

-- Create indexes for query_history
CALL create_index_if_not_exists('query_history', 'idx_query_history_connection_id', '(connection_id)');
CALL create_index_if_not_exists('query_history', 'idx_query_history_status', '(execution_status)');
CALL create_index_if_not_exists('query_history', 'idx_query_history_created_at', '(created_at DESC)');

-- Clean up
DROP PROCEDURE IF EXISTS create_index_if_not_exists;
