# Ticket 标签管理系统

一个基于 FastAPI 和 Vue3 的 Ticket 标签管理系统，支持创建、编辑、删除 Ticket，并为 Ticket 添加和管理标签。

## 技术栈

### 后端
- **FastAPI 0.115.0** - 现代化的 Python Web 框架
- **PostgreSQL 19.0** - 关系型数据库
- **SQLAlchemy 2.0.36** - Python ORM
- **AsyncPG 0.29.0** - 异步 PostgreSQL 驱动
- **Pydantic 2.9.2** - 数据验证和序列化
- **Alembic 1.14.0** - 数据库迁移工具
- **Pytest 8.3.3** - 测试框架

### 前端
- **Vue 3.5.26** - 渐进式 JavaScript 框架
- **TypeScript 5.9.3** - JavaScript 的超集
- **Vite 8.0.0** - 下一代前端构建工具
- **Element Plus 2.13.0** - Vue 3 组件库
- **UnoCSS 0.60.2** - 原子化 CSS 引擎
- **Pinia 2.2.6** - Vue 状态管理库
- **Vue Router 4.4.5** - Vue 官方路由
- **Vitest** - 单元测试框架

## 项目结构

```
sth-project/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── config/          # 配置文件
│   │   ├── core/            # 核心功能（数据库连接）
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── utils/           # 工具函数
│   │   ├── middleware/      # 中间件
│   │   ├── crud/            # CRUD 操作
│   │   ├── api/             # API 路由
│   │   └── main.py          # 应用入口
│   ├── tests/               # 后端单元测试
│   ├── requirements.txt     # Python 依赖
│   └── Dockerfile           # Docker 配置
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── api/             # API 封装
│   │   ├── components/      # Vue 组件
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── types/           # TypeScript 类型定义
│   │   ├── utils/           # 工具函数
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   ├── App.vue          # 根组件
│   │   └── main.ts          # 应用入口
│   ├── __tests__/           # 前端单元测试
│   ├── package.json         # Node.js 依赖
│   ├── vite.config.ts       # Vite 配置
│   ├── tsconfig.json        # TypeScript 配置
│   └── Dockerfile           # Docker 配置
├── docker-compose.yml       # Docker Compose 配置
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明
```

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆项目并进入项目目录
```bash
cd w1/sth-project
```

2. 启动所有服务
```bash
docker-compose up -d
```

3. 访问应用
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 本地开发

#### 后端

1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
创建 `.env` 文件：
```
DATABASE_URL=postgresql+asyncpg://ticket_user:ticket_password@localhost:5432/ticket_db
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

4. 启动数据库
```bash
docker-compose up -d postgres
```

5. 运行应用
```bash
uvicorn app.main:app --reload
```

#### 前端

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 主要 API 端点

#### Ticket 相关
- `GET /api/tickets` - 获取 Ticket 列表
- `GET /api/tickets/{id}` - 获取单个 Ticket
- `POST /api/tickets` - 创建 Ticket
- `PUT /api/tickets/{id}` - 更新 Ticket
- `DELETE /api/tickets/{id}` - 删除 Ticket
- `PATCH /api/tickets/{id}/toggle` - 切换 Ticket 完成状态
- `POST /api/tickets/{id}/tags` - 为 Ticket 添加标签
- `DELETE /api/tickets/{id}/tags/{tag_id}` - 从 Ticket 移除标签

#### Tag 相关
- `GET /api/tags` - 获取 Tag 列表
- `GET /api/tags/{id}` - 获取单个 Tag
- `POST /api/tags` - 创建 Tag
- `PUT /api/tags/{id}` - 更新 Tag
- `DELETE /api/tags/{id}` - 删除 Tag

## 测试

### 后端测试
```bash
cd backend
pytest tests/ -v
```

### 前端测试
```bash
cd frontend
npm run test
```

## 功能特性

- ✅ 创建、编辑、删除 Ticket
- ✅ 为 Ticket 添加和管理标签
- ✅ 标签的多对多关系管理
- ✅ Ticket 完成状态切换
- ✅ 分页查询
- ✅ 响应式 UI 设计
- ✅ 完整的类型支持（TypeScript）
- ✅ 单元测试覆盖

## 数据库模型

### Ticket
- `id`: 主键
- `title`: 标题
- `description`: 描述
- `is_completed`: 是否完成
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `tags`: 关联的标签（多对多）

### Tag
- `id`: 主键
- `name`: 标签名称
- `color`: 标签颜色
- `created_at`: 创建时间

## 开发规范

- 后端遵循 FastAPI 最佳实践
- 前端遵循 Vue3 组合式 API 规范
- 使用 TypeScript 进行类型检查
- 编写单元测试保证代码质量
- 遵循 RESTful API 设计原则

## 许可证

MIT License
