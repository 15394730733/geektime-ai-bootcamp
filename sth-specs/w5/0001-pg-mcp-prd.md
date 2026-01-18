# PG-MCP 产品需求文档 (PRD)

**文档版本:** 1.0
**创建日期:** 2026-01-18
**最后更新:** 2026-01-18
**状态:** Draft

---

## 1. 产品概述

### 1.1 产品简介

PG-MCP（PostgreSQL Model Context Protocol Server）是一个基于 Python 的 MCP 服务器，旨在为用户提供智能的 PostgreSQL 数据库自然语言查询接口。用户可以使用自然语言描述查询需求，服务器自动生成并执行安全的 SQL 查询，返回结果或 SQL 语句。

### 1.2 核心价值

- **自然语言查询**: 用户无需掌握 SQL 语法，使用自然语言即可查询数据库
- **智能 SQL 生成**: 基于大语言模型（GLM-4.7）理解用户意图并生成准确的 SQL
- **安全性保障**: 严格的 SQL 校验机制，仅允许只读查询，防止 SQL 注入和危险操作
- **结果验证**: 多层验证确保 SQL 执行结果与用户意图匹配
- **灵活输出**: 支持返回 SQL 语句或查询结果，满足不同使用场景

### 1.3 目标用户

- 数据分析师
- 业务人员
- 开发者
- 需要快速查询数据库的非技术用户

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 数据库连接与 Schema 缓存

**优先级:** P0 (必须有)

**功能描述:**
- MCP 服务器启动时自动读取配置文件中可访问的数据库列表
- 连接到每个数据库并提取完整的 schema 信息
- 缓存以下元数据：
  - **Tables**: 表名、列名、数据类型、约束、注释
  - **Views**: 视图定义、列信息
  - **Types**: 自定义类型、枚举类型
  - **Indexes**: 索引名称、索引列、索引类型
  - **Foreign Keys**: 外键关系
  - **Primary Keys**: 主键信息

**技术要求:**
- 使用 Asyncpg 进行异步数据库连接
- Schema 信息在内存中缓存，支持定期刷新
- 支持配置文件热更新（可选）

#### 2.1.2 自然语言查询接口

**优先级:** P0 (必须有)

**功能描述:**
提供 MCP 工具 `query`，接收以下参数：
- `natural_language_query` (string, required): 自然语言查询描述
- `database_name` (string, required): 目标数据库名称
- `return_type` (string, optional): 返回类型，可选值 `["sql", "result"]`，默认 `"result"`
- `max_rows` (integer, optional): 最大返回行数，默认 100

**使用示例:**
```python
# 返回查询结果
mcp.call_tool("query", {
    "natural_language_query": "查找销售额最高的前10个产品",
    "database_name": "ecommerce_db"
})

# 只返回 SQL 语句
mcp.call_tool("query", {
    "natural_language_query": "统计每个部门的员工数量",
    "database_name": "hr_db",
    "return_type": "sql"
})
```

#### 2.1.3 智能SQL生成

**优先级:** P0 (必须有)

**功能描述:**
- 使用智谱 AI GLM-4.7 模型生成 SQL
- 输入包括：
  - 用户的自然语言查询
  - 目标数据库的 schema 信息
  - 上下文信息（如相关表的结构）
- 输出：
  - 标准的 PostgreSQL SQL 查询语句
  - 必要时包含 JOIN、子查询、聚合函数等复杂语法

**技术要求:**
- 构建详细的 Prompt，包含完整的 schema 上下文
- 支持Few-shot learning，提供示例查询
- 处理模糊查询，询问澄清问题（可选）

#### 2.1.4 SQL安全校验

**优先级:** P0 (必须有)

**功能描述:**

多层安全校验机制：

**第一层：语法分析**
- 使用 SQLGlot 解析 SQL 语法树
- 检测并拒绝以下操作：
  - INSERT/UPDATE/DELETE/DROP/TRUNCATE/ALTER 等写操作
  - CREATE/REPLACE 表或视图操作
  - GRANT/REVOKE 权限操作
  - CALL 函数调用
  - COPY 导入导出数据

**第二层：危险操作检测**
- 拒绝包含以下关键词的查询：
  - `pg_sleep`, `benchmark` 等延时函数
  - `pg_` 开头的系统表访问（除必要系统视图外）
  - 文件操作函数
  - 网络操作函数

**第三层：SQL注入检测**
- 参数化查询，防止字符串拼接注入
- 检测异常的 SQL 模式（如注释符、分号注入等）

**技术要求:**
- 使用 SQLGlot 进行 AST 解析
- 白名单机制：仅允许 SELECT 和特定安全函数
- 记录所有被拒绝的查询及原因

#### 2.1.5 SQL执行与结果验证

**优先级:** P0 (必须有)

**功能描述:**

**执行前验证:**
- EXPLAIN 分析查询计划
- 检查是否有全表扫描（可选警告）
- 估算查询成本，拒绝过高成本查询

