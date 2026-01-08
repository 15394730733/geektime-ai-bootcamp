# Implementation Plan: Database Query Tool

## Overview

This implementation plan breaks down the database query tool development into discrete, manageable tasks. The approach follows a backend-first strategy, establishing core functionality before building the frontend interface. Each task builds incrementally on previous work, ensuring a working system at each checkpoint.

## Tasks

- [x] 1. Set up project structure and core dependencies
  - Create backend directory structure with FastAPI application
  - Set up frontend directory structure with React and TypeScript
  - Configure Python dependencies (FastAPI, sqlglot, OpenAI SDK, SQLAlchemy)
  - Configure TypeScript dependencies (React, Ant Design, Monaco Editor)
  - Create environment configuration files
  - _Requirements: 8.1, 8.4, 9.1_

- [x] 2. Implement SQLite metadata store and database models
  - [x] 2.1 Create SQLite database schema for metadata storage
    - Define database connection table structure
    - Define metadata tables for storing table/column information
    - Implement database initialization logic
    - _Requirements: 8.1, 8.4, 8.5_

  - [x] 2.2 Write property test for database initialization
    - **Property 20: Database initialization**
    - **Validates: Requirements 8.5**

  - [x] 2.3 Create Pydantic models for database connections and metadata
    - Implement DatabaseConnection model with validation
    - Implement DatabaseMetadata, TableInfo, and ColumnInfo models
    - Add JSON serialization with camelCase formatting
    - _Requirements: 1.1, 2.2, 9.7_

  - [x] 2.4 Write property test for data model serialization
    - **Property 7: Query result formatting**
    - **Validates: Requirements 3.5, 9.7**

- [x] 3. Implement SQL validation and query engine
  - [x] 3.1 Create SQL validator using sqlglot
    - Implement SQL parsing and syntax validation
    - Add SELECT-only query enforcement
    - Implement automatic LIMIT clause addition
    - Add descriptive error message generation
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 3.2 Write property test for SQL validation
    - **Property 5: SQL validation**
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [x] 3.3 Write property test for automatic LIMIT addition
    - **Property 6: Automatic LIMIT addition**
    - **Validates: Requirements 3.4**

  - [x] 3.4 Implement query execution engine
    - Create database connection management
    - Implement query execution with error handling
    - Add result formatting with camelCase field names
    - Implement query timeout handling
    - _Requirements: 3.5, 3.6, 10.4_

  - [x] 3.5 Write property test for query execution
    - **Property 8: Query execution error handling**
    - **Validates: Requirements 3.6**

- [x] 4. Implement database manager and metadata extraction
  - [x] 4.1 Create database connection manager
    - Implement database connection storage and retrieval
    - Add PostgreSQL connection validation
    - Implement connection status tracking
    - Add descriptive error handling for connection failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.2_

  - [x] 4.2 Write property test for database connection management
    - **Property 1: Database connection storage**
    - **Validates: Requirements 1.1, 1.2**

  - [x] 4.3 Write property test for connection validation
    - **Property 2: Connection validation**
    - **Validates: Requirements 1.3, 1.4**

  - [x] 4.4 Implement PostgreSQL metadata extraction
    - Query PostgreSQL system catalogs for table information
    - Extract column names, data types, and constraints
    - Store extracted metadata in SQLite database
    - Handle metadata extraction errors gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.5 Write property test for metadata extraction
    - **Property 3: Metadata extraction and storage**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 4.6 Write property test for metadata error handling
    - **Property 4: Metadata extraction error handling**
    - **Validates: Requirements 2.5**

- [x] 5. Implement LLM service for natural language processing
  - [x] 5.1 Create OpenAI integration service
    - Implement OpenAI API client configuration
    - Create natural language to SQL conversion
    - Build database metadata context for LLM prompts
    - Add error handling for LLM service failures
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

  - [x] 5.2 Write property test for LLM SQL generation
    - **Property 9: Natural language SQL generation**
    - **Validates: Requirements 4.1, 4.2**

  - [x] 5.3 Write property test for LLM error handling
    - **Property 11: LLM error handling**
    - **Validates: Requirements 4.4**

  - [x] 5.4 Integrate LLM service with SQL validator
    - Ensure LLM-generated queries pass through validation
    - Add validation pipeline for generated SQL
    - _Requirements: 4.3_

  - [x] 5.5 Write property test for LLM validation pipeline
    - **Property 10: LLM-generated query validation**
    - **Validates: Requirements 4.3**

