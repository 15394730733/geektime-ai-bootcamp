# Requirements Document: Database Selector Fix

## Introduction

This specification addresses the issue where the database selector dropdown in the Query page does not properly reflect the selected database or fails to trigger metadata updates when switching between databases. Users report that clicking on a database in the dropdown (e.g., switching from "test2 - 默认库" to "test - 测试数据库, 编辑一下") does not update the UI state or load the corresponding database metadata.

## Glossary

- **Database_Selector**: The dropdown component in the Query page header that allows users to choose which database to query
- **Selected_Database**: The currently active database that queries will execute against
- **Metadata_Panel**: The left panel displaying schema information (tables, columns) for the selected database
- **Query_Context**: The application state that tracks which database is currently selected
- **AppStateContext**: React context managing global application state including database selection

## Requirements

### Requirement 1: Database Selection Persistence

**User Story:** As a user, I want the database selector to visually reflect my current selection, so that I always know which database I'm querying against.

#### Acceptance Criteria

1. WHEN a user selects a database from the dropdown, THE Database_Selector SHALL display the selected database name
2. WHEN the page reloads with a database already selected, THE Database_Selector SHALL show the previously selected database
3. WHEN a user switches between databases, THE Database_Selector SHALL update its displayed value immediately
4. THE Database_Selector SHALL maintain its selected value until the user explicitly changes it

### Requirement 2: Metadata Synchronization

**User Story:** As a user, I want the metadata panel to update when I switch databases, so that I see the correct schema information for my selected database.

#### Acceptance Criteria

1. WHEN a user selects a database, THE Metadata_Panel SHALL load and display the schema for that database
2. WHEN metadata loading is in progress, THE Metadata_Panel SHALL show a loading indicator
3. WHEN metadata loading fails, THE System SHALL display an error message and maintain the previous metadata state
4. WHEN a user switches from database A to database B, THE Metadata_Panel SHALL clear database A's metadata before loading database B's metadata

### Requirement 3: Query Context Synchronization

**User Story:** As a user, I want my queries to execute against the database I've selected, so that I get results from the correct data source.

#### Acceptance Criteria

1. WHEN a user selects a database, THE Query_Context SHALL update to reflect the new selection
2. WHEN a user executes a query, THE System SHALL use the currently selected database from Query_Context
3. WHEN the selected database changes, THE System SHALL update all components that depend on the database selection
4. THE System SHALL prevent query execution if no database is selected

### Requirement 4: Visual Feedback

**User Story:** As a user, I want clear visual feedback when switching databases, so that I know the system is responding to my actions.

#### Acceptance Criteria

1. WHEN a user clicks on a database in the dropdown, THE Database_Selector SHALL provide immediate visual feedback
2. WHEN database metadata is loading, THE System SHALL display a loading state in the metadata panel
3. WHEN a database switch completes successfully, THE System SHALL display a success message
4. IF a database switch fails, THEN THE System SHALL display an error message and revert to the previous selection

### Requirement 5: Dropdown State Management

**User Story:** As a user, I want the database dropdown to work reliably, so that I can easily switch between my databases.

#### Acceptance Criteria

1. WHEN the dropdown is opened, THE Database_Selector SHALL display all active databases
2. WHEN a user clicks on a database option, THE Database_Selector SHALL close the dropdown and apply the selection
3. THE Database_Selector SHALL highlight the currently selected database in the dropdown list
4. WHEN no database is selected, THE Database_Selector SHALL display a placeholder text

### Requirement 6: Error Handling

**User Story:** As a developer, I want proper error handling for database selection, so that users receive helpful feedback when issues occur.

#### Acceptance Criteria

1. IF metadata loading fails, THEN THE System SHALL log the error details to the console
2. IF a database selection fails, THEN THE System SHALL display a user-friendly error message
3. WHEN an error occurs, THE System SHALL maintain application stability and allow retry attempts
4. THE System SHALL distinguish between network errors, permission errors, and data errors in error messages
