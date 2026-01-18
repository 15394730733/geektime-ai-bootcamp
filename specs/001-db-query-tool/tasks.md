# Tasks: MySQL 支持增强

**Feature**: Database Query Tool - MySQL Metadata & Query Support
**Base**: Existing PostgreSQL implementation in `./w2/sth-db-query/backend`
**Input**: 参考 PostgreSQL 实现添加 MySQL 支持到现有数据库查询工具

**Context**: 当前系统仅支持 PostgreSQL，需要添加 MySQL 数据库的元数据提取、查询执行和自然语言 SQL 生成支持。本地已有 MySQL 数据库 `test_db`，密码存储在 `.env` 文件中。

**Organization**: 任务按用户故事组织，确保每个功能可以独立实现和测试。

## 原有任务说明

下方保留原有的 Database Query Tool 完整任务清单（T001-T171），这些任务已完成 PostgreSQL 实现。

本次新增的 MySQL 支持任务使用新的编号系统（M001-M035），位于文件末尾的 "MySQL Support Enhancement" 部分。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `./w2/sth-db-query/backend/`, `./w2/sth-db-query/frontend/`
- Backend paths: `backend/app/`
- Frontend paths: `frontend/src/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 [P] Setup Python backend project with uv in ./w2/sth-db-query/backend/
- [X] T003 [P] Setup React frontend project with Vite in ./w2/sth-db-query/frontend/
- [X] T004 [P] Configure backend environment variables in ./w2/sth-db-query/backend/.env.example
- [X] T005 [P] Configure frontend environment variables in ./w2/sth-db-query/frontend/.env.example
- [X] T006 Create SQLite database schema in ./w2/sth-db-query/.db_query/db_query.db
- [X] T007 [P] Configure CORS middleware in backend for all origins
- [X] T008 [P] Setup basic logging configuration in backend
- [X] T009 [P] Setup test directories structure (backend/tests/, frontend/tests/)
- [X] T010 Create docker-compose.yml for development environment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Setup SQLAlchemy database models and session management in backend/app/models/__init__.py
- [X] T012 [P] Create Pydantic schemas for API requests/responses in backend/app/schemas/
- [X] T013 [P] Setup FastAPI application with basic middleware in backend/app/main.py
- [X] T014 [P] Configure SQLAlchemy async session in backend/app/core/database.py
- [X] T015 [P] Create base CRUD operations in backend/app/crud/__init__.py
- [X] T016 [P] Setup basic error handling and response models in backend/app/utils/response.py
- [X] T017 [P] Configure Pydantic settings for environment variables in backend/app/core/config.py
- [X] T018 [P] Setup LLM service integration with OpenAI SDK in backend/app/services/llm.py
- [X] T019 [P] Create SQL validation utilities with sqlglot in backend/app/core/security.py
- [X] T020 [P] Setup frontend TypeScript configuration and basic component structure
- [X] T021 [P] Configure Refine5 data provider and router in frontend/src/App.tsx
- [X] T022 [P] Setup Tailwind CSS and Ant Design theme in frontend
- [X] T023 [P] Create API client utilities in frontend/src/services/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Connection Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to add, validate, and manage database connections

**Independent Test**: Can be fully tested by adding database connections and verifying storage without any query functionality

### Unit Tests for User Story 1
- [ ] T024 [P] [US1] Create unit tests for database URL validation in backend/tests/unit/test_validation.py
- [ ] T025 [P] [US1] Create unit tests for DatabaseConnection model in backend/tests/unit/test_models.py
- [ ] T026 [P] [US1] Create unit tests for database connection CRUD operations in backend/tests/unit/test_crud.py
- [ ] T027 [P] [US1] Create unit tests for PostgreSQL URL format validation in backend/tests/unit/test_postgres_validation.py
- [ ] T028 [P] [US1] Create unit tests for connection name uniqueness validation in backend/tests/unit/test_name_uniqueness.py
- [ ] T029 [P] [US1] Create unit tests for database connection timeout handling in backend/tests/unit/test_connection_timeout.py
- [ ] T030 [P] [US1] Create unit tests for database connection model serialization in backend/tests/unit/test_model_serialization.py
- [ ] T031 [P] [US1] Create unit tests for database connection CRUD error handling in backend/tests/unit/test_crud_errors.py
- [ ] T032 [P] [US1] Create unit tests for database connection service layer in backend/tests/unit/test_connection_service.py
- [ ] T033 [P] [US1] Create unit tests for database connection status transitions in backend/tests/unit/test_connection_status.py
- [ ] T034 [P] [US1] Create unit tests for database connection configuration parsing in backend/tests/unit/test_config_parsing.py
- [ ] T035 [P] [US1] Create unit tests for database connection health check logic in backend/tests/unit/test_health_check.py

### Integration Tests for User Story 1
- [ ] T036 [P] [US1] Create integration tests for database connection endpoints in backend/tests/integration/test_db_connections.py
- [ ] T037 [P] [US1] Create integration tests for database connection validation workflow in backend/tests/integration/test_connection_validation.py
- [ ] T038 [P] [US1] Create integration tests for database connection CRUD with real database in backend/tests/integration/test_db_crud_real.py
- [ ] T039 [P] [US1] Create integration tests for database connection list pagination in backend/tests/integration/test_connection_pagination.py
- [ ] T040 [P] [US1] Create integration tests for concurrent database connection operations in backend/tests/integration/test_concurrent_connections.py
- [ ] T041 [P] [US1] Create integration tests for database connection error recovery in backend/tests/integration/test_error_recovery.py
- [ ] T042 [P] [US1] Create integration tests for database connection session management in backend/tests/integration/test_session_management.py

### Implementation for User Story 1
- [ ] T043 [P] [US1] Create DatabaseConnection SQLAlchemy model in backend/app/models/database.py
- [ ] T044 [P] [US1] Create Pydantic schemas for database connections in backend/app/schemas/database.py
- [ ] T045 [P] [US1] Implement database connection CRUD operations in backend/app/crud/database.py
- [ ] T046 [P] [US1] Create database connection service with validation in backend/app/services/database.py
- [ ] T047 [US1] Implement GET /api/v1/dbs endpoint in backend/app/api/v1/dbs.py
- [ ] T048 [US1] Implement PUT /api/v1/dbs/{name} endpoint in backend/app/api/v1/dbs.py
- [ ] T049 [P] [US1] Create React component for database connection list in frontend/src/components/DatabaseList.tsx
- [ ] T050 [P] [US1] Create React component for database connection form in frontend/src/components/DatabaseForm.tsx
- [ ] T051 [P] [US1] Create database management page in frontend/src/pages/Databases.tsx
- [ ] T052 [US1] Integrate database connection components with Refine5 resources

### End-to-End Tests for User Story 1
- [ ] T053 [US1] Create E2E test for adding database connection through UI in frontend/tests/e2e/test-add-connection.spec.ts
- [ ] T054 [US1] Create E2E test for viewing database connections list in frontend/tests/e2e/test-view-connections.spec.ts
- [ ] T055 [US1] Create E2E test for connection validation error handling in frontend/tests/e2e/test-connection-errors.spec.ts
- [ ] T056 [US1] Create E2E test for database connection form validation in frontend/tests/e2e/test-form-validation.spec.ts
- [ ] T057 [US1] Create E2E test for database connection editing workflow in frontend/tests/e2e/test-edit-connection.spec.ts
- [ ] T058 [US1] Create E2E test for database connection deletion with confirmation in frontend/tests/e2e/test-delete-connection.spec.ts
- [ ] T059 [US1] Create E2E test for database connection duplicate name handling in frontend/tests/e2e/test-duplicate-names.spec.ts
- [ ] T060 [US1] Create E2E test for database connection list sorting and filtering in frontend/tests/e2e/test-connection-listing.spec.ts
- [ ] T061 [US1] Create E2E test for database connection status indicators in frontend/tests/e2e/test-connection-status.spec.ts
- [ ] T062 [US1] Create E2E test for database connection timeout scenarios in frontend/tests/e2e/test-timeout-handling.spec.ts
- [ ] T063 [US1] Create E2E test for database connection network error recovery in frontend/tests/e2e/test-network-errors.spec.ts

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Database Metadata Exploration (Priority: P2)

**Goal**: Allow users to explore database structure (tables, views, columns)

**Independent Test**: Can be tested by connecting to databases and verifying metadata retrieval without query execution

### Unit Tests for User Story 2
- [ ] T064 [P] [US2] Create unit tests for metadata extraction logic in backend/tests/unit/test_metadata_extraction.py
- [ ] T065 [P] [US2] Create unit tests for DatabaseMetadata model in backend/tests/unit/test_models.py
- [ ] T066 [P] [US2] Create unit tests for metadata caching mechanisms in backend/tests/unit/test_cache.py
- [ ] T067 [P] [US2] Create unit tests for PostgreSQL introspection queries in backend/tests/unit/test_introspection.py
- [ ] T068 [P] [US2] Create unit tests for table column type mapping in backend/tests/unit/test_column_mapping.py
- [ ] T069 [P] [US2] Create unit tests for view detection and parsing in backend/tests/unit/test_view_detection.py
- [ ] T070 [P] [US2] Create unit tests for metadata cache expiration logic in backend/tests/unit/test_cache_expiration.py
- [ ] T071 [P] [US2] Create unit tests for metadata serialization/deserialization in backend/tests/unit/test_metadata_serialization.py
- [ ] T072 [P] [US2] Create unit tests for concurrent metadata access in backend/tests/unit/test_concurrent_metadata.py
- [ ] T073 [P] [US2] Create unit tests for metadata update conflict resolution in backend/tests/unit/test_metadata_conflicts.py
- [ ] T074 [P] [US2] Create unit tests for large schema metadata handling in backend/tests/unit/test_large_schema.py
- [ ] T075 [P] [US2] Create unit tests for metadata filtering and search in backend/tests/unit/test_metadata_filtering.py

### Integration Tests for User Story 2
- [ ] T076 [P] [US2] Create integration tests for metadata retrieval from PostgreSQL in backend/tests/integration/test_metadata_retrieval.py
- [ ] T077 [P] [US2] Create integration tests for metadata caching workflow in backend/tests/integration/test_metadata_cache.py
- [ ] T078 [P] [US2] Create integration tests for metadata refresh operations in backend/tests/integration/test_metadata_refresh.py
- [ ] T079 [P] [US2] Create integration tests for metadata consistency across connections in backend/tests/integration/test_metadata_consistency.py
- [ ] T080 [P] [US2] Create integration tests for metadata performance under load in backend/tests/integration/test_metadata_performance.py
- [ ] T081 [P] [US2] Create integration tests for metadata error handling and recovery in backend/tests/integration/test_metadata_errors.py
- [ ] T082 [P] [US2] Create integration tests for metadata API rate limiting in backend/tests/integration/test_metadata_rate_limiting.py

### Implementation for User Story 2
- [ ] T083 [P] [US2] Create DatabaseMetadata SQLAlchemy model in backend/app/models/metadata.py
- [ ] T084 [P] [US2] Create Pydantic schemas for metadata responses in backend/app/schemas/metadata.py
- [ ] T085 [P] [US2] Implement metadata extraction service in backend/app/services/metadata.py
- [ ] T086 [P] [US2] Implement metadata caching in SQLite in backend/app/services/cache.py
- [ ] T087 [US2] Implement GET /api/v1/dbs/{name} endpoint in backend/app/api/v1/dbs.py
- [ ] T088 [P] [US2] Create React component for metadata viewer in frontend/src/components/MetadataViewer.tsx
- [ ] T089 [P] [US2] Create table/column detail components in frontend/src/components/TableDetails.tsx
- [ ] T090 [US2] Integrate metadata viewer with database list page

### End-to-End Tests for User Story 2
- [ ] T091 [US2] Create E2E test for exploring database metadata through UI in frontend/tests/e2e/test-explore-metadata.spec.ts
- [ ] T092 [US2] Create E2E test for metadata caching behavior in frontend/tests/e2e/test-metadata-cache.spec.ts
- [ ] T093 [US2] Create E2E test for connection error handling in metadata view in frontend/tests/e2e/test-metadata-errors.spec.ts
- [ ] T094 [US2] Create E2E test for table structure visualization in frontend/tests/e2e/test-table-visualization.spec.ts
- [ ] T095 [US2] Create E2E test for column type and constraint display in frontend/tests/e2e/test-column-details.spec.ts
- [ ] T096 [US2] Create E2E test for view definition exploration in frontend/tests/e2e/test-view-exploration.spec.ts
- [ ] T097 [US2] Create E2E test for metadata search and filtering in frontend/tests/e2e/test-metadata-search.spec.ts
- [ ] T098 [US2] Create E2E test for large schema navigation in frontend/tests/e2e/test-large-schema.spec.ts
- [ ] T099 [US2] Create E2E test for metadata refresh functionality in frontend/tests/e2e/test-metadata-refresh.spec.ts
- [ ] T100 [US2] Create E2E test for schema change detection in frontend/tests/e2e/test-schema-changes.spec.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - SQL Query Execution (Priority: P3)

**Goal**: Enable users to execute manual SQL queries and natural language queries

**Independent Test**: Can be tested with manual SQL queries and LLM-generated queries using established database connections

### Unit Tests for User Story 3
- [ ] T101 [P] [US3] Create unit tests for SQL validation logic in backend/tests/unit/test_sql_validation.py
- [ ] T102 [P] [US3] Create unit tests for LIMIT clause addition in backend/tests/unit/test_query_processing.py
- [ ] T103 [P] [US3] Create unit tests for QueryExecution and QueryResult models in backend/tests/unit/test_models.py
- [ ] T104 [P] [US3] Create unit tests for LLM prompt generation in backend/tests/unit/test_llm_prompts.py
- [ ] T105 [P] [US3] Create unit tests for query result formatting in backend/tests/unit/test_result_formatting.py
- [ ] T106 [P] [US3] Create unit tests for SQL injection prevention in backend/tests/unit/test_sql_injection.py
- [ ] T107 [P] [US3] Create unit tests for query execution timeout handling in backend/tests/unit/test_query_timeout.py
- [ ] T108 [P] [US3] Create unit tests for natural language parsing in backend/tests/unit/test_nl_parsing.py
- [ ] T109 [P] [US3] Create unit tests for SQL generation from natural language in backend/tests/unit/test_sql_generation.py
- [ ] T110 [P] [US3] Create unit tests for query result pagination in backend/tests/unit/test_pagination.py
- [ ] T111 [P] [US3] Create unit tests for query performance monitoring in backend/tests/unit/test_performance_monitoring.py
- [ ] T112 [P] [US3] Create unit tests for query history tracking in backend/tests/unit/test_query_history.py
- [ ] T113 [P] [US3] Create unit tests for concurrent query execution in backend/tests/unit/test_concurrent_queries.py
- [ ] T114 [P] [US3] Create unit tests for query result caching in backend/tests/unit/test_result_cache.py
- [ ] T115 [P] [US3] Create unit tests for database-specific SQL dialects in backend/tests/unit/test_sql_dialects.py

### Integration Tests for User Story 3
- [ ] T116 [P] [US3] Create integration tests for SQL query execution in backend/tests/integration/test_query_execution.py
- [ ] T117 [P] [US3] Create integration tests for natural language to SQL conversion in backend/tests/integration/test_natural_language.py
- [ ] T118 [P] [US3] Create integration tests for query result pagination in backend/tests/integration/test_query_results.py
- [ ] T119 [P] [US3] Create integration tests for LLM API integration in backend/tests/integration/test_llm_integration.py
- [ ] T120 [P] [US3] Create integration tests for complex SQL query handling in backend/tests/integration/test_complex_queries.py
- [ ] T121 [P] [US3] Create integration tests for query execution performance in backend/tests/integration/test_query_performance.py
- [ ] T122 [P] [US3] Create integration tests for query result export functionality in backend/tests/integration/test_result_export.py
- [ ] T123 [P] [US3] Create integration tests for query history and analytics in backend/tests/integration/test_query_analytics.py
- [ ] T124 [P] [US3] Create integration tests for database connection pooling in backend/tests/integration/test_connection_pooling.py

### Implementation for User Story 3
- [ ] T125 [P] [US3] Create QueryExecution and QueryResult SQLAlchemy models in backend/app/models/query.py
- [ ] T126 [P] [US3] Create Pydantic schemas for query requests/responses in backend/app/schemas/query.py
- [ ] T127 [P] [US3] Implement query execution service in backend/app/services/query.py
- [ ] T128 [P] [US3] Implement natural language processing service in backend/app/services/nlp.py
- [ ] T129 [US3] Implement POST /api/v1/dbs/{name}/query endpoint in backend/app/api/v1/query.py
- [ ] T130 [US3] Implement POST /api/v1/dbs/{name}/query/natural endpoint in backend/app/api/v1/query.py
- [ ] T131 [P] [US3] Create React component for SQL query editor with Monaco in frontend/src/components/QueryEditor.tsx
- [ ] T132 [P] [US3] Create React component for natural language input in frontend/src/components/NaturalLanguageInput.tsx
- [ ] T133 [P] [US3] Create React component for query results display in frontend/src/components/QueryResults.tsx
- [ ] T134 [P] [US3] Create query execution page in frontend/src/pages/Query.tsx
- [ ] T135 [US3] Integrate query components with metadata viewer for context

### End-to-End Tests for User Story 3
- [ ] T136 [US3] Create E2E test for manual SQL query execution in frontend/tests/e2e/test-manual-query.spec.ts
- [ ] T137 [US3] Create E2E test for natural language query conversion in frontend/tests/e2e/test-natural-language-query.spec.ts
- [ ] T138 [US3] Create E2E test for SQL validation error handling in frontend/tests/e2e/test-query-validation.spec.ts
- [ ] T139 [US3] Create E2E test for query result display and export in frontend/tests/e2e/test-query-results.spec.ts
- [ ] T140 [US3] Create E2E test for LIMIT clause automatic addition in frontend/tests/e2e/test-query-limits.spec.ts
- [ ] T141 [US3] Create E2E test for complex query execution scenarios in frontend/tests/e2e/test-complex-queries.spec.ts
- [ ] T142 [US3] Create E2E test for query performance monitoring in frontend/tests/e2e/test-query-performance.spec.ts
- [ ] T143 [US3] Create E2E test for query history navigation in frontend/tests/e2e/test-query-history.spec.ts
- [ ] T144 [US3] Create E2E test for concurrent query execution in frontend/tests/e2e/test-concurrent-queries.spec.ts
- [ ] T145 [US3] Create E2E test for query result caching behavior in frontend/tests/e2e/test-result-caching.spec.ts
- [ ] T146 [US3] Create E2E test for query syntax highlighting in frontend/tests/e2e/test-syntax-highlighting.spec.ts
- [ ] T147 [US3] Create E2E test for query auto-completion in frontend/tests/e2e/test-auto-completion.spec.ts
- [ ] T148 [US3] Create E2E test for query error recovery and retry in frontend/tests/e2e/test-error-recovery.spec.ts
- [ ] T149 [US3] Create E2E test for query result filtering and sorting in frontend/tests/e2e/test-result-filtering.spec.ts
- [ ] T150 [US3] Create E2E test for large result set handling in frontend/tests/e2e/test-large-results.spec.ts

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T082 [P] Add comprehensive API documentation with OpenAPI/Swagger
- [ ] T083 [P] Implement request/response logging and monitoring
- [ ] T084 [P] Add input sanitization and security headers
- [ ] T085 [P] Implement rate limiting for API endpoints
- [ ] T086 [P] Add database connection health checks
- [ ] T087 [P] Implement query execution timeout handling
- [ ] T088 [P] Add frontend loading states and error boundaries
- [ ] T089 [P] Implement query history and favorites
- [ ] T090 [P] Add keyboard shortcuts for query editor
- [ ] T091 [P] Create comprehensive user documentation
- [ ] T092 [P] Add performance monitoring and metrics
- [ ] T093 [P] Implement database connection pooling
- [ ] T094 [P] Add data export functionality (CSV, JSON)
- [ ] T095 [P] Create admin interface for connection management
- [ ] T096 [P] Add query result caching for performance
- [ ] T097 [P] Implement query syntax highlighting
- [ ] T098 [P] Add support for multiple database types
- [ ] T099 [P] Create comprehensive test coverage reports
- [ ] T100 Run final security audit and penetration testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (unit/integration/e2e) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create unit tests for database URL validation in backend/tests/unit/test_validation.py"
Task: "Create integration tests for database connection endpoints in backend/tests/integration/test_db_connections.py"
Task: "Create E2E test for adding database connection through UI in frontend/tests/e2e/test-add-connection.spec.ts"

# Launch all models for User Story 1 together:
Task: "Create DatabaseConnection SQLAlchemy model in backend/app/models/database.py"
Task: "Create Pydantic schemas for database connections in backend/app/schemas/database.py"

# Launch all services for User Story 1 together:
Task: "Implement database connection CRUD operations in backend/app/crud/database.py"
Task: "Create database connection service with validation in backend/app/services/database.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Backend + Frontend connection management)
   - Developer B: User Story 2 (Backend + Frontend metadata exploration)
   - Developer C: User Story 3 (Backend + Frontend query execution)
3. Stories complete and integrate independently

---

## Test Strategy Summary

**Unit Tests**: 39 tasks (T024-T115 across all user stories)
- Backend: Model validation, service logic, utility functions, security, performance, caching
- Frontend: Component logic, API client functions, form validation, state management

**Integration Tests**: 28 tasks (T036-T124 across user stories)
- API endpoint testing, service integration, database operations, performance testing, error handling
- Database connection testing, metadata caching, query execution workflows

**End-to-End Tests**: 40 tasks (T053-T150 across all user stories)
- Complete user workflows, UI interactions, error scenarios, performance testing
- Form validation, data visualization, concurrent operations, large dataset handling

**System-Level Tests**: Additional comprehensive testing coverage
- [ ] T151 Create system test for full database connection lifecycle in tests/system/test_connection_lifecycle.py
- [ ] T152 Create system test for end-to-end query execution pipeline in tests/system/test_query_pipeline.py
- [ ] T153 Create system test for metadata refresh and consistency in tests/system/test_metadata_system.py
- [ ] T154 Create system test for concurrent user load simulation in tests/system/test_load_simulation.py
- [ ] T155 Create system test for data security and privacy compliance in tests/system/test_security_compliance.py
- [ ] T156 Create system test for backup and recovery procedures in tests/system/test_backup_recovery.py
- [ ] T157 Create system test for API rate limiting under load in tests/system/test_rate_limiting.py
- [ ] T158 Create system test for LLM service integration reliability in tests/system/test_llm_reliability.py
- [ ] T159 Create system test for cross-browser compatibility in frontend/tests/system/test-cross-browser.spec.ts
- [ ] T160 Create system test for mobile responsiveness in frontend/tests/system/test-mobile-responsive.spec.ts

**Performance Tests**: Specialized performance validation
- [ ] T161 Create performance test for database connection pooling in tests/performance/test_connection_pooling.py
- [ ] T162 Create performance test for query execution under load in tests/performance/test_query_load.py
- [ ] T163 Create performance test for metadata caching efficiency in tests/performance/test_cache_performance.py
- [ ] T164 Create performance test for LLM API response times in tests/performance/test_llm_performance.py
- [ ] T165 Create performance test for frontend rendering speed in frontend/tests/performance/test-rendering.spec.ts
- [ ] T166 Create performance test for large dataset visualization in frontend/tests/performance/test-data-visualization.spec.ts

**Security Tests**: Comprehensive security validation
- [ ] T167 Create security test for SQL injection prevention in tests/security/test_sql_injection.py
- [ ] T168 Create security test for API authentication bypass in tests/security/test_auth_bypass.py
- [ ] T169 Create security test for data leakage prevention in tests/security/test_data_leakage.py
- [ ] T170 Create security test for XSS prevention in frontend/tests/security/test-xss-prevention.spec.ts
- [ ] T171 Create security test for CSRF protection in frontend/tests/security/test-csrf-protection.spec.ts

**Total Test Tasks**: 135 comprehensive test implementations ensuring code quality, security, and performance

---

---

# MySQL Support Enhancement

## Phase M1: Setup & Dependencies (MySQL 支持基础设施)

**Purpose**: 安装 MySQL 支持所需依赖并配置环境

- [ ] M001 添加 MySQL 驱动依赖到 w2/sth-db-query/backend/pyproject.toml（aiomysql>=0.2.0）
- [ ] M002 [P] 更新 .env.example 添加 MySQL 连接示例和说明
- [ ] M003 [P] 验证本地 MySQL test_db 数据库可连接性

---

## Phase M2: Foundational (数据库类型抽象层)

**Purpose**: 创建数据库类型抽象基础设施，支持 PostgreSQL 和 MySQL

**⚠️ CRITICAL**: 必须完成此阶段才能开始任何 MySQL 用户故事实现

- [ ] M004 创建数据库类型检测器 in w2/sth-db-query/backend/app/core/db_type_detector.py
- [ ] M005 [P] 定义数据库适配器接口 in w2/sth-db-query/backend/app/core/db_adapter.py
- [ ] M006 [P] 实现 PostgreSQL 适配器 in w2/sth-db-query/backend/app/adapters/postgres_adapter.py
- [ ] M007 [P] 实现 MySQL 适配器 in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M008 创建适配器工厂管理器 in w2/sth-db-query/backend/app/core/adapter_factory.py
- [ ] M009 更新连接池管理器支持多数据库类型 in w2/sth-db-query/backend/app/core/connection_pool.py

**Checkpoint**: 基础设施就绪 - MySQL 用户故事实现可以并行开始

---

## Phase M3: User Story 1 - MySQL Metadata Extraction (Priority: P1) 🎯 MVP

**Goal**: 实现对 MySQL 数据库的元数据提取功能（表、视图、列信息）

**Independent Test**: 添加 MySQL 连接后，能成功获取并显示数据库的表和视图元数据

### Implementation for User Story 1

- [ ] M010 [P] [US1] 在 MySQLAdapter 中实现表列表查询（information_schema.tables） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M011 [P] [US1] 在 MySQLAdapter 中实现视图列表查询（information_schema.views） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M012 [P] [US1] 在 MySQLAdapter 中实现列详情查询（information_schema.columns） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M013 [P] [US1] 在 MySQLAdapter 中实现主键信息查询（information_schema.key_column_usage） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M014 [US1] 更新 DatabaseService._extract_database_metadata 使用适配器 in w2/sth-db-query/backend/app/services/database.py
- [ ] M015 [US1] 测试 MySQL 元数据提取功能（连接本地 test_db 并验证结果）

**Checkpoint**: MySQL 元数据提取功能完整可用

---

## Phase M4: User Story 2 - MySQL Query Execution (Priority: P2)

**Goal**: 实现对 MySQL 数据库的 SQL 查询执行功能

**Independent Test**: 能对 MySQL 数据库执行 SELECT 查询并返回结果

### Implementation for User Story 2

- [ ] M016 [P] [US2] 在 MySQLAdapter 中实现查询执行方法（execute_query） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M017 [P] [US2] 在 MySQLAdapter 中实现 MySQL 特有数据类型序列化 in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M018 [P] [US2] 在 MySQLAdapter 中实现查询超时控制（SET max_execution_time） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [ ] M019 [P] [US2] 更新连接池管理器支持 MySQL 连接池（aiomysql） in w2/sth-db-query/backend/app/core/connection_pool.py
- [ ] M020 [US2] 更新 QueryService 使用数据库适配器执行查询 in w2/sth-db-query/backend/app/services/query.py
- [ ] M021 [US2] 测试 MySQL 查询执行功能（对 test_db 执行 SELECT 查询）

**Checkpoint**: MySQL 查询执行功能完整可用，User Stories 1 & 2 均可独立工作

---

## Phase M5: User Story 3 - MySQL Natural Language SQL (Priority: P3)

**Goal**: 实现针对 MySQL 的自然语言转 SQL 功能

**Independent Test**: 能通过自然语言描述生成并执行 MySQL 查询

### Implementation for User Story 3

- [ ] M022 [P] [US3] 扩展 LLM prompt 模板支持 MySQL 语法 in w2/sth-db-query/backend/app/services/llm.py
- [ ] M023 [P] [US3] 在 LLMService._create_sql_generation_prompt 添加数据库类型检测和适配 in w2/sth-db-query/backend/app/services/llm.py
- [ ] M024 [P] [US3] 更新 SQL 验证器支持 MySQL 方言（sqlglot dialect='mysql'） in w2/sth-db-query/backend/app/core/security.py
- [ ] M025 [US3] 集成数据库类型到 LLM metadata context building in w2/sth-db-query/backend/app/services/llm.py
- [ ] M026 [US3] 测试 MySQL 自然语言查询（对 test_db 使用自然语言生成 SQL）

**Checkpoint**: 所有用户故事均完整可用，支持 PostgreSQL 和 MySQL 的全功能

---

## Phase M6: Polish & Cross-Cutting Concerns

**Purpose**: 跨功能的改进和优化

- [ ] M027 [P] 更新 DatabaseService URL 验证支持 mysql:// and mysql+aiomysql:// in w2/sth-db-query/backend/app/services/database.py
- [ ] M028 [P] 更新 API 响应包含数据库类型信息 in w2/sth-db-query/backend/app/api/v1/endpoints/databases.py
- [ ] M029 [P] 添加数据库类型到 DatabaseConnection schema in w2/sth-db-query/backend/app/schemas/database.py
- [ ] M030 [P] 更新错误处理区分 PostgreSQL 和 MySQL 错误 in w2/sth-db-query/backend/app/core/errors.py
- [ ] M031 [P] 添加数据库类型到连接状态显示 in w2/sth-db-query/backend/app/api/v1/endpoints/databases.py
- [ ] M032 更新 API 文档（OpenAPI）包含 MySQL 支持说明
- [ ] M033 更新 README.md 添加 MySQL 支持文档和示例
- [ ] M034 运行现有测试套件确保向后兼容
- [ ] M035 添加 MySQL 集成测试（连接 test_db） in w2/sth-db-query/backend/tests/integration/test_mysql.py

---

## MySQL Implementation Notes

### 关键技术点

**MySQL 元数据查询**:
- 表信息: `information_schema.tables`
- 视图信息: `information_schema.views`
- 列信息: `information_schema.columns`
- 主键信息: `information_schema.key_column_usage`
- 外键信息: `information_schema.referential_constraints`

**MySQL 查询特性**:
- 驱动: `aiomysql`（异步 MySQL 驱动）
- 超时控制: `SET max_execution_time = <ms>`
- 连接字符串: `mysql://user:password@host:port/database`
- 方言: sqlglot 使用 `dialect='mysql'`