**执行:**
- 使用 Asyncpg 执行 SQL
- 设置查询超时（如 30 秒）
- 限制返回行数（max_rows 参数）

**结果验证:**
- 检查执行错误，记录详细错误信息
- 验证返回结果的列数和行数
- 如果结果为空，提供可能的原因提示

#### 2.1.6 结果质量评估（可选）

**优先级:** P1 (应该有)

**功能描述:**

使用 OpenAI GPT 模型评估查询结果与用户意图的匹配度：

**评估输入:**
- 原始自然语言查询
- 生成的 SQL 语句
- 查询结果的前 10 行（或全部结果）

**评估输出:**
- 匹配度分数（0-10 分）
- 简短的评估说明
- 如果分数 < 7，触发重新生成

**重新生成机制:**
- 最多重试 2 次
- 每次重试加入之前的错误信息
- 超过重试次数后返回最佳结果并标注低置信度

**技术要求:**
- 可配置是否启用此功能
- 缓存评估结果避免重复调用
- 考虑成本，可选使用更便宜的模型

#### 2.1.7 灵活的返回格式

**优先级:** P0 (必须有)

**功能描述:**

根据 `return_type` 参数返回不同内容：

**`return_type = "result"`** (默认):
```json
{
    "success": true,
    "data": {
        "columns": ["id", "name", "email"],
        "rows": [
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"]
        ],
        "row_count": 2,
        "execution_time_ms": 45
    },
    "sql": "SELECT id, name, email FROM users LIMIT 2;",
    "confidence_score": 9.2,
    "database": "ecommerce_db"
}
```

**`return_type = "sql"`**:
```json
{
    "success": true,
    "sql": "SELECT id, name, email FROM users LIMIT 2;",
    "explanation": "查询用户表的前2条记录，返回ID、姓名和邮箱",
    "database": "ecommerce_db"
}
```

**错误响应:**
```json
{
    "success": false,
    "error": {
        "code": "UNSAFE_QUERY_DETECTED",
        "message": "查询包含不允许的操作: DROP TABLE",
        "details": "安全校验失败，查询被拒绝"
    }
}
```

### 2.2 配置管理

#### 2.2.1 数据库配置

**配置文件位置:** `config/databases.yaml`

```yaml
databases:
  - name: blog_small
    connection:
      host: localhost
      port: 5432
      database: blog_small
      user: postgres
      password: postgres
      pool_size: 10
    cache_ttl: 3600  # schema缓存时间（秒）

  - name: ecommerce_medium
    connection:
      host: localhost
      port: 5432
      database: ecommerce_medium
      user: postgres
      password: postgres

  - name: saas_crm_large
    connection:
      host: localhost
      port: 5432
      database: saas_crm_large
      user: postgres
      password: postgres
```

#### 2.2.2 LLM配置

```yaml
llm:
  provider: zhipu  # 或 openai
  model: glm-4-plus
  api_key: ${ZHIPU_API_KEY}
  temperature: 0.1
  max_tokens: 2000

  # 可选的结果评估模型
  evaluation:
    enabled: true
    provider: openai
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}
    threshold: 7.0  # 最低置信度阈值
```

#### 2.2.3 安全配置

```yaml
security:
  max_execution_time: 30  # 查询超时时间（秒）
  max_return_rows: 1000   # 默认最大返回行数
  allowed_hosts:
    - localhost
    - 127.0.0.1
    - "*.internal.company.com"

  # SQL 安全规则
  sql_rules:
    allow_explain: true
    allow_temp_tables: false
    allow_cte: true
    max_joins: 10
    max_subquery_depth: 3
```

---

## 3. 非功能需求

### 3.1 性能要求

| 指标 | 目标值 | 备注 |
|------|--------|------|
| 启动时间 | < 5 秒 | 包括 schema 缓存加载 |
| SQL生成时间 | < 3 秒 | 从接收请求到生成SQL |
| 查询执行时间 | < 10 秒 | 一般查询（P95） |
| 并发查询数 | > 50 | 同时处理的查询数 |
| Schema缓存大小 | < 100 MB | 内存占用 |

### 3.2 可靠性要求

- **可用性**: 99.5% (月度)
- **错误恢复**: 数据库连接断开自动重连
- **降级策略**: LLM 服务不可用时返回友好错误
- **日志记录**: 完整的查询日志和错误日志

### 3.3 安全性要求

- **只读访问**: 严格限制为只读查询
- **SQL注入防护**: 参数化查询 + AST 验证
- **敏感信息保护**: 日志中脱敏处理敏感数据
- **访问控制**: 支持 API Key 或 Token 认证（可选）

### 3.4 可维护性要求

- **代码质量**: 遵循 PEP 8，类型注解覆盖率 > 80%
- **测试覆盖率**: 单元测试覆盖率 > 80%
- **文档**: 完整的 API 文档和部署文档
- **监控**: Prometheus 指标导出（查询数、错误率、延迟等）

---

