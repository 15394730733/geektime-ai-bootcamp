# Data Model: Database Query Tool

**Date**: 2025-12-30
**Purpose**: Define data entities, relationships, and validation rules for the database query tool

## Overview

The data model consists of entities for managing database connections, caching metadata, and handling query execution. All models use Pydantic for validation and type safety.

## Core Entities

### 1. DatabaseConnection
Represents a connection to an external database that users can query.

**Attributes**:
- `id`: UUID (primary key, auto-generated)
- `name`: str (unique identifier, 1-50 chars, alphanumeric + hyphens)
- `url`: str (database connection URL, validated format)
- `description`: str (optional, 0-200 chars)
- `created_at`: datetime (auto-generated)
- `updated_at`: datetime (auto-updated)
- `is_active`: bool (default: true)

**Validation Rules**:
- URL must be valid PostgreSQL connection string format
- Name must be unique across all connections
- Description is optional but recommended

**Relationships**:
- One-to-many with DatabaseMetadata
- One-to-many with QueryHistory

### 2. DatabaseMetadata
Cached information about database structure (tables, views, columns).

**Attributes**:
- `id`: UUID (primary key, auto-generated)
- `connection_id`: UUID (foreign key to DatabaseConnection)
- `object_type`: Enum["table", "view"] (type of database object)
- `schema_name`: str (database schema, defaults to "public")
- `object_name`: str (table/view name)
- `columns`: List[ColumnInfo] (column definitions)
- `created_at`: datetime (when metadata was cached)
- `updated_at`: datetime (when metadata was last refreshed)

**ColumnInfo Sub-entity**:
- `name`: str (column name)
- `data_type`: str (SQL data type)
- `is_nullable`: bool (whether column allows NULL)
- `is_primary_key`: bool (whether column is part of primary key)
- `default_value`: str | None (default value if any)

**Validation Rules**:
- object_name must be valid SQL identifier
- schema_name must be valid SQL identifier
- columns list cannot be empty

**Relationships**:
- Many-to-one with DatabaseConnection
- Referenced by QueryExecution for LLM context

### 3. QueryExecution
Represents a single SQL query execution request.

**Attributes**:
- `id`: UUID (primary key, auto-generated)
- `connection_id`: UUID (foreign key to DatabaseConnection)
- `query_type`: Enum["manual", "natural_language"] (how query was created)
- `original_input`: str (user's original input - SQL or natural language)
- `generated_sql`: str | None (SQL generated from natural language)
- `final_sql`: str (actual SQL executed, with LIMIT added if needed)
- `execution_status`: Enum["pending", "success", "error", "timeout"]
- `error_message`: str | None (error details if execution failed)
- `execution_time_ms`: int | None (query execution duration)
- `result_row_count`: int | None (number of rows returned)
- `created_at`: datetime (auto-generated)

**Validation Rules**:
- original_input cannot be empty
- generated_sql is required when query_type is "natural_language"
- final_sql must be valid SQL (validated before execution)
- execution_time_ms must be positive when status is "success"

**Relationships**:
- Many-to-one with DatabaseConnection
- One-to-one with QueryResult (when successful)

### 4. QueryResult
Stores the actual data returned from query execution.

**Attributes**:
- `id`: UUID (primary key, auto-generated)
- `query_id`: UUID (foreign key to QueryExecution)
- `columns`: List[str] (column names in order)
- `rows`: List[List[Any]] (actual data rows)
- `truncated`: bool (whether results were truncated due to size limits)

**Validation Rules**:
- columns list cannot be empty
- rows length must match result_row_count in QueryExecution
- individual row lengths must match columns length

**Relationships**:
- One-to-one with QueryExecution

## Data Flow

### Connection Setup
1. User provides DatabaseConnection data
2. System validates connection URL
3. System attempts to connect and retrieve basic info
4. DatabaseConnection record created
5. Background job populates DatabaseMetadata

### Query Execution (Manual)
1. User provides SQL string
2. System validates SQL (SELECT only, adds LIMIT if needed)
3. QueryExecution record created with status "pending"
4. SQL executed against target database
5. QueryResult record created with data
6. QueryExecution updated with success/error status

### Query Execution (Natural Language)
1. User provides natural language description
2. System retrieves relevant DatabaseMetadata for context
3. LLM generates SQL using metadata context
4. QueryExecution record created with generated_sql
5. Same execution flow as manual queries

## Validation Rules Summary

### Business Rules
- Only SELECT statements are allowed
- Automatic LIMIT 1000 addition when missing
- Maximum result set size: 1000 rows
- Connection URLs must be valid PostgreSQL format
- Database names must be unique
- Metadata cache TTL: 24 hours (configurable)

### Data Integrity
- All foreign key relationships enforced
- UUID primary keys for scalability
- Timestamps auto-managed
- Soft deletes via is_active flag

### Performance Constraints
- Metadata cache prevents repeated introspection
- Result size limits prevent memory exhaustion
- Query execution timeouts (30 seconds default)
- Connection pooling for database efficiency

## Schema Evolution

### Version 1.0 (Current)
- Basic CRUD operations for all entities
- SQLite storage with SQLAlchemy
- Pydantic validation throughout

### Future Considerations
- Query history and favorites
- User permissions (if authentication added)
- Query performance analytics
- Multi-database support expansion