**与 PostgreSQL 的主要差异**:
- 系统表结构不同（information_schema）
- 数据类型映射不同（JSON, DECIMAL, TINYINT 等）
- 引号使用（MySQL 使用反引号 `` ` ``，PostgreSQL 使用双引号）
- LIMIT 语法相同（好消息）

### 测试数据库配置

本地 MySQL 数据库:
- 数据库名: `test_db`
- 密码: 在 `.env` 中的 `MYSQL_PS`
- 连接 URL 示例: `mysql://root:password@localhost:3306/test_db`

---

## MySQL Tasks Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase M1)**: 无依赖 - 可立即开始
- **Foundational (Phase M2)**: 依赖 Setup 完成 - 阻塞所有 MySQL 用户故事
- **User Stories (Phase M3+)**: 全部依赖 Foundational 完成
  - MySQL 用户故事可并行进行（如果有人力）
  - 或按优先级顺序执行（P1 → P2 → P3）
- **Polish (Phase M6)**: 依赖所有期望的 MySQL 用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 完成后可开始 - 无其他故事依赖
- **User Story 2 (P2)**: Foundational 完成后可开始 - 可能与 US1 集成但应独立可测
- **User Story 3 (P3)**: Foundational 完成后可开始 - 可能与 US1/US2 集成但应独立可测