## 4. 技术栈

### 4.1 核心依赖

| 组件 | 技术选型 | 版本要求 | 用途 |
|------|----------|----------|------|
| MCP框架 | FastMCP | latest | MCP服务器实现 |
| 数据库驱动 | Asyncpg | >= 0.29.0 | 异步PostgreSQL连接 |
| SQL解析 | SQLGlot | >= 20.0.0 | SQL语法分析和验证 |
| 数据验证 | Pydantic | >= 2.0.0 | 数据模型验证 |
| LLM客户端 | OpenAI SDK | >= 1.0.0 | 调用GLM/OpenAI API |

### 4.2 开发工具

- **Python版本**: 3.11+
- **包管理**: uv
- **测试框架**: pytest + pytest-asyncio
- **代码检查**: ruff, mypy
- **文档工具**: Markdown

---

## 5. 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                         MCP Client                          │
│                    (Claude Code / Others)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       PG-MCP Server                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Router    │  │   Config    │  │  Schema Cache       │  │
│  │   (FastMCP) │  │   Manager   │  │  (PostgreSQL Info)  │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
│         │                                                   │
│         ↓                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Query Processing Pipeline              │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 1. Parse Request (Pydantic)                         │   │
│  │ 2. Retrieve Schema                                  │   │
│  │ 3. Generate SQL (GLM-4.7)                           │   │
│  │ 4. Validate SQL (SQLGlot)                           │   │
│  │ 5. Execute Query (Asyncpg)                          │   │
│  │ 6. Evaluate Result (OpenAI - Optional)              │   │
│  │ 7. Format Response                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ↓                   ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │   Zhipu AI   │  │    OpenAI    │
│   Databases  │  │   (GLM-4.7)  │  │  (Optional)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 6. 测试数据库

### 6.1 测试数据库设计

需要创建三个不同规模和复杂度的测试数据库：

1. **blog_small** (小型博客)
   - 5-10 张表
   - 基础CRUD操作
   - 简单关系（用户、文章、评论、标签）

2. **ecommerce_medium** (中型电商)
   - 15-25 张表
   - 复杂关系（订单、商品、库存、支付、物流）
   - 多种数据类型和索引

3. **saas_crm_large** (大型CRM)
   - 40+ 张表
   - 复杂业务逻辑（客户、销售、营销、报表）
   - 包含视图、物化视图、自定义类型

### 6.2 测试查询集

创建 `TEST_QUERIES.md` 文件，包含：

- 简单查询（单表、过滤）
- 中等查询（JOIN、聚合）
- 复杂查询（子查询、窗口函数、CTE）
- 边缘案例（空结果、大数据集）
- 错误案例（SQL注入、危险操作）

---

## 7. 交付物清单

- [ ] PG-MCP 源代码
- [ ] 配置文件示例
- [ ] Makefile（用于构建测试数据库）
- [ ] 部署文档
- [ ] API 文档
- [ ] 测试用例
- [ ] 测试数据库 SQL 文件（3个）
- [ ] TEST_QUERIES.md（测试查询集）

---

## 8. 里程碑

| 阶段 | 目标 | 预计时间 |
|------|------|----------|
| Phase 0 | 项目初始化、环境搭建 | 1天 |
| Phase 1 | Schema 缓存实现 | 2天 |
| Phase 2 | SQL生成功能 | 3天 |
| Phase 3 | 安全校验机制 | 2天 |
| Phase 4 | 查询执行与结果返回 | 2天 |
| Phase 5 | 结果质量评估（可选） | 2天 |
| Phase 6 | 测试数据库构建 | 1天 |
| Phase 7 | 测试用例编写 | 2天 |
| Phase 8 | 文档完善 | 1天 |
| Phase 9 | 代码review与优化 | 2天 |
| Phase 10 | 集成测试与部署 | 1天 |

**总计:** 约 19 天

---

## 9. 风险与依赖

### 9.1 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM API 不稳定 | 高 | 实现重试机制、降级策略 |
| SQL生成质量不达标 | 中 | 优化Prompt、Few-shot学习 |
| 性能不满足要求 | 中 | 查询优化、缓存策略 |
| 安全漏洞 | 高 | 多层校验、安全审计 |

### 9.2 外部依赖

- Zhipu AI API (GLM-4.7)
- OpenAI API (可选，结果评估)
- PostgreSQL 数据库（测试环境）

---

## 10. 附录

### 10.1 术语表

- **MCP**: Model Context Protocol，AI助手与工具间的协议
- **Schema**: 数据库结构信息（表、视图、类型等）
- **SQLGlot**: Python SQL解析器和转换器
- **AST**: Abstract Syntax Tree，抽象语法树

### 10.2 参考文档

- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [Asyncpg 文档](https://magicstack.github.io/asyncpg/)
- [SQLGlot 文档](https://github.com/tobymao/sqlglot)
- [GLM API 文档](https://open.bigmodel.cn/dev/api)

---

**文档结束**
