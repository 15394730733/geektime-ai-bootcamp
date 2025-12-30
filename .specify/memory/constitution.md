<!--
SYNC IMPACT REPORT (2025-12-30)
Version change: N/A → 1.0.0 (Initial constitution creation)
Modified principles: All 7 principles added (first constitution)
Added sections: Core Principles, Technology Stack, Development Standards, Governance
Removed sections: None
Templates requiring updates: None (generic templates remain compatible)
Follow-up TODOs: None
-->
# Database Query Tool Constitution

## Core Principles

### I. Ergonomic Code Style
后端使用 Ergonomic Python 风格编写代码，前端使用 TypeScript；前后端都要有严格的类型标注；代码必须清晰、可读、可维护。

### II. Pydantic Data Models
所有数据模型必须使用 Pydantic 定义；确保类型安全和数据验证；模型定义清晰且文档完备。

### III. CamelCase JSON Format
所有后端生成的 JSON 数据必须使用 camelCase 格式；确保前端后端数据格式一致性；API 响应格式标准化。

### IV. SQL Security & Validation
所有输入的 SQL 语句必须经过 sqlglot 解析；仅允许 SELECT 语句；如果查询不包含 LIMIT 子句，默认添加 LIMIT 1000；语法错误必须给出明确错误信息。

### V. Database Metadata Caching
数据库连接字符串和 metadata 存储在 SQLite 数据库中；metadata 信息可复用，避免重复查询；支持 PostgreSQL 等多种数据库类型。

### VI. LLM Integration
支持通过自然语言生成 SQL 查询；将数据库表和视图信息作为上下文传递给 LLM；使用 OpenAI SDK 集成 GLM API。

### VII. Open Access Design
无需 authentication，任何用户都可以使用；后端 API 支持 CORS，允许所有 origin；简化用户体验，降低使用门槛。

## Technology Stack

使用 Python (uv) / FastAPI / sqlglot / OpenAI SDK 作为后端技术栈；前端使用 React / Refine5 / Tailwind / Ant Design；SQL 编辑器使用 Monaco Editor；GLM API Key 通过环境变量配置。

## Development Standards

数据库连接和 metadata 存储在 ./w2/sth-db-query/.db_query/db_query.db 中；遵循严格的类型标注要求；确保代码质量和安全性；API 设计遵循 RESTful 原则。

## Governance

本宪法是项目的技术指导原则；所有代码变更必须符合宪法要求；新增功能或修改现有原则需要更新宪法；版本控制遵循语义化版本规范。

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
