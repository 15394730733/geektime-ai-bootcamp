# Requirements Document

## Introduction

重构数据库查询工具的前端布局，实现类似专业数据库管理工具的左右分栏界面。左侧显示数据库结构树（schemas、tables、columns），右侧为查询编辑器和结果展示区域，提供更高效的数据库查询体验。

## Glossary

- **Query_Page**: 主查询页面，包含左侧元数据面板和右侧查询区域
- **Metadata_Panel**: 左侧面板，显示数据库结构树形视图
- **Query_Panel**: 右侧面板，包含查询编辑器和结果展示
- **Schema_Tree**: 数据库结构的树形展示组件
- **Query_Editor**: SQL 查询编辑器组件（基于 Monaco Editor）
- **Results_Table**: 查询结果表格组件
- **Tab_System**: 查询标签页系统，支持多个查询会话

## Requirements

### Requirement 1: 左右分栏布局

**User Story:** As a database user, I want a split-panel layout with metadata on the left and query area on the right, so that I can easily reference table structures while writing queries.

#### Acceptance Criteria

1. THE Query_Page SHALL display a resizable left-right split layout
2. THE Metadata_Panel SHALL occupy the left side with a default width of 280px
3. THE Query_Panel SHALL occupy the remaining right side space
4. WHEN the user drags the splitter, THE Query_Page SHALL resize both panels proportionally
5. THE Query_Page SHALL persist the panel width preference in local storage

### Requirement 2: 数据库结构树

**User Story:** As a database user, I want to see the database schema in a tree structure, so that I can quickly navigate tables and columns.

#### Acceptance Criteria

1. THE Schema_Tree SHALL display databases, schemas, tables, and columns in a hierarchical tree
2. WHEN a database is selected, THE Schema_Tree SHALL load and display its schemas and tables
3. THE Schema_Tree SHALL show icons to distinguish tables from views
4. THE Schema_Tree SHALL display column data types and primary key indicators
5. WHEN a user clicks on a table name, THE Query_Editor SHALL insert the fully qualified table name
6. WHEN a user clicks on a column name, THE Query_Editor SHALL insert the column name
7. THE Schema_Tree SHALL support search/filter functionality for tables and columns

### Requirement 3: 查询编辑器区域

**User Story:** As a database user, I want a powerful query editor with tab support, so that I can work on multiple queries simultaneously.

#### Acceptance Criteria

1. THE Query_Editor SHALL support multiple query tabs
2. WHEN a user creates a new tab, THE Tab_System SHALL add a new query session with default name "Query {timestamp}"
3. WHEN a user closes a tab, THE Tab_System SHALL prompt for unsaved changes if query content exists
4. THE Query_Editor SHALL provide syntax highlighting for SQL
5. THE Query_Editor SHALL display a toolbar with Execute, Format, and Clear buttons
6. WHEN the user presses Ctrl+Enter, THE Query_Editor SHALL execute the current query
7. THE Query_Editor SHALL show the selected database name in the tab header area

### Requirement 4: 查询结果展示

**User Story:** As a database user, I want to see query results in a data grid with export options, so that I can analyze and share the data.

#### Acceptance Criteria

1. THE Results_Table SHALL display query results in a sortable, filterable table
2. THE Results_Table SHALL show column headers with data type indicators
3. THE Results_Table SHALL support pagination with configurable page size
4. WHEN results exceed the display limit, THE Results_Table SHALL show a truncation warning
5. THE Results_Table SHALL provide Export CSV and Export JSON buttons
6. THE Results_Table SHALL display row count and execution time
7. WHEN a query fails, THE Results_Table SHALL display the error message clearly

### Requirement 5: 上下分割的右侧面板

**User Story:** As a database user, I want the query editor and results to be in a resizable vertical split, so that I can adjust the view based on my needs.

#### Acceptance Criteria

1. THE Query_Panel SHALL display a vertical split with editor on top and results on bottom
2. WHEN the user drags the vertical splitter, THE Query_Panel SHALL resize editor and results areas
3. THE Query_Panel SHALL persist the vertical split ratio in local storage
4. WHEN no results exist, THE Results_Table SHALL show a placeholder message

### Requirement 6: 响应式设计

**User Story:** As a database user, I want the interface to work well on different screen sizes, so that I can use it on various devices.

#### Acceptance Criteria

1. WHEN the viewport width is less than 768px, THE Query_Page SHALL collapse the Metadata_Panel into a drawer
2. THE Query_Page SHALL provide a toggle button to show/hide the Metadata_Panel on small screens
3. THE Query_Page SHALL maintain minimum widths for both panels to ensure usability

### Requirement 7: 简化导航流程

**User Story:** As a database user, I want to directly access the query interface after selecting a database, so that I can start querying immediately without extra navigation steps.

#### Acceptance Criteria

1. THE Application SHALL NOT display a left sidebar navigation menu
2. WHEN a user clicks on a database in the database list, THE Application SHALL navigate directly to the Query_Page with that database selected
3. THE Query_Page SHALL be the primary interface after database selection
4. THE Application SHALL provide a way to return to the database list from the Query_Page header
