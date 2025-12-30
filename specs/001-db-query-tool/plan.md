# Implementation Plan: Database Query Tool

**Branch**: `001-db-query-tool` | **Date**: 2025-12-30 | **Spec**: specs/001-db-query-tool/spec.md
**Input**: Feature specification from `/specs/001-db-query-tool/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

构建一个数据库查询工具，允许用户添加数据库连接、探索元数据、执行SQL查询和通过自然语言生成SQL。后端使用Python/FastAPI，前端使用React/Refine5，集成LLM进行自然语言SQL生成。数据库连接和元数据存储在SQLite中，确保安全性和性能。

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+ (uv), Node.js 22+, TypeScript, React 19+
**Primary Dependencies**: FastAPI, sqlglot, OpenAI SDK, React 19+, Refine5, Tailwind CSS, Ant Design, Monaco Editor
**Storage**: SQLite (for connections and metadata), PostgreSQL (target databases)
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Web application (Linux/Windows/Mac)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <30s connection setup, <10s metadata retrieval, <5s query execution
**Constraints**: SQL SELECT-only validation, automatic LIMIT 1000, CORS all origins, no authentication
**Scale/Scope**: Single user tool, up to 100 database connections, metadata for databases with 1000+ tables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Ergonomic Code Style
- 后端使用 Python (uv)，前端使用 TypeScript - 符合要求
- 严格类型标注将在实现中确保
- 设计阶段已明确代码结构和风格指南

### ✅ II. Pydantic Data Models
- 后端使用 Pydantic 定义数据模型 - 已确认
- 数据模型文档已创建，包含所有实体定义和验证规则

### ✅ III. CamelCase JSON Format
- 后端生成 camelCase JSON - 已确认
- API 合约中明确定义了响应格式

### ✅ IV. SQL Security & Validation
- 使用 sqlglot 解析和验证 SQL - 已确认
- 仅允许 SELECT 语句 - 已确认
- 自动添加 LIMIT 1000 - 已确认
- 安全验证逻辑已在设计中定义

### ✅ V. Database Metadata Caching
- SQLite 存储连接和元数据 - 已确认
- 支持 PostgreSQL - 已确认
- 元数据缓存策略已在数据模型中定义

### ✅ VI. LLM Integration
- OpenAI SDK 集成 GLM API - 已确认
- 自然语言转 SQL 功能 - 已确认
- LLM 服务已在架构设计中定义

### ✅ VII. Open Access Design
- 无需 authentication - 已确认
- CORS 支持所有 origin - 已确认
- API 设计遵循开放访问原则

**Result**: ✅ All constitution principles satisfied. Design phase confirms compliance with all governance requirements.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
./w2/sth-db-query/
├── .db_query/
│   └── db_query.db          # SQLite database for connections and metadata
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── dbs.py   # Database management endpoints
│   │   │       └── query.py # Query execution endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py    # Application configuration
│   │   │   └── security.py  # SQL validation logic
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py  # Database connection models
│   │   │   └── metadata.py  # Metadata models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── database.py  # Pydantic schemas
│   │   │   └── query.py     # Query schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── database.py  # Database connection service
│   │       ├── metadata.py  # Metadata extraction service
│   │       ├── llm.py       # LLM integration service
│   │       └── query.py     # Query execution service
│   ├── pyproject.toml       # Python dependencies (uv)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_services.py
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DatabaseList.tsx
│   │   │   ├── DatabaseForm.tsx
│   │   │   ├── MetadataViewer.tsx
│   │   │   ├── QueryEditor.tsx
│   │   │   ├── QueryResults.tsx
│   │   │   └── NaturalLanguageInput.tsx
│   │   ├── pages/
│   │   │   ├── Databases.tsx
│   │   │   ├── Query.tsx
│   │   │   └── index.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── tests/
│       ├── components/
│       └── integration/
├── docker-compose.yml        # Development environment
└── README.md
```

**Structure Decision**: Web application with separate frontend and backend directories. Backend uses standard FastAPI structure with Pydantic models. Frontend uses React with Refine5 framework. SQLite database stored in .db_query subdirectory. Environment variables handled through .env files.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