- [x] 6. Checkpoint - Backend core functionality complete
  - Ensure all backend tests pass
  - Verify database connections, metadata extraction, and query execution work
  - Test natural language processing pipeline
  - Ask the user if questions arise

- [x] 7. Implement FastAPI REST endpoints
  - [x] 7.1 Create database management endpoints
    - Implement GET /api/v1/dbs for listing databases
    - Implement PUT /api/v1/dbs/{name} for adding databases
    - Implement GET /api/v1/dbs/{name} for database metadata
    - Add CORS configuration for all origins
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [x] 7.2 Write property test for API endpoints
    - **Property 22: API endpoint behavior**
    - **Validates: Requirements 9.2, 9.3, 9.4**

  - [x] 7.3 Create query execution endpoints
    - Implement POST /api/v1/dbs/{name}/query for SQL execution
    - Implement POST /api/v1/dbs/{name}/query/natural for natural language queries
    - Add consistent error response formatting
    - _Requirements: 9.5, 9.6, 10.1_

  - [x] 7.4 Write property test for query endpoints
    - **Property 22: API endpoint behavior**
    - **Validates: Requirements 9.5, 9.6**

  - [x] 7.5 Write property test for CORS support
    - **Property 21: API CORS support**
    - **Validates: Requirements 9.1**

  - [x] 7.6 Write property test for API response formatting
    - **Property 23: API response format**
    - **Validates: Requirements 9.7**

- [x] 8. Implement React frontend foundation
  - [x] 8.1 Set up React application with TypeScript
    - Configure React with TypeScript and strict type checking
    - Set up Ant Design component library
    - Configure Tailwind CSS for styling
    - Create basic routing structure
    - _Requirements: 5.4, 5.5_

  - [x] 8.2 Create API client service
    - Implement TypeScript API client for backend communication
    - Add type definitions for all API responses
    - Implement error handling for API calls
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 8.3 Write unit tests for API client
    - Test API client methods with mock responses
    - Test error handling scenarios
    - _Requirements: 10.5_

- [x] 9. Implement database management interface
  - [x] 9.1 Create DatabaseList component
    - Display all stored database connections
    - Show connection status and last connected time
    - Add database selection functionality
    - _Requirements: 5.1_

  - [x] 9.2 Write unit test for DatabaseList component
    - Test component rendering with various database lists
    - Test database selection behavior
    - _Requirements: 5.1_

  - [x] 9.3 Create DatabaseForm component
    - Implement form for adding new database connections
    - Add URL and description input fields with validation
    - Handle form submission and error display
    - _Requirements: 5.2_

  - [x] 9.4 Write unit test for DatabaseForm component
    - Test form validation and submission
    - Test error display formatting
    - _Requirements: 5.2, 10.5_

  - [x] 9.5 Create MetadataViewer component
    - Display database schema in expandable tree structure
    - Show tables, views, columns, and data types
    - Update display when database selection changes
    - _Requirements: 5.3, 6.5_

  - [x] 9.6 Write property test for metadata display
    - **Property 12: Database selection UI state**
    - **Validates: Requirements 5.3, 6.6**

- [x] 10. Implement query interface with Monaco Editor
  - [x] 10.1 Create QueryEditor component with Monaco Editor
    - Integrate Monaco Editor for SQL input
    - Configure SQL syntax highlighting
    - Add query execution functionality
    - _Requirements: 6.1, 6.2_

  - [x] 10.2 Write unit test for QueryEditor component
    - Test Monaco Editor integration and rendering
    - Test query execution trigger
    - _Requirements: 6.1_

  - [x] 10.3 Write property test for SQL syntax highlighting
    - **Property 14: SQL editor syntax highlighting**
    - **Validates: Requirements 6.2**

  - [x] 10.4 Create QueryResults component
    - Display query results in data table format
    - Add export functionality for CSV and JSON
    - Show query execution time and row count
    - Handle loading states and error display
    - _Requirements: 6.3, 6.4, 10.5_

  - [x] 10.5 Write property test for query results display
    - **Property 13: Query results display**
    - **Validates: Requirements 6.3, 6.4**
    - **Status: PASSING** - All 8 test cases pass, validating table format display, CSV export, JSON export, clipboard functionality, loading states, execution time formatting, truncated results, and special character handling

