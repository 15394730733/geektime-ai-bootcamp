# Tasks: MySQL 支持增强

**Feature**: Database Query Tool - MySQL Metadata & Query Support
**Base**: Existing PostgreSQL implementation in `./w2/sth-db-query/backend`
**Input**: 参考 PostgreSQL 实现添加 MySQL 支持到现有数据库查询工具

**Context**: 当前系统仅支持 PostgreSQL，需要添加 MySQL 数据库的元数据提取、查询执行和自然语言 SQL 生成支持。本地已有 MySQL 数据库 `test_db`，密码存储在 `.env` 文件中。

**Organization**: 任务按用户故事组织，确保每个功能可以独立实现和测试。



# MySQL Support Enhancement

## Phase M1: Setup & Dependencies (MySQL 支持基础设施)

**Purpose**: 安装 MySQL 支持所需依赖并配置环境

- [X] M001 添加 MySQL 驱动依赖到 w2/sth-db-query/backend/pyproject.toml（aiomysql>=0.2.0）
- [X] M002 [P] 更新 .env.example 添加 MySQL 连接示例和说明
- [ ] M003 [P] 验证本地 MySQL test_db 数据库可连接性

---

## Phase M2: Foundational (数据库类型抽象层)

**Purpose**: 创建数据库类型抽象基础设施，支持 PostgreSQL 和 MySQL

**⚠️ CRITICAL**: 必须完成此阶段才能开始任何 MySQL 用户故事实现

- [X] M004 创建数据库类型检测器 in w2/sth-db-query/backend/app/core/db_type_detector.py
- [X] M005 [P] 定义数据库适配器接口 in w2/sth-db-query/backend/app/core/db_adapter.py
- [X] M006 [P] 实现 PostgreSQL 适配器 in w2/sth-db-query/backend/app/adapters/postgres_adapter.py
- [X] M007 [P] 实现 MySQL 适配器 in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [X] M008 创建适配器工厂管理器 in w2/sth-db-query/backend/app/core/adapter_factory.py
- [X] M009 更新连接池管理器支持多数据库类型 in w2/sth-db-query/backend/app/core/connection_pool.py

**Checkpoint**: 基础设施就绪 - MySQL 用户故事实现可以并行开始

---

## Phase M3: User Story 1 - MySQL Metadata Extraction (Priority: P1) 🎯 MVP

**Goal**: 实现对 MySQL 数据库的元数据提取功能（表、视图、列信息）

**Independent Test**: 添加 MySQL 连接后，能成功获取并显示数据库的表和视图元数据

### Implementation for User Story 1

- [X] M010 [P] [US1] 在 MySQLAdapter 中实现表列表查询（information_schema.tables） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [X] M011 [P] [US1] 在 MySQLAdapter 中实现视图列表查询（information_schema.views） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [X] M012 [P] [US1] 在 MySQLAdapter 中实现列详情查询（information_schema.columns） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [X] M013 [P] [US1] 在 MySQLAdapter 中实现主键信息查询（information_schema.key_column_usage） in w2/sth-db-query/backend/app/adapters/mysql_adapter.py
- [X] M014 [US1] 更新 DatabaseService._extract_database_metadata 使用适配器 in w2/sth-db-query/backend/app/services/database.py
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