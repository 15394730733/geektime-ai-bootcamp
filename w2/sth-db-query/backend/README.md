# Database Query Tool Backend

这是一个基于 FastAPI 的数据库查询工具后端服务，提供 REST API 接口用于数据库连接管理和 SQL 查询执行。

## 功能特性

- 🗄️ **多数据库支持**: 支持 PostgreSQL 等数据库连接管理
- 🔍 **SQL 查询执行**: 提供标准的 SQL 查询接口
- 🧠 **自然语言查询**: 支持自然语言到 SQL 的转换（开发中）
- 📊 **查询结果处理**: 支持结果分页、格式化输出
- 🔒 **安全认证**: 内置安全中间件和请求验证
- 📚 **自动文档**: 基于 OpenAPI 的自动 API 文档生成

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy (异步)
- **数据库**: SQLite (应用数据库), PostgreSQL (目标数据库)
- **AI 服务**: GLM API (智谱清言)
- **部署**: Docker, Docker Compose
- **测试**: Pytest, Coverage
- **代码质量**: Ruff, MyPy

## 快速开始

### 使用 Docker Compose (推荐)

```bash
# 克隆项目
cd backend

# 使用 Docker Compose 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 本地开发环境

#### 环境要求

- Python 3.12+
- PostgreSQL (可选，用于测试)

#### 安装依赖

```bash
# 安装 uv 包管理器 (推荐)
pip install uv

# 安装项目依赖
uv sync

# 或者使用 pip
pip install -r requirements.txt
```

#### 环境配置

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./.db_query/db_query.db

# 服务器配置
HOST=0.0.0.0
PORT=8000

# GLM API 配置
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# 开发配置
DEBUG=true
LOG_LEVEL=INFO

# CORS 配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# 查询配置
MAX_QUERY_RESULTS=1000
QUERY_TIMEOUT_SECONDS=30
```

#### 初始化数据库

```bash
# 创建数据库表
python init_db.py
```

#### 启动服务

```bash
# 使用启动脚本 (Windows)
start_server.bat

# 或者直接运行
python app/main.py

# 或者使用 uvicorn
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json
- 健康检查: http://localhost:8000/health

## API 接口文档

### 健康检查

```http
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "service": "database-query-tool"
}
```

### 数据库管理

#### 获取所有数据库连接

```http
GET /api/v1/dbs/
```

响应示例：
```json
{
  "success": true,
  "message": "Databases retrieved successfully",
  "data": [
    {
      "id": "db1",
      "name": "test_db",
      "url": "postgresql://user:pass@localhost:5432/test_db",
      "description": "测试数据库",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  ]
}
```

#### 创建数据库连接

```http
PUT /api/v1/dbs/{name}
```

请求体：
```json
{
  "name": "test_db",
  "url": "postgresql://user:pass@localhost:5432/test_db",
  "description": "测试数据库"
}
```

#### 获取指定数据库连接

```http
GET /api/v1/dbs/{name}
```

#### 更新数据库连接

```http
PUT /api/v1/dbs/{name}
```

#### 删除数据库连接

```http
DELETE /api/v1/dbs/{name}
```

### 查询执行

#### 执行 SQL 查询

```http
POST /api/v1/dbs/{name}/query
```

请求体：
```json
{
  "sql": "SELECT * FROM users LIMIT 10"
}
```

响应示例：
```json
{
  "columns": ["id", "name", "email"],
  "rows": [
    [1, "张三", "zhangsan@example.com"],
    [2, "李四", "lisi@example.com"]
  ],
  "row_count": 2,
  "execution_time_ms": 45,
  "truncated": false
}
```

#### 执行自然语言查询 (开发中)

```http
POST /api/v1/dbs/{name}/query/natural
```

请求体：
```json
{
  "prompt": "显示前10个用户的信息"
}
```

## 数据模型

### 数据库连接 (Database)

```typescript
interface Database {
  id: string;
  name: string;           // 数据库名称 (1-50字符, 只允许字母数字下划线横线)
  url: string;            // PostgreSQL 连接URL
  description?: string;   // 描述 (最多200字符)
  created_at: DateTime;
  updated_at: DateTime;
  is_active: boolean;
}
```

### 查询请求 (QueryRequest)

```typescript
interface QueryRequest {
  sql: string;  // SQL 查询语句
}
```

### 查询结果 (QueryResult)

```typescript
interface QueryResult {
  columns: string[];        // 列名数组
  rows: any[][];           // 结果行数据
  row_count: number;       // 结果行数
  execution_time_ms: number; // 执行时间(毫秒)
  truncated: boolean;      // 是否被截断
}
```

### 自然语言查询请求 (NaturalLanguageQueryRequest)

```typescript
interface NaturalLanguageQueryRequest {
  prompt: string;  // 自然语言查询提示
}
```

### 数据库元数据 (DatabaseMetadata)

```typescript
interface DatabaseMetadata {
  database: string;
  tables: TableMetadata[];
  views: ViewMetadata[];
}

interface TableMetadata {
  name: string;
  schema: string;
  columns: ColumnMetadata[];
}

interface ColumnMetadata {
  name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
  default_value?: string;
}
```

## 开发指南

### 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由定义
│   │   └── v1/
│   │       ├── endpoints/    # 端点处理函数
│   │       │   ├── databases.py
│   │       │   └── queries.py
│   │       └── api.py
│   ├── core/          # 核心配置和服务
│   │   ├── config.py      # 应用配置
│   │   ├── database.py    # 数据库连接
│   │   └── security.py    # 安全中间件
│   ├── crud/          # 数据访问层
│   ├── models/        # 数据模型
│   ├── schemas/       # Pydantic 模式
│   ├── services/      # 业务逻辑层
│   └── utils/         # 工具函数
├── tests/             # 测试文件
├── Dockerfile         # Docker 镜像构建
├── pyproject.toml     # 项目配置和依赖
├── start_server.bat  # Windows 启动脚本
└── README.md         # 项目文档
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行带覆盖率的测试
uv run pytest --cov=app --cov-report=html

# 运行特定测试文件
uv run pytest tests/test_api.py -v
```

### 代码质量检查

```bash
# 代码格式化和检查
uv run ruff check .
uv run ruff format .

# 类型检查
uv run mypy .
```

### 添加新功能

1. 在 `schemas/` 中定义数据模型
2. 在 `models/` 中定义数据库模型 (如果需要)
3. 在 `services/` 中实现业务逻辑
4. 在 `api/v1/endpoints/` 中添加 API 端点
5. 编写相应的测试用例

## 部署

### 生产环境配置

```bash
# 设置环境变量
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export DEBUG=false
export LOG_LEVEL=WARNING
export GLM_API_KEY="your_production_api_key"

# 使用 Docker 部署
docker build -t db-query-backend .
docker run -p 8000:8000 -e DATABASE_URL=$DATABASE_URL db-query-backend
```

### 使用 Docker Compose

```bash
# 生产环境部署
docker-compose -f docker-compose.prod.yml up -d
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 PostgreSQL 服务是否运行
   - 验证连接 URL 格式
   - 确认用户名密码正确

2. **端口占用**
   - 修改 `PORT` 环境变量
   - 检查端口是否被其他服务占用

3. **GLM API 调用失败**
   - 检查 `GLM_API_KEY` 配置
   - 验证 API 密钥有效性
   - 检查网络连接

### 日志查看

```bash
# 查看应用日志
docker-compose logs -f backend

# 查看数据库日志
docker-compose logs -f postgres
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 发送邮件: your-email@example.com