### Parallel Opportunities (MySQL Specific)

- Phase M1: M002, M003 可并行
- Phase M2: M005, M006, M007 可并行
- Phase M3 (US1): M010, M011, M012, M013 可并行
- Phase M4 (US2): M016, M017, M018, M019 可并行
- Phase M5 (US3): M022, M023, M024 可并行
- Phase M6: M027, M028, M029, M030, M031 可并行

---

## MySQL Implementation Strategy

### MVP First (仅 User Story 1)

1. 完成 Phase M1: Setup
2. 完成 Phase M2: Foundational（关键 - 阻塞所有故事）
3. 完成 Phase M3: User Story 1
4. **停止并验证**: 独立测试 MySQL User Story 1
5. 如果就绪则部署/演示（MySQL 元数据支持）

### Incremental Delivery（增量交付）

1. 完成 Setup + Foundational → MySQL 基础就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示（MySQL 元数据可用）
3. 添加 User Story 2 → 独立测试 → 部署/演示（MySQL 查询可用）
4. 添加 User Story 3 → 独立测试 → 部署/演示（MySQL 全功能可用）
5. 每个故事增加价值且不破坏 PostgreSQL 功能

---

## Summary: MySQL Enhancement

**Total MySQL Tasks**: 35
**Tasks per User Story**:
- Setup (Phase M1): 3 tasks
- Foundational (Phase M2): 6 tasks
- User Story 1 (Metadata): 6 tasks
- User Story 2 (Query Execution): 6 tasks
- User Story 3 (Natural Language): 5 tasks
- Polish (Phase M6): 9 tasks

**Parallel Opportunities**: 18 tasks marked [P] across all phases
**Independent Test Criteria**: 每个用户故事都有明确的独立测试标准
**Suggested MVP Scope**: Phase M1 + Phase M2 + Phase M3（Setup + Foundational + US1）
**Format Validation**: ✅ 所有任务遵循检查清单格式（checkbox, ID, labels, file paths）

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- MySQL tasks should NOT break existing PostgreSQL functionality
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
