# Requirements Document

## Introduction

A web-based database query tool that allows users to connect to databases, explore metadata, and execute SQL queries through both direct SQL input and natural language processing. The system provides a user-friendly interface for database exploration and querying with built-in safety features.

## Glossary

- **Database_Manager**: The system component responsible for managing database connections and metadata
- **Query_Engine**: The component that executes SQL queries and validates syntax
- **LLM_Service**: The service that converts natural language to SQL queries
- **Metadata_Store**: SQLite database storing connection information and database metadata
- **SQL_Validator**: Component that validates and sanitizes SQL queries using sqlglot

## Requirements

### Requirement 1: Database Connection Management

**User Story:** As a database administrator, I want to add and manage database connections, so that I can access multiple databases from a single interface.

#### Acceptance Criteria

1. WHEN a user provides a database URL and name, THE Database_Manager SHALL store the connection information in the Metadata_Store
2. WHEN a user requests all databases, THE Database_Manager SHALL return a list of all stored database connections
3. WHEN a user provides a PostgreSQL connection string, THE Database_Manager SHALL validate the connection before storing
4. WHEN a database connection fails, THE Database_Manager SHALL return a descriptive error message
5. THE Database_Manager SHALL support PostgreSQL database connections

### Requirement 2: Database Metadata Extraction

**User Story:** As a data analyst, I want to view database schema information, so that I can understand the structure before writing queries.

#### Acceptance Criteria

1. WHEN a database is successfully connected, THE Database_Manager SHALL extract table and view metadata
2. WHEN metadata is extracted, THE Database_Manager SHALL store table names, column names, and data types in the Metadata_Store
3. WHEN a user requests database metadata, THE Database_Manager SHALL return structured information about tables and views
4. THE Database_Manager SHALL use PostgreSQL system catalogs to extract metadata information
5. WHEN metadata extraction fails, THE Database_Manager SHALL return an error without storing incomplete data

### Requirement 3: SQL Query Execution

**User Story:** As a data analyst, I want to execute SQL queries safely, so that I can retrieve data without risking database integrity.

#### Acceptance Criteria

1. WHEN a user submits a SQL query, THE SQL_Validator SHALL parse it using sqlglot to ensure syntax correctness
2. WHEN a SQL query is syntactically invalid, THE SQL_Validator SHALL return a descriptive error message
3. WHEN a SQL query contains non-SELECT statements, THE SQL_Validator SHALL reject the query
4. WHEN a SELECT query lacks a LIMIT clause, THE Query_Engine SHALL automatically add "LIMIT 1000"
5. WHEN a valid query is executed, THE Query_Engine SHALL return results in JSON format with camelCase field names
6. WHEN query execution fails, THE Query_Engine SHALL return a descriptive error message

### Requirement 4: Natural Language Query Generation

**User Story:** As a business user, I want to generate SQL queries using natural language, so that I can query databases without knowing SQL syntax.

#### Acceptance Criteria

1. WHEN a user provides a natural language prompt, THE LLM_Service SHALL generate a corresponding SQL query
2. WHEN generating SQL, THE LLM_Service SHALL use database metadata as context for accurate table and column references
3. WHEN the LLM generates a query, THE SQL_Validator SHALL validate it before execution
4. WHEN natural language processing fails, THE LLM_Service SHALL return an error message
5. THE LLM_Service SHALL use OpenAI SDK for natural language processing

### Requirement 5: Web Interface for Database Management

**User Story:** As a user, I want a web interface to manage database connections, so that I can easily add and view my databases.

#### Acceptance Criteria

1. WHEN a user visits the databases page, THE Web_Interface SHALL display all stored database connections
2. WHEN a user adds a new database, THE Web_Interface SHALL provide a form with URL and description fields
3. WHEN a user selects a database, THE Web_Interface SHALL display the database metadata in a tree structure
4. THE Web_Interface SHALL use React with TypeScript for type safety
5. THE Web_Interface SHALL use Ant Design components for consistent UI styling

### Requirement 6: Query Interface with Monaco Editor

**User Story:** As a data analyst, I want a professional SQL editor interface, so that I can write and execute queries efficiently.

#### Acceptance Criteria

1. WHEN a user opens the query interface, THE Web_Interface SHALL display a Monaco Editor for SQL input
2. WHEN a user types SQL, THE Monaco_Editor SHALL provide syntax highlighting for SQL
3. WHEN a user executes a query, THE Web_Interface SHALL display results in a data table format
4. WHEN query results are returned, THE Web_Interface SHALL provide export options for CSV and JSON
5. THE Web_Interface SHALL display database schema information alongside the query editor
6. WHEN a user switches between databases, THE Web_Interface SHALL update the available schema information

### Requirement 7: Natural Language Query Interface

**User Story:** As a business user, I want to input natural language queries, so that I can get data without writing SQL.

#### Acceptance Criteria

1. WHEN a user enters natural language text, THE Web_Interface SHALL provide a text input for natural language queries
2. WHEN a user submits natural language input, THE Web_Interface SHALL send it to the LLM service
3. WHEN the LLM generates SQL, THE Web_Interface SHALL display both the generated SQL and execute it automatically
4. WHEN natural language processing fails, THE Web_Interface SHALL display the error message clearly
5. THE Web_Interface SHALL allow users to edit the generated SQL before execution

### Requirement 8: Data Storage and Persistence

**User Story:** As a system administrator, I want database connections and metadata to persist, so that users don't need to reconfigure connections repeatedly.

#### Acceptance Criteria

1. THE Metadata_Store SHALL use SQLite database for local storage
2. WHEN the application starts, THE Database_Manager SHALL load existing connections from the Metadata_Store
3. WHEN metadata is updated, THE Database_Manager SHALL persist changes to the Metadata_Store
4. THE Metadata_Store SHALL be located at ./w2/sth-db-query/.db_query/db_query.db
5. WHEN the SQLite database doesn't exist, THE Database_Manager SHALL create it with the required schema

### Requirement 9: API Design and CORS Support

**User Story:** As a frontend developer, I want a well-defined REST API, so that I can build the user interface efficiently.

#### Acceptance Criteria

1. THE API SHALL support CORS for all origins to enable frontend development
2. WHEN clients request GET /api/v1/dbs, THE API SHALL return all stored databases
3. WHEN clients send PUT /api/v1/dbs/{name} with connection data, THE API SHALL store the database connection
4. WHEN clients request GET /api/v1/dbs/{name}, THE API SHALL return database metadata
5. WHEN clients send POST /api/v1/dbs/{name}/query with SQL, THE API SHALL execute the query and return results
6. WHEN clients send POST /api/v1/dbs/{name}/query/natural with natural language, THE API SHALL generate and execute SQL
7. THE API SHALL return all responses in JSON format with camelCase field names

### Requirement 10: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand and fix issues.

#### Acceptance Criteria

1. WHEN any operation fails, THE System SHALL return descriptive error messages
2. WHEN database connections fail, THE System SHALL indicate whether it's a network, authentication, or configuration issue
3. WHEN SQL syntax is invalid, THE System SHALL highlight the specific syntax error
4. WHEN queries timeout, THE System SHALL inform the user about the timeout
5. THE Web_Interface SHALL display error messages in a user-friendly format with appropriate styling