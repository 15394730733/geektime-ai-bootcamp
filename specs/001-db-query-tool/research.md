# Research: Database Query Tool

**Date**: 2025-12-30
**Context**: Database query tool with LLM integration for natural language SQL generation

## Technical Decisions

### Decision: Python (uv) + FastAPI Backend
**Rationale**: Constitution requires Ergonomic Python style and Pydantic data models. FastAPI provides excellent async support, automatic OpenAPI documentation, and native Pydantic integration. uv provides fast Python package management.

**Alternatives considered**:
- Django: Too heavy for this use case, more suited for full web applications
- Flask: Less structured than FastAPI, would require more manual API documentation
- Node.js/Express: Would violate Constitution's Python requirement

### Decision: React + Refine5 Frontend
**Rationale**: Constitution specifies TypeScript frontend. Refine5 provides excellent admin interface components, data provider abstraction, and TypeScript support out of the box.

**Alternatives considered**:
- Vue.js: Good but Refine5 specifically mentioned in requirements
- Angular: Too heavy for this type of tool
- Plain React: Would require building many admin components from scratch

### Decision: SQLite for Local Storage
**Rationale**: Simple file-based database perfect for storing connection strings and cached metadata. No server required, atomic transactions, good performance for read-heavy workloads.

**Alternatives considered**:
- JSON files: No ACID transactions, concurrency issues
- PostgreSQL local: Overkill, requires server process
- Redis: Not persistent, overkill for this use case

### Decision: sqlglot for SQL Parsing
**Rationale**: Excellent SQL parsing library with support for multiple dialects. Can parse, validate, and transform SQL statements. Perfect for ensuring SELECT-only queries.

**Alternatives considered**:
- sqlparse: Basic parsing only, no dialect support
- Custom regex: Insecure and error-prone
- Database-specific parsers: Would limit multi-database support

### Decision: OpenAI SDK for LLM Integration
**Rationale**: Constitution specifies OpenAI SDK for GLM API integration. Provides reliable async client with proper error handling and token management.

**Alternatives considered**:
- Direct HTTP requests: More error-prone, no built-in retry logic
- LangChain: Overkill for simple API calls, adds unnecessary complexity
- Custom client: Would duplicate existing well-tested code

### Decision: Monaco Editor for SQL Input
**Rationale**: Constitution specifies Monaco Editor. Industry standard for code editing with excellent SQL syntax highlighting, IntelliSense, and customization options.

**Alternatives considered**:
- Ace Editor: Good but Monaco provides better TypeScript integration
- CodeMirror: Excellent but requires more configuration
- Plain textarea: No syntax highlighting or advanced features

### Decision: Tailwind CSS + Ant Design
**Rationale**: Constitution specifies Tailwind + Ant Design. Provides consistent design system with excellent React component library and utility-first CSS approach.

**Alternatives considered**:
- Material-UI: Good but Ant Design specifically required
- Bootstrap: Less modern than Tailwind
- Styled Components: Would require building design system from scratch

## Architecture Decisions

### Decision: RESTful API Design
**Rationale**: Simple, well-understood pattern. REST APIs are easy to test, cache, and integrate with. Provides clear resource-based URLs and standard HTTP methods.

**Alternatives considered**:
- GraphQL: Overkill for this use case, adds complexity
- WebSocket: Not needed for request-response pattern
- RPC: Less standard, harder to integrate with frontend frameworks

### Decision: Service Layer Architecture
**Rationale**: Clear separation of concerns. Services handle business logic, API routes handle HTTP concerns, models handle data validation.

**Alternatives considered**:
- Fat controllers: Mixes HTTP and business logic
- Repository pattern: Overkill for this scale
- Active Record: Less suitable for async Python applications

### Decision: Environment-Based Configuration
**Rationale**: GLM API key must be configurable. Environment variables provide security and flexibility across different deployment environments.

**Alternatives considered**:
- Config files: Less secure for secrets
- Hardcoded values: Not deployable
- Database config: Overkill for API keys

## Security Decisions

### Decision: SELECT-Only SQL Validation
**Rationale**: Critical security requirement. Only allowing SELECT statements prevents data modification. sqlglot parsing ensures syntactically valid SQL.

**Alternatives considered**:
- Allow all SQL: Extremely dangerous
- Whitelist specific patterns: Less flexible, harder to maintain
- Database user permissions: Adds complexity, still allows dangerous operations

### Decision: Automatic LIMIT Addition
**Rationale**: Prevents accidental large result sets that could overwhelm the system or database. 1000 rows provides good balance between functionality and safety.

**Alternatives considered**:
- No limit: Could cause performance issues
- User-configurable limit: Adds complexity
- Smaller limit (100): Too restrictive for legitimate use cases

## Performance Decisions

### Decision: Metadata Caching Strategy
**Rationale**: Database metadata changes infrequently. Caching in SQLite avoids repeated expensive introspection queries while ensuring data consistency.

**Alternatives considered**:
- No caching: Poor performance for large databases
- In-memory cache: Not persistent across restarts
- External cache (Redis): Overkill, adds infrastructure complexity

### Decision: Async/Await Throughout
**Rationale**: Database queries and LLM calls are I/O bound. Async provides better resource utilization and responsiveness, especially important for web interface.

**Alternatives considered**:
- Synchronous code: Poor scalability, blocking operations
- Threading: More complex, harder to debug
- Callbacks: Less readable than async/await

## Integration Decisions

### Decision: CORS All Origins
**Rationale**: Constitution requires CORS support for all origins. Tool is designed for open access, no authentication required.

**Alternatives considered**:
- Restricted origins: Would limit usability
- No CORS: Prevents web usage
- Origin validation: Adds complexity for no benefit

### Decision: JSON Response Format
**Rationale**: Constitution requires camelCase JSON. Standard web API format, easily consumed by JavaScript frontends.

**Alternatives considered**:
- snake_case: Inconsistent with JavaScript conventions
- Custom format: Less standard, harder to integrate
- XML: Outdated, more verbose

## Testing Strategy

### Decision: pytest for Backend Testing
**Rationale**: Industry standard for Python testing. Excellent async support, fixtures, and mocking capabilities. Integrates well with FastAPI test client.

**Alternatives considered**:
- unittest: Built-in but less convenient
- nose: Largely replaced by pytest
- Custom test runner: Would duplicate existing functionality

### Decision: Vitest for Frontend Testing
**Rationale**: Fast, modern test runner optimized for Vite-based projects. Excellent TypeScript support and React testing utilities.

**Alternatives considered**:
- Jest: Good but Vitest provides better performance
- Mocha: Requires more configuration
- Cypress: Better for E2E, overkill for unit tests