- [x] 11. Implement natural language query interface
  - [x] 11.1 Create NaturalLanguageInput component
    - Add text input for natural language queries
    - Implement submission to LLM service
    - Display generated SQL with edit capability
    - Show both generated SQL and execution results
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

  - [x] 11.2 Write property test for natural language processing UI
    - **Property 15: Natural language processing UI flow**
    - **Validates: Requirements 7.2, 7.3**

  - [x] 11.3 Write property test for generated SQL editability
    - **Property 17: Generated SQL editability**
    - **Validates: Requirements 7.5**

  - [x] 11.4 Implement error handling for natural language processing
    - Display LLM service errors clearly to users
    - Add user-friendly error formatting and styling
    - _Requirements: 7.4, 10.5_

  - [x] 11.5 Write property test for UI error display
    - **Property 16: UI error display**
    - **Validates: Requirements 7.4**
    - **Status: PASSING** - All 5 test cases pass, validating error display for natural language processing errors, SQL execution errors, error dismissal, consistent formatting, and edge cases

- [x] 12. Implement application state management and persistence
  - [x] 12.1 Add application startup data loading
    - Load stored database connections on application start
    - Initialize metadata store if it doesn't exist
    - Handle startup errors gracefully
    - _Requirements: 8.2, 8.5_

  - [x] 12.2 Write property test for startup data loading
    - **Property 18: Application startup data loading**
    - **Validates: Requirements 8.2**

  - [x] 12.3 Implement metadata persistence
    - Ensure metadata updates are saved to SQLite database
    - Add automatic persistence for connection changes
    - _Requirements: 8.3_

  - [x] 12.4 Write property test for metadata persistence
    - **Property 19: Metadata persistence**
    - **Validates: Requirements 8.3**

- [x] 13. Implement comprehensive error handling
  - [x] 13.1 Add error categorization and messaging
    - Implement descriptive error messages for all failure types
    - Add error categorization (network, authentication, configuration)
    - Include specific syntax error highlighting for SQL
    - Add timeout error handling and reporting
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 13.2 Write property test for error message quality
    - **Property 24: Error message quality**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**

  - [x] 13.3 Implement UI error formatting
    - Add consistent error display styling across all components
    - Ensure error messages are user-friendly and actionable
    - _Requirements: 10.5_

  - [x] 13.4 Write property test for UI error formatting
    - **Property 25: UI error formatting**
    - **Validates: Requirements 10.5**

- [x] 14. Integration and final wiring
  - [x] 14.1 Connect all frontend components
    - Wire database management, query interface, and natural language components
    - Implement proper state management between components
    - Add navigation and layout structure
    - _Requirements: 5.1, 6.1, 7.1_

  - [x] 14.2 Write integration tests
    - Test end-to-end database connection and query execution
    - Test natural language processing pipeline
    - Test error propagation from backend to frontend
    - _Requirements: All requirements_

  - [x] 14.3 Add final UI polish and layout
    - Implement the query interface layout as shown in the design image
    - Add responsive design for different screen sizes
    - Ensure consistent styling and user experience
    - _Requirements: 5.5, 6.5_

- [x] 15. Final checkpoint - Ensure all tests pass
  - Run complete test suite for backend and frontend
  - Verify all property-based tests pass with 100+ iterations
  - Test application with real PostgreSQL database connections
  - Ensure all requirements are met and documented
  - Ask the user if questions arise

## Notes

- All tasks are required for comprehensive development with full testing coverage
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- Integration tests ensure end-to-end functionality works correctly
- The implementation follows a backend-first approach to establish core functionality early