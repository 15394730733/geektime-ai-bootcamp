# Ticket 标签管理系统 - 详细实现计划

## 文档说明

**基于文档**: `0001-spec-by-claude.md` - Ticket 标签管理系统需求与设计文档
**创建日期**: 2025-01-15
**预计工期**: 13-18 天
**技术栈**: Python 3.11+ / FastAPI / PostgreSQL / Vue 3 / TypeScript / Element Plus

---

## 目录

1. [项目准备阶段](#1-项目准备阶段)
2. [后端开发阶段](#2-后端开发阶段)
3. [前端开发阶段](#3-前端开发阶段)
4. [集成测试阶段](#4-集成测试阶段)
5. [部署优化阶段](#5-部署优化阶段)
6. [验收交付阶段](#6-验收交付阶段)

---

## 1. 项目准备阶段

**工期**: 1-2 天
**目标**: 搭建完整的开发环境和基础架构

### 1.1 环境搭建

#### 1.1.1 后端项目初始化

**任务清单**:
- [ ] 创建后端项目目录结构
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   └── database.py
  ├── tests/
  ├── alembic/
  └── pyproject.toml
  ```

- [ ] 配置 Python 依赖管理
  - 使用 `uv` 或 `poetry` 管理依赖
  - 核心依赖版本:
    - fastapi==0.109.0
    - uvicorn[standard]==0.27.0
    - sqlalchemy==2.0.25
    - alembic==1.13.1
    - psycopg2-binary==2.9.9
    - pydantic==2.5.3

- [ ] 配置开发环境
  - 设置 `.env` 文件
  - 配置 `pyproject.toml`
  - 配置 `.python-version`

- [ ] 配置代码规范工具
  - Black (代码格式化)
  - Flake8 (代码检查)
  - mypy (类型检查)
  - pytest (测试框架)

**验收标准**:
- ✅ 后端服务可以正常启动 (`uvicorn app.main:app --reload`)
- ✅ 依赖安装无错误
- ✅ 访问 `http://localhost:8000/docs` 能看到 FastAPI 自动文档

#### 1.1.2 前端项目初始化

**任务清单**:
- [ ] 使用 Vite 创建 Vue 3 + TypeScript 项目
  ```bash
  npm create vite@latest frontend -- --template vue-ts
  ```

- [ ] 安装核心依赖
  - vue@^3.4.15
  - vue-router@^4.2.5
  - pinia@^2.1.7
  - element-plus@^2.5.2
  - @element-plus/icons-vue@^2.3.1
  - unocss@^0.58.0
  - axios@^1.6.5
  - @vueuse/core@^10.7.2

- [ ] 配置开发工具
  - 配置 `tsconfig.json`
  - 配置 `vite.config.ts`
  - 配置 `unocss.config.ts`
  - 配置 ESLint 和 Prettier

- [ ] 创建目录结构
  ```
  frontend/src/
  ├── components/
  │   ├── tickets/
  │   ├── tags/
  │   ├── layout/
  │   └── common/
  ├── stores/
  ├── services/
  ├── types/
  ├── utils/
  └── styles/
  ```

**验收标准**:
- ✅ 前端开发服务器可以正常启动 (`npm run dev`)
- ✅ 访问 `http://localhost:5173` 能看到默认页面
- ✅ TypeScript 编译无错误

#### 1.1.3 数据库环境搭建

**任务清单**:
- [ ] 使用 Docker Compose 配置 PostgreSQL
  ```yaml
  services:
    postgres:
      image: postgres:15-alpine
      environment:
        POSTGRES_DB: ticketdb
        POSTGRES_USER: ticketuser
        POSTGRES_PASSWORD: ticketpass
      ports:
        - "5432:5432"
  ```

- [ ] 配置 Alembic 数据库迁移
  - 初始化 Alembic (`alembic init`)
  - 配置 `alembic.ini`
  - 配置 `env.py`

- [ ] 准备测试数据脚本
  - 创建 `seed.sql` 文件
  - 编写测试标签和 Ticket 数据

**验收标准**:
- ✅ PostgreSQL 容器正常运行
- ✅ 可以使用数据库客户端连接
- ✅ Alembic 可以执行迁移命令

### 1.2 数据库设计与迁移

**工期**: 0.5-1 天

#### 1.2.1 创建数据库模型

**任务清单**:
- [ ] 创建 SQLAlchemy 模型
  - `app/models/ticket.py` - Ticket 模型
  - `app/models/tag.py` - Tag 模型
  - 配置多对多关系表

- [ ] 定义模型字段
  ```python
  # tickets 表
  - id: SERIAL PRIMARY KEY
  - title: VARCHAR(200) NOT NULL
  - description: TEXT
  - is_completed: BOOLEAN DEFAULT FALSE
  - created_at: TIMESTAMP WITH TIME ZONE
  - updated_at: TIMESTAMP WITH TIME ZONE

  # tags 表
  - id: SERIAL PRIMARY KEY
  - name: VARCHAR(50) UNIQUE NOT NULL
  - color: VARCHAR(7) NOT NULL
  - created_at: TIMESTAMP WITH TIME ZONE
  - updated_at: TIMESTAMP WITH TIME ZONE

  # ticket_tags 表
  - ticket_id: INTEGER REFERENCES tickets(id)
  - tag_id: INTEGER REFERENCES tags(id)
  - PRIMARY KEY (ticket_id, tag_id)
  ```

- [ ] 创建数据库索引
  - `idx_tickets_is_completed`
  - `idx_tickets_created_at`
  - `idx_tags_name`
  - `idx_ticket_tags_ticket_id`
  - `idx_ticket_tags_tag_id`

**验收标准**:
- ✅ 模型类定义完整,类型正确
- ✅ 关系配置正确(多对多)
- ✅ 所有字段都有默认值和约束

#### 1.2.2 编写数据库迁移脚本

**任务清单**:
- [ ] 创建初始迁移脚本
  ```bash
  alembic revision --autogenerate -m "Initial migration"
  ```

- [ ] 添加 updated_at 自动更新触发器
  ```sql
  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
  END;
  $$ language 'plpgsql';
  ```

- [ ] 测试迁移脚本
  - 执行 `alembic upgrade head`
  - 验证表结构创建成功
  - 验证索引创建成功

**验收标准**:
- ✅ 迁移脚本可以成功执行
- ✅ 数据库表结构与设计一致
- ✅ 可以通过 Alembic 回滚迁移

---

## 2. 后端开发阶段

**工期**: 3-4 天
**目标**: 完成所有后端 API 和业务逻辑

### 2.1 Pydantic Schema 定义

**工期**: 0.5 天

**任务清单**:
- [ ] 创建 Ticket Schema
  - `TicketBase` - 基础字段
  - `TicketCreate` - 创建请求
  - `TicketUpdate` - 更新请求
  - `TicketResponse` - 响应模型
  - `TicketListResponse` - 列表响应

- [ ] 创建 Tag Schema
  - `TagBase` - 基础字段
  - `TagCreate` - 创建请求
  - `TagUpdate` - 更新请求
  - `TagResponse` - 响应模型
  - `TagListResponse` - 列表响应(含使用次数)

- [ ] 配置序列化
  - 时间格式化为 ISO 8601
  - 嵌套关系序列化(Ticket 包含 tags)

**验收标准**:
- ✅ 所有 Schema 定义完整
- ✅ 字段验证规则正确(长度、必填)
- ✅ JSON 序列化/反序列化正常

### 2.2 CRUD 层实现

**工期**: 1 天

#### 2.2.1 Ticket CRUD

**任务清单**:
- [ ] 实现基础 CRUD 操作 (`app/crud/ticket.py`)
  - `get_ticket(db, ticket_id)` - 获取单个
  - `get_tickets(db, skip, limit)` - 获取列表
  - `create_ticket(db, ticket)` - 创建
  - `update_ticket(db, ticket_id, ticket)` - 更新
  - `delete_ticket(db, ticket_id)` - 删除

- [ ] 实现高级查询
  - `search_tickets(db, keyword)` - 搜索
  - `filter_tickets_by_tags(db, tag_ids)` - 标签筛选
  - `filter_tickets_by_status(db, is_completed)` - 状态筛选

- [ ] 实现批量操作
  - `batch_delete_tickets(db, ticket_ids)` - 批量删除
  - `batch_toggle_tickets(db, ticket_ids, is_completed)` - 批量完成

- [ ] 实现关系处理
  - 关联标签查询(避免 N+1 问题)
  - 使用 `selectinload` 或 `joinedload`

**验收标准**:
- ✅ 所有 CRUD 函数有正确的类型提示
- ✅ 数据库会话管理正确
- ✅ 错误处理完善(记录不存在、唯一性冲突等)

#### 2.2.2 Tag CRUD

**任务清单**:
- [ ] 实现基础 CRUD 操作 (`app/crud/tag.py`)
  - `get_tag(db, tag_id)`
  - `get_tags(db, skip, limit)`
  - `create_tag(db, tag)`
  - `update_tag(db, tag_id, tag)`
  - `delete_tag(db, tag_id)`

- [ ] 实现统计功能
  - `get_tag_usage_count(db, tag_id)` - 获取使用次数
  - `get_all_tags_with_count(db)` - 获取所有标签及使用次数

- [ ] 实现颜色生成工具 (`app/utils/color_generator.py`)
  - 自动生成随机颜色
  - 确保颜色可读性(避免太浅/太深)
  - 支持自定义颜色

**验收标准**:
- ✅ 标签名称唯一性校验
- ✅ 删除标签时自动清理关联
- ✅ 颜色生成算法合理

### 2.3 API 路由实现

**工期**: 1.5 天

#### 2.3.1 Ticket API

**任务清单**:
- [ ] 实现 Ticket 路由 (`app/api/tickets.py`)
  - `GET /api/v1/tickets` - 获取列表(支持筛选和搜索)
  - `GET /api/v1/tickets/{ticket_id}` - 获取详情
  - `POST /api/v1/tickets` - 创建
  - `PUT /api/v1/tickets/{ticket_id}` - 更新
  - `DELETE /api/v1/tickets/{ticket_id}` - 删除单个
  - `DELETE /api/v1/tickets` - 批量删除
  - `PATCH /api/v1/tickets/{ticket_id}/toggle` - 切换状态
  - `PATCH /api/v1/tickets/batch-complete` - 批量完成

- [ ] 实现查询参数处理
  ```python
  @router.get("/tickets")
  async def get_tickets(
      search: Optional[str] = None,
      tag_ids: Optional[str] = None,  # 逗号分隔
      is_completed: Optional[bool] = None,
      skip: int = 0,
      limit: int = 100,
      db: Session = Depends(get_db)
  ):
      # 实现逻辑
  ```

- [ ] 添加请求验证
  - 标题长度 1-200 字符
  - 描述最多 2000 字符
  - 标签 ID 列表有效性校验

**验收标准**:
- ✅ 所有 API 端点可访问
- ✅ 请求参数验证正确
- ✅ 错误响应格式统一

#### 2.3.2 Tag API

**任务清单**:
- [ ] 实现 Tag 路由 (`app/api/tags.py`)
  - `GET /api/v1/tags` - 获取列表(含使用次数)
  - `GET /api/v1/tags/{tag_id}` - 获取详情
  - `POST /api/v1/tags` - 创建
  - `PUT /api/v1/tags/{tag_id}` - 更新
  - `DELETE /api/v1/tags/{tag_id}` - 删除

- [ ] 实现标签名称唯一性校验
  ```python
  @router.post("/tags")
  async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
      existing = crud.get_tag_by_name(db, tag.name)
      if existing:
          raise HTTPException(status_code=400, detail="Tag name already exists")
      # ...
  ```

- [ ] 实现删除关联清理
  - 删除标签时自动移除 ticket_tags 关联
  - 使用 SQLAlchemy `ON DELETE CASCADE`

**验收标准**:
- ✅ API 响应包含使用次数
- ✅ 唯一性约束生效
- ✅ 删除标签不影响 Ticket 数据

#### 2.3.3 CORS 和异常处理

**任务清单**:
- [ ] 配置 CORS
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

- [ ] 统一异常处理
  - 创建 `app/utils/exceptions.py`
  - 自定义异常类
  - 全局异常处理器

- [ ] 添加日志
  - 配置日志级别
  - 记录请求和错误
  - 使用结构化日志(JSON 格式)

**验收标准**:
- ✅ 前端可以正常调用 API
- ✅ 错误响应格式统一且友好
- ✅ 日志输出清晰可读

### 2.4 后端测试

**工期**: 1 天

#### 2.4.1 单元测试

**任务清单**:
- [ ] 测试 Ticket CRUD
  ```python
  def test_create_ticket(db_session):
      ticket = TicketCreate(title="Test Ticket")
      created = crud.create_ticket(db_session, ticket)
      assert created.id is not None
      assert created.title == "Test Ticket"

  def test_create_ticket_with_tags(db_session):
      # 测试关联标签创建
  ```

- [ ] 测试 Tag CRUD
  ```python
  def test_create_tag(db_session):
      tag = TagCreate(name="Bug", color="#EF4444")
      created = crud.create_tag(db_session, tag)
      assert created.name == "Bug"

  def test_tag_name_unique(db_session):
      # 测试唯一性约束
  ```

- [ ] 测试工具函数
  - 颜色生成器测试
  - 搜索功能测试

**验收标准**:
- ✅ 测试覆盖率 > 80%
- ✅ 所有关键逻辑有测试覆盖

#### 2.4.2 API 集成测试

**任务清单**:
- [ ] 测试所有 API 端点
  ```python
  def test_create_ticket_api(client):
      response = client.post(
          "/api/v1/tickets",
          json={"title": "Test Ticket", "tag_ids": [1, 2]}
      )
      assert response.status_code == 200
      data = response.json()
      assert data["title"] == "Test Ticket"
      assert len(data["tags"]) == 2
  ```

- [ ] 测试参数验证
  - 测试必填字段缺失
  - 测试字段长度超限
  - 测试无效的 tag_id

- [ ] 测试错误处理
  - 测试 404 响应
  - 测试 400 响应
  - 测试 500 响应

**验收标准**:
- ✅ 所有 API 端点有集成测试
- ✅ 异常场景有测试覆盖
- ✅ 测试可以在 CI 中运行

---

## 3. 前端开发阶段

**工期**: 4-5 天
**目标**: 完成所有前端页面和组件

### 3.1 基础架构搭建

**工期**: 0.5 天

#### 3.1.1 类型定义

**任务清单**:
- [ ] 定义 TypeScript 类型 (`src/types/`)
  - `src/types/ticket.ts`
    ```typescript
    export interface Ticket {
      id: number
      title: string
      description: string | null
      isCompleted: boolean
      createdAt: string
      updatedAt: string
      tags: Tag[]
    }

    export interface TicketFormData {
      title: string
      description?: string
      tagIds: number[]
    }
    ```

  - `src/types/tag.ts`
    ```typescript
    export interface Tag {
      id: number
      name: string
      color: string
      usageCount?: number
      createdAt: string
    }
    ```

  - `src/types/index.ts` - 统一导出

**验收标准**:
- ✅ 类型定义与后端 API 一致
- ✅ 所有接口有完整的类型注释

#### 3.1.2 API 服务封装

**任务清单**:
- [ ] 创建 API 服务 (`src/services/api.ts`)
  ```typescript
  import axios from 'axios'

  const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 10000,
  })

  // 请求拦截器
  api.interceptors.request.use((config) => {
    // 添加认证 token(如果需要)
    return config
  })

  // 响应拦截器
  api.interceptors.response.use(
    (response) => response.data,
    (error) => {
      // 统一错误处理
      return Promise.reject(error)
    }
  )

  export const ticketApi = {
    getList: (params) => api.get('/tickets', { params }),
    getById: (id) => api.get(`/tickets/${id}`),
    create: (data) => api.post('/tickets', data),
    update: (id, data) => api.put(`/tickets/${id}`, data),
    delete: (id) => api.delete(`/tickets/${id}`),
    batchDelete: (ticketIds) => api.delete('/tickets', { data: { ticket_ids: ticketIds } }),
    toggle: (id) => api.patch(`/tickets/${id}/toggle`),
    batchComplete: (ticketIds, isCompleted) =>
      api.patch('/tickets/batch-complete', {
        ticket_ids: ticketIds,
        is_completed: isCompleted,
      }),
  }

  export const tagApi = {
    getList: (params) => api.get('/tags', { params }),
    getById: (id) => api.get(`/tags/${id}`),
    create: (data) => api.post('/tags', data),
    update: (id, data) => api.put(`/tags/${id}`, data),
    delete: (id) => api.delete(`/tags/${id}`),
  }
  ```

**验收标准**:
- ✅ 所有 API 方法有类型定义
- ✅ 错误处理逻辑完善
- ✅ 支持请求取消(避免内存泄漏)

#### 3.1.3 Pinia Store 配置

**任务清单**:
- [ ] 创建 Ticket Store (`src/stores/ticket.ts`)
  ```typescript
  import { defineStore } from 'pinia'
  import { ref, computed } from 'vue'

  export const useTicketStore = defineStore('ticket', () => {
    // 状态
    const tickets = ref<Ticket[]>([])
    const filters = ref<Filters>({
      search: '',
      tagIds: [],
      isCompleted: null,
      sortBy: 'createdAt',
      sortOrder: 'desc',
    })
    const selectedTickets = ref<number[]>([])
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Getters
    const filteredTickets = computed(() => {
      let result = tickets.value

      // 搜索过滤
      if (filters.value.search) {
        const keyword = filters.value.search.toLowerCase()
        result = result.filter(t =>
          t.title.toLowerCase().includes(keyword) ||
          t.description?.toLowerCase().includes(keyword)
        )
      }

      // 标签过滤
      if (filters.value.tagIds.length > 0) {
        result = result.filter(t =>
          filters.value.tagIds.every(tagId =>
            t.tags.some(tag => tag.id === tagId)
          )
        )
      }

      // 状态过滤
      if (filters.value.isCompleted !== null) {
        result = result.filter(t => t.isCompleted === filters.value.isCompleted)
      }

      // 排序
      result.sort((a, b) => {
        const field = filters.value.sortBy
        const order = filters.value.sortOrder === 'asc' ? 1 : -1
        if (a[field] < b[field]) return -1 * order
        if (a[field] > b[field]) return 1 * order
        return 0
      })

      return result
    })

    const stats = computed(() => ({
      total: tickets.value.length,
      completed: tickets.value.filter(t => t.isCompleted).length,
      pending: tickets.value.filter(t => !t.isCompleted).length,
    }))

    // Actions
    async function fetchTickets() {
      isLoading.value = true
      error.value = null
      try {
        const data = await ticketApi.getList(filters.value)
        tickets.value = data.items
      } catch (e) {
        error.value = e.message
        throw e
      } finally {
        isLoading.value = false
      }
    }

    async function createTicket(formData: TicketFormData) {
      const data = await ticketApi.create(formData)
      tickets.value.unshift(data)
      return data
    }

    async function updateTicket(id: number, formData: TicketFormData) {
      const data = await ticketApi.update(id, formData)
      const index = tickets.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tickets.value[index] = data
      }
      return data
    }

    async function deleteTicket(id: number) {
      await ticketApi.delete(id)
      tickets.value = tickets.value.filter(t => t.id !== id)
    }

    async function toggleTicket(id: number) {
      const data = await ticketApi.toggle(id)
      const ticket = tickets.value.find(t => t.id === id)
      if (ticket) {
        Object.assign(ticket, data)
      }
    }

    async function batchDelete(ticketIds: number[]) {
      await ticketApi.batchDelete(ticketIds)
      tickets.value = tickets.value.filter(t => !ticketIds.includes(t.id))
      selectedTickets.value = []
    }

    async function batchComplete(ticketIds: number[], isCompleted: boolean) {
      await ticketApi.batchComplete(ticketIds, isCompleted)
      ticketIds.forEach(id => {
        const ticket = tickets.value.find(t => t.id === id)
        if (ticket) ticket.isCompleted = isCompleted
      })
      selectedTickets.value = []
    }

    function setFilters(newFilters: Partial<Filters>) {
      Object.assign(filters.value, newFilters)
    }

    function setSelectedTickets(ticketIds: number[]) {
      selectedTickets.value = ticketIds
    }

    return {
      // 状态
      tickets,
      filters,
      selectedTickets,
      isLoading,
      error,
      // Getters
      filteredTickets,
      stats,
      // Actions
      fetchTickets,
      createTicket,
      updateTicket,
      deleteTicket,
      toggleTicket,
      batchDelete,
      batchComplete,
      setFilters,
      setSelectedTickets,
    }
  })
  ```

- [ ] 创建 Tag Store (`src/stores/tag.ts`)
  ```typescript
  export const useTagStore = defineStore('tag', () => {
    const tags = ref<Tag[]>([])
    const isLoading = ref(false)

    async function fetchTags() {
      const data = await tagApi.getList({ include_usage_count: true })
      tags.value = data.items
    }

    async function createTag(name: string, color?: string) {
      const data = await tagApi.create({
        name,
        color: color || generateColor(),
      })
      tags.value.push(data)
      return data
    }

    async function deleteTag(id: number) {
      await tagApi.delete(id)
      tags.value = tags.value.filter(t => t.id !== id)
    }

    return { tags, isLoading, fetchTags, createTag, deleteTag }
  })
  ```

**验收标准**:
- ✅ Store 逻辑完整
- ✅ 异步操作有错误处理
- ✅ 状态更新符合 Vue 3 响应式规则

### 3.2 通用组件开发

**工期**: 1 天

#### 3.2.1 SearchBar 组件

**任务清单**:
- [ ] 实现 `src/components/common/SearchBar.vue`
  ```vue
  <template>
    <el-input
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :placeholder="placeholder"
      clearable
      @input="handleInput"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>
  </template>

  <script setup lang="ts">
  import { ref, watch } from 'vue'

  interface Props {
    modelValue: string
    placeholder?: string
    debounce?: number
  }

  const props = withDefaults(defineProps<Props>(), {
    placeholder: '搜索...',
    debounce: 300,
  })

  const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void
  }>()

  // 防抖处理
  let debounceTimer: ReturnType<typeof setTimeout>
  function handleInput(value: string) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      emit('update:modelValue', value)
    }, props.debounce)
  }
  </script>
  ```

**验收标准**:
- ✅ 支持双向绑定
- ✅ 防抖功能正常
- ✅ 清空按钮可用

#### 3.2.2 ConfirmDialog 组件

**任务清单**:
- [ ] 实现 `src/components/common/ConfirmDialog.vue`
  ```vue
  <template>
    <el-dialog
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :title="title"
      width="400px"
    >
      <p>{{ message }}</p>
      <template #footer>
        <el-button @click="$emit('update:modelValue', false)">
          取消
        </el-button>
        <el-button type="danger" @click="handleConfirm">
          确认
        </el-button>
      </template>
    </el-dialog>
  </template>

  <script setup lang="ts">
  interface Props {
    modelValue: boolean
    title: string
    message: string
  }

  defineProps<Props>()

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'confirm'): void
  }>()

  function handleConfirm() {
    emit('confirm')
    emit('update:modelValue', false)
  }
  </script>
  ```

**验收标准**:
- ✅ 支持自定义标题和消息
- ✅ 确认/取消按钮功能正常

#### 3.2.3 SortControl 组件

**任务清单**:
- [ ] 实现 `src/components/common/SortControl.vue`
  ```vue
  <template>
    <div class="flex items-center gap-2">
      <el-select :model-value="sortBy" @change="handleSortByChange" style="width: 120px">
        <el-option label="创建时间" value="createdAt" />
        <el-option label="更新时间" value="updatedAt" />
        <el-option label="标题" value="title" />
      </el-select>
      <el-button
        :icon="sortOrder === 'asc' ? SortUp : SortDown"
        @click="toggleSortOrder"
      />
    </div>
  </template>

  <script setup lang="ts">
  interface Props {
    sortBy: string
    sortOrder: 'asc' | 'desc'
  }

  const props = defineProps<Props>()
  const emit = defineEmits<{
    (e: 'update:sortBy', value: string): void
    (e: 'update:sortOrder', value: 'asc' | 'desc'): void
  }>()

  function handleSortByChange(value: string) {
    emit('update:sortBy', value)
  }

  function toggleSortOrder() {
    emit('update:sortOrder', props.sortOrder === 'asc' ? 'desc' : 'asc')
  }
  </script>
  ```

**验收标准**:
- ✅ 排序字段选择正常
- ✅ 排序方向切换正常

### 3.3 Ticket 相关组件

**工期**: 1.5 天

#### 3.3.1 TicketCard 组件

**任务清单**:
- [ ] 实现 `src/components/tickets/TicketCard.vue`
  ```vue
  <template>
    <div
      class="ticket-card"
      :class="{ 'is-completed': ticket.isCompleted, 'is-selected': isSelected }"
      @click="handleClick"
    >
      <el-checkbox
        :model-value="isSelected"
        @update:model-value="$emit('select', ticket.id)"
        @click.stop
      />

      <div class="ticket-content">
        <h3 class="ticket-title">{{ ticket.title }}</h3>
        <p class="ticket-description">{{ ticket.description }}</p>

        <div class="ticket-tags">
          <el-tag
            v-for="tag in ticket.tags"
            :key="tag.id"
            :color="tag.color"
            size="small"
            @click.stop="$emit('filterByTag', tag)"
          >
            {{ tag.name }}
          </el-tag>
        </div>

        <div class="ticket-meta">
          <span class="ticket-time">{{ formatTime(ticket.createdAt) }}</span>
        </div>
      </div>

      <div class="ticket-actions">
        <el-button
          :type="ticket.isCompleted ? 'warning' : 'success'"
          :icon="ticket.isCompleted ? Refresh : Check"
          size="small"
          @click.stop="$emit('toggle', ticket.id)"
        >
          {{ ticket.isCompleted ? '取消完成' : '完成' }}
        </el-button>
        <el-button
          type="primary"
          :icon="Edit"
          size="small"
          @click.stop="$emit('edit', ticket)"
        >
          编辑
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          size="small"
          @click.stop="$emit('delete', ticket.id)"
        >
          删除
        </el-button>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { Ticket } from '@/types'
  import { Edit, Delete, Check, Refresh } from '@element-plus/icons-vue'
  import { formatDistanceToNow } from 'date-fns'
  import { zhCN } from 'date-fns/locale'

  interface Props {
    ticket: Ticket
    isSelected: boolean
  }

  defineProps<Props>()

  const emit = defineEmits<{
    (e: 'select', id: number): void
    (e: 'edit', ticket: Ticket): void
    (e: 'delete', id: number): void
    (e: 'toggle', id: number): void
    (e: 'filterByTag', tag: Tag): void
  }>()

  function formatTime(time: string) {
    return formatDistanceToNow(new Date(time), {
      addSuffix: true,
      locale: zhCN,
    })
  }

  function handleClick() {
    emit('select', props.ticket.id)
  }
  </script>

  <style scoped>
  .ticket-card {
    /* UnoCSS 或自定义样式 */
  }
  </style>
  ```

**验收标准**:
- ✅ 显示所有 Ticket 信息
- ✅ 标签颜色正确显示
- ✅ 完成/未完成状态视觉区分
- ✅ 所有操作按钮可用

#### 3.3.2 TicketForm 组件

**任务清单**:
- [ ] 实现 `src/components/tickets/TicketForm.vue`
  ```vue
  <template>
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          maxlength="200"
          show-word-limit
          placeholder="请输入标题"
        />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="4"
          maxlength="2000"
          show-word-limit
          placeholder="请输入描述(可选)"
        />
      </el-form-item>

      <el-form-item label="标签" prop="tagIds">
        <TagSelector
          v-model="formData.tagIds"
          :available-tags="tags"
          show-create-button
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
        <el-button @click="$emit('cancel')">取消</el-button>
      </el-form-item>
    </el-form>
  </template>

  <script setup lang="ts">
  import { ref, reactive, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'
  import { Ticket, TicketFormData } from '@/types'

  interface Props {
    ticket?: Ticket
    tags: Tag[]
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    (e: 'submit', data: TicketFormData): void
    (e: 'cancel'): void
  }>()

  const formRef = ref<FormInstance>()
  const isEdit = computed(() => !!props.ticket)

  const formData = reactive<TicketFormData>({
    title: '',
    description: '',
    tagIds: [],
  })

  const rules: FormRules = {
    title: [
      { required: true, message: '请输入标题', trigger: 'blur' },
      { min: 1, max: 200, message: '标题长度为 1-200 个字符', trigger: 'blur' },
    ],
    description: [
      { max: 2000, message: '描述最多 2000 个字符', trigger: 'blur' },
    ],
  }

  // 如果是编辑模式,填充表单数据
  watch(
    () => props.ticket,
    (ticket) => {
      if (ticket) {
        formData.title = ticket.title
        formData.description = ticket.description || ''
        formData.tagIds = ticket.tags.map(t => t.id)
      }
    },
    { immediate: true }
  )

  async function handleSubmit() {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      emit('submit', { ...formData })
    } catch (error) {
      ElMessage.error('请检查表单输入')
    }
  }
  </script>
  ```

**验收标准**:
- ✅ 表单验证规则正确
- ✅ 创建/编辑模式切换正常
- ✅ 标签选择功能正常

#### 3.3.3 TicketList 组件

**任务清单**:
- [ ] 实现 `src/components/tickets/TicketList.vue`
  ```vue
  <template>
    <div class="ticket-list">
      <!-- 批量操作栏 -->
      <div v-if="selectedTickets.length > 0" class="batch-actions">
        <span>已选择 {{ selectedTickets.length }} 项</span>
        <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
          批量删除
        </el-button>
        <el-button type="success" :icon="Check" @click="handleBatchComplete">
          批量完成
        </el-button>
        <el-button @click="clearSelection">取消选择</el-button>
      </div>

      <!-- Ticket 列表 -->
      <div class="ticket-cards">
        <TicketCard
          v-for="ticket in tickets"
          :key="ticket.id"
          :ticket="ticket"
          :is-selected="selectedTickets.includes(ticket.id)"
          @select="handleSelect"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle="handleToggle"
          @filter-by-tag="handleFilterByTag"
        />
      </div>

      <!-- 空状态 -->
      <el-empty v-if="tickets.length === 0" description="暂无数据" />
    </div>
  </template>

  <script setup lang="ts">
  import { Ticket } from '@/types'
  import { Delete, Check } from '@element-plus/icons-vue'

  interface Props {
    tickets: Ticket[]
    selectedTickets: number[]
  }

  const props = defineProps<Props>()

  const emit = defineEmits<{
    (e: 'update:selectedTickets', ids: number[]): void
    (e: 'edit', ticket: Ticket): void
    (e: 'delete', id: number): void
    (e: 'toggle', id: number): void
    (e: 'batchDelete', ids: number[]): void
    (e: 'batchComplete', ids: number[]): void
    (e: 'filterByTag', tag: Tag): void
  }>()

  function handleSelect(id: number) {
    const isSelected = props.selectedTickets.includes(id)
    const newIds = isSelected
      ? props.selectedTickets.filter(i => i !== id)
      : [...props.selectedTickets, id]
    emit('update:selectedTickets', newIds)
  }

  function clearSelection() {
    emit('update:selectedTickets', [])
  }

  function handleEdit(ticket: Ticket) {
    emit('edit', ticket)
  }

  function handleDelete(id: number) {
    emit('delete', id)
  }

  function handleToggle(id: number) {
    emit('toggle', id)
  }

  function handleFilterByTag(tag: Tag) {
    emit('filterByTag', tag)
  }

  function handleBatchDelete() {
    emit('batchDelete', props.selectedTickets)
  }

  function handleBatchComplete() {
    emit('batchComplete', props.selectedTickets)
  }
  </script>
  ```

**验收标准**:
- ✅ 列表展示正常
- ✅ 批量操作功能正常
- ✅ 空状态显示正常

#### 3.3.4 BatchActions 组件

**任务清单**:
- [ ] 实现批量操作逻辑
  - 批量删除
  - 批量完成
  - 二次确认对话框

**验收标准**:
- ✅ 批量操作触发确认对话框
- ✅ 操作成功后清空选择

### 3.4 Tag 相关组件

**工期**: 0.5 天

#### 3.4.1 TagBadge 组件

**任务清单**:
- [ ] 实现 `src/components/tags/TagBadge.vue`
  ```vue
  <template>
    <el-tag
      :style="{ backgroundColor: tag.color }"
      :closable="showClose"
      @close="handleClose"
      @click="handleClick"
      class="tag-badge"
    >
      {{ tag.name }}
    </el-tag>
  </template>

  <script setup lang="ts">
  import { Tag } from '@/types'

  interface Props {
    tag: Tag
    showClose?: boolean
    clickable?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    showClose: false,
    clickable: false,
  })

  const emit = defineEmits<{
    (e: 'remove', tagId: number): void
    (e: 'click', tag: Tag): void
  }>()

  function handleClose() {
    emit('remove', props.tag.id)
  }

  function handleClick() {
    if (props.clickable) {
      emit('click', props.tag)
    }
  }
  </script>

  <style scoped>
  .tag-badge {
    cursor: pointer;
  }
  </style>
  ```

**验收标准**:
- ✅ 标签颜色显示正确
- ✅ 关闭按钮功能正常

#### 3.4.2 TagSelector 组件

**任务清单**:
- [ ] 实现 `src/components/tags/TagSelector.vue`
  ```vue
  <template>
    <div class="tag-selector">
      <el-select
        :model-value="selectedTags"
        @update:model-value="handleChange"
        multiple
        filterable
        allow-create
        placeholder="选择标签"
        @create="handleCreate"
      >
        <el-option
          v-for="tag in availableTags"
          :key="tag.id"
          :label="tag.name"
          :value="tag.id"
        >
          <span :style="{ color: tag.color }">●</span>
          {{ tag.name }}
        </el-option>
      </el-select>

      <div v-if="showCreateButton" class="selected-tags">
        <TagBadge
          v-for="tag in selectedTagObjects"
          :key="tag.id"
          :tag="tag"
          show-close
          @remove="handleRemove"
        />
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { computed } from 'vue'
  import { Tag } from '@/types'
  import TagBadge from './TagBadge.vue'

  interface Props {
    selectedTags: number[]
    availableTags: Tag[]
    showCreateButton?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    showCreateButton: false,
  })

  const emit = defineEmits<{
    (e: 'update:selectedTags', tagIds: number[]): void
    (e: 'createNew', name: string): void
  }>()

  const selectedTagObjects = computed(() =>
    props.availableTags.filter(t => props.selectedTags.includes(t.id))
  )

  function handleChange(tagIds: number[]) {
    emit('update:selectedTags', tagIds)
  }

  function handleRemove(tagId: number) {
    const newTagIds = props.selectedTags.filter(id => id !== tagId)
    emit('update:selectedTags', newTagIds)
  }

  function handleCreate(name: string) {
    emit('createNew', name)
  }
  </script>
  ```

**验收标准**:
- ✅ 多选功能正常
- ✅ 创建新标签功能正常
- ✅ 已选标签显示正确

#### 3.4.3 TagManager 组件

**任务清单**:
- [ ] 实现标签管理对话框
  ```vue
  <template>
    <el-dialog
      v-model="visible"
      title="标签管理"
      width="600px"
    >
      <!-- 创建标签表单 -->
      <el-form :model="formData" inline>
        <el-form-item label="标签名称">
          <el-input v-model="formData.name" placeholder="输入标签名称" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="formData.color" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreate">创建</el-button>
        </el-form-item>
      </el-form>

      <!-- 标签列表 -->
      <el-table :data="tags" style="margin-top: 20px">
        <el-table-column prop="name" label="名称">
          <template #default="{ row }">
            <el-tag :style="{ backgroundColor: row.color }">
              {{ row.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="使用次数" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </template>

  <script setup lang="ts">
  import { ref } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Tag } from '@/types'
  import { useTagStore } from '@/stores/tag'

  const tagStore = useTagStore()

  const visible = ref(false)
  const formData = ref({
    name: '',
    color: generateColor(),
  })

  const tags = computed(() => tagStore.tags)

  async function handleCreate() {
    try {
      await tagStore.createTag(formData.value.name, formData.value.color)
      ElMessage.success('标签创建成功')
      formData.value.name = ''
      formData.value.color = generateColor()
    } catch (error) {
      ElMessage.error('创建失败: ' + error.message)
    }
  }

  async function handleDelete(id: number) {
    try {
      await ElMessageBox.confirm('确定删除此标签吗?', '警告', {
        type: 'warning',
      })
      await tagStore.deleteTag(id)
      ElMessage.success('标签删除成功')
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败: ' + error.message)
      }
    }
  }

  defineExpose({ visible })
  </script>
  ```

**验收标准**:
- ✅ 创建标签功能正常
- ✅ 删除标签有二次确认
- ✅ 标签列表刷新正常

### 3.5 布局组件

**工期**: 0.5 天

#### 3.5.1 Header 组件

**任务清单**:
- [ ] 实现 `src/components/layout/Header.vue`
  - 显示 Logo 和标题
  - 显示统计信息(总数、已完成、未完成)
  - 创建新 Ticket 按钮

**验收标准**:
- ✅ 统计数据正确显示
- ✅ 创建按钮功能正常

#### 3.5.2 FilterSidebar 组件

**任务清单**:
- [ ] 实现 `src/components/layout/FilterSidebar.vue`
  ```vue
  <template>
    <div class="filter-sidebar">
      <!-- 标签筛选 -->
      <div class="filter-section">
        <h4>标签筛选</h4>
        <el-checkbox-group v-model="selectedTagIds" @change="handleTagChange">
          <el-checkbox
            v-for="tag in tags"
            :key="tag.id"
            :label="tag.id"
          >
            <span :style="{ color: tag.color }">●</span>
            {{ tag.name }} ({{ tag.usageCount }})
          </el-checkbox>
          <el-checkbox label="no-tags">
            无标签
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 状态筛选 -->
      <div class="filter-section">
        <h4>状态筛选</h4>
        <el-radio-group v-model="statusFilter" @change="handleStatusChange">
          <el-radio :label="null">全部</el-radio>
          <el-radio :label="false">未完成</el-radio>
          <el-radio :label="true">已完成</el-radio>
        </el-radio-group>
      </div>

      <!-- 管理标签按钮 -->
      <el-button type="primary" @click="openTagManager">
        管理标签
      </el-button>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, watch } from 'vue'
  import { useTagStore } from '@/stores/tag'

  const tagStore = useTagStore()

  const selectedTagIds = ref<number[]>([])
  const statusFilter = ref<boolean | null>(null)

  const emit = defineEmits<{
    (e: 'filterChange', filters: Filters): void
    (e: 'openTagManager'): void
  }>()

  function handleTagChange(tagIds: number[]) {
    emit('filterChange', {
      tagIds,
      isCompleted: statusFilter.value,
    })
  }

  function handleStatusChange(status: boolean | null) {
    emit('filterChange', {
      tagIds: selectedTagIds.value,
      isCompleted: status,
    })
  }

  function openTagManager() {
    emit('openTagManager')
  }
  </script>
  ```

**验收标准**:
- ✅ 标签筛选功能正常
- ✅ 状态筛选功能正常
- ✅ 管理标签按钮可打开对话框

### 3.6 主页面集成

**工期**: 1 天

#### 3.6.1 App.vue 主页面

**任务清单**:
- [ ] 实现 `src/App.vue`
  ```vue
  <template>
    <div id="app" class="min-h-screen bg-gray-50">
      <!-- Header -->
      <Header
        :stats="stats"
        @create="handleCreateTicket"
      />

      <div class="container mx-auto px-4 py-6">
        <div class="flex gap-6">
          <!-- Sidebar -->
          <FilterSidebar
            :tags="tags"
            @filter-change="handleFilterChange"
            @open-tag-manager="tagManagerVisible = true"
          />

          <!-- Main Content -->
          <div class="flex-1">
            <!-- 搜索和排序 -->
            <div class="mb-4 flex items-center gap-4">
              <SearchBar v-model="searchKeyword" />
              <SortControl
                v-model:sort-by="sortBy"
                v-model:sort-order="sortOrder"
              />
            </div>

            <!-- Ticket List -->
            <TicketList
              :tickets="filteredTickets"
              :selected-tickets="selectedTickets"
              @update:selected-tickets="setSelectedTickets"
              @edit="handleEditTicket"
              @delete="handleDeleteTicket"
              @toggle="handleToggleTicket"
              @batch-delete="handleBatchDelete"
              @batch-complete="handleBatchComplete"
              @filter-by-tag="handleFilterByTag"
            />
          </div>
        </div>
      </div>

      <!-- Ticket Form Dialog -->
      <el-dialog
        v-model="formVisible"
        :title="isEdit ? '编辑 Ticket' : '创建 Ticket'"
        width="600px"
      >
        <TicketForm
          :ticket="editingTicket"
          :tags="tags"
          @submit="handleSubmitTicket"
          @cancel="formVisible = false"
        />
      </el-dialog>

      <!-- Tag Manager Dialog -->
      <TagManager ref="tagManagerRef" />

      <!-- Loading -->
      <el-loading v-if="isLoading" />
    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { useTicketStore } from '@/stores/ticket'
  import { useTagStore } from '@/stores/tag'
  import { Ticket, TicketFormData } from '@/types'

  const ticketStore = useTicketStore()
  const tagStore = useTagStore()

  const formVisible = ref(false)
  const tagManagerVisible = ref(false)
  const isEdit = ref(false)
  const editingTicket = ref<Ticket>()
  const searchKeyword = ref('')
  const sortBy = ref('createdAt')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  const tags = computed(() => tagStore.tags)
  const filteredTickets = computed(() => ticketStore.filteredTickets)
  const selectedTickets = computed(() => ticketStore.selectedTickets)
  const stats = computed(() => ticketStore.stats)
  const isLoading = computed(() => ticketStore.isLoading)

  onMounted(async () => {
    try {
      await Promise.all([
        ticketStore.fetchTickets(),
        tagStore.fetchTags(),
      ])
    } catch (error) {
      ElMessage.error('加载数据失败: ' + error.message)
    }
  })

  // 搜索和排序
  watch([searchKeyword, sortBy, sortOrder], () => {
    ticketStore.setFilters({
      search: searchKeyword.value,
      sortBy: sortBy.value,
      sortOrder: sortOrder.value,
    })
  })

  function handleCreateTicket() {
    isEdit.value = false
    editingTicket.value = undefined
    formVisible.value = true
  }

  function handleEditTicket(ticket: Ticket) {
    isEdit.value = true
    editingTicket.value = ticket
    formVisible.value = true
  }

  async function handleSubmitTicket(formData: TicketFormData) {
    try {
      if (isEdit.value && editingTicket.value) {
        await ticketStore.updateTicket(editingTicket.value.id, formData)
        ElMessage.success('更新成功')
      } else {
        await ticketStore.createTicket(formData)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
    } catch (error) {
      ElMessage.error('操作失败: ' + error.message)
    }
  }

  async function handleDeleteTicket(id: number) {
    try {
      await ElMessageBox.confirm('确定删除此 Ticket 吗?', '警告', {
        type: 'warning',
      })
      await ticketStore.deleteTicket(id)
      ElMessage.success('删除成功')
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败: ' + error.message)
      }
    }
  }

  async function handleToggleTicket(id: number) {
    try {
      await ticketStore.toggleTicket(id)
    } catch (error) {
      ElMessage.error('操作失败: ' + error.message)
    }
  }

  async function handleBatchDelete() {
    try {
      await ElMessageBox.confirm(
        `确定删除选中的 ${selectedTickets.value.length} 个 Ticket 吗?`,
        '警告',
        { type: 'warning' }
      )
      await ticketStore.batchDelete(selectedTickets.value)
      ElMessage.success('批量删除成功')
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('操作失败: ' + error.message)
      }
    }
  }

  async function handleBatchComplete() {
    try {
      await ticketStore.batchComplete(selectedTickets.value, true)
      ElMessage.success('批量完成成功')
    } catch (error) {
      ElMessage.error('操作失败: ' + error.message)
    }
  }

  function handleFilterChange(filters: any) {
    ticketStore.setFilters(filters)
  }

  function handleFilterByTag(tag: Tag) {
    ticketStore.setFilters({ tagIds: [tag.id] })
  }

  function setSelectedTickets(ids: number[]) {
    ticketStore.setSelectedTickets(ids)
  }
  </script>

  <style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
  }
  </style>
  ```

**验收标准**:
- ✅ 页面布局符合设计
- ✅ 所有功能集成正常
- ✅ 数据流转正确

### 3.7 样式系统

**工期**: 0.5 天

#### 3.7.1 设计令牌

**任务清单**:
- [ ] 创建 `src/styles/design-tokens.css`
  ```css
  :root {
    /* 颜色 */
    --color-primary: #3B82F6;
    --color-success: #10B981;
    --color-warning: #F59E0B;
    --color-danger: #EF4444;
    --color-background: #FFFFFF;
    --color-surface: #F3F4F6;
    --color-text: #111827;
    --color-text-secondary: #6B7280;

    /* 间距 */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    /* 圆角 */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;

    /* 阴影 */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
  ```

#### 3.7.2 UnoCSS 配置

**任务清单**:
- [ ] 配置 `unocss.config.ts`
  ```typescript
  import { defineConfig } from 'unocss'

  export default defineConfig({
    presets: [],
    shortcuts: {
      'flex-center': 'flex items-center justify-center',
      'flex-between': 'flex items-center justify-between',
      'btn-primary': 'bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md',
      'card': 'bg-white rounded-lg shadow-md p-4',
    },
    theme: {
      colors: {
        primary: {
          50: '#EFF6FF',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
      },
    },
  })
  ```

**验收标准**:
- ✅ 设计令牌定义完整
- ✅ UnoCSS 配置生效
- ✅ 样式在组件中应用正常

#### 3.7.3 响应式适配

**任务清单**:
- [ ] 移动端适配 (<768px)
  - 单列布局
  - 侧边栏折叠为抽屉
  - 调整字体大小和间距

- [ ] 平板适配 (768px-1023px)
  - 侧边栏可折叠
  - 卡片布局自适应

- [ ] 桌面适配 (≥1024px)
  - 完整双列布局
  - 最佳显示效果

**验收标准**:
- ✅ 在不同设备上显示正常
- ✅ 触摸交互友好
- ✅ 布局不破裂

---

## 4. 集成测试阶段

**工期**: 2-3 天
**目标**: 完成前后端联调和端到端测试

### 4.1 前后端联调

**工期**: 1 天

**任务清单**:
- [ ] API 联调测试
  - 测试所有 API 端点
  - 验证请求/响应格式
  - 验证错误处理

- [ ] 数据流转测试
  - 创建 Ticket → 数据保存 → 前端刷新
  - 更新 Ticket → 状态同步
  - 删除 Ticket → 列表更新

- [ ] 异常场景测试
  - 网络错误处理
  - 服务器错误处理
  - 超时处理

**验收标准**:
- ✅ 所有功能可正常使用
- ✅ 数据一致性正确
- ✅ 错误提示友好

### 4.2 E2E 测试

**工期**: 1 天

**任务清单**:
- [ ] 安装 Playwright
  ```bash
  npm install -D @playwright/test
  ```

- [ ] 编写 E2E 测试用例
  ```typescript
  import { test, expect } from '@playwright/test'

  test.describe('Ticket Management', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5173')
    })

    test('create a new ticket', async ({ page }) => {
      await page.click('button:has-text("New Ticket")')
      await page.fill('[name="title"]', 'Test Ticket')
      await page.fill('[name="description"]', 'Test Description')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=Test Ticket')).toBeVisible()
    })

    test('filter tickets by tag', async ({ page }) => {
      await page.check('input[type="checkbox"][value="1"]')
      await expect(page.locator('.ticket-card')).toHaveCount(5)
    })

    test('search tickets', async ({ page }) => {
      await page.fill('input[placeholder*="搜索"]', 'Bug')
      await expect(page.locator('.ticket-card')).toHaveCount(3)
    })

    test('complete a ticket', async ({ page }) => {
      await page.click('.ticket-card:first-child .toggle-button')
      await expect(page.locator('.ticket-card:first-child')).toHaveClass(/is-completed/)
    })

    test('batch delete tickets', async ({ page }) => {
      await page.check('.ticket-card:nth-child(1) .el-checkbox')
      await page.check('.ticket-card:nth-child(2) .el-checkbox')
      await page.click('button:has-text("批量删除")')
      await page.click('button:has-text("确认")')
      await expect(page.locator('.ticket-card')).toHaveCount(8)
    })
  })
  ```

**验收标准**:
- ✅ E2E 测试覆盖主要用户流程
- ✅ 测试可以在 CI 中运行
- ✅ 测试稳定性良好

### 4.3 性能测试

**工期**: 0.5 天

**任务清单**:
- [ ] 前端性能测试
  - 使用 Lighthouse 测试
  - 目标: Performance > 90
  - 检查首次加载时间
  - 检查 API 响应时间

- [ ] 后端性能测试
  - 使用 Locust 或 Apache Bench
  - 测试并发请求
  - 目标: 1000+ Ticket 数据流畅运行
  - API 响应时间 < 200ms

**验收标准**:
- ✅ 页面加载时间 < 2s
- ✅ API 响应时间 < 200ms
- ✅ 搜索响应时间 < 100ms

---

## 5. 部署优化阶段

**工期**: 2-3 天
**目标**: 完成生产环境部署和性能优化

### 5.1 Docker 部署

**工期**: 1 天

**任务清单**:
- [ ] 编写后端 Dockerfile
  ```dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  COPY pyproject.toml ./
  RUN pip install --no-cache-dir -e .

  COPY ./app ./app

  EXPOSE 8000

  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

- [ ] 编写前端 Dockerfile
  ```dockerfile
  FROM node:20-alpine as builder

  WORKDIR /app

  COPY package*.json ./
  RUN npm ci

  COPY . .
  RUN npm run build

  FROM nginx:alpine

  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]
  ```

- [ ] 配置 docker-compose.yml
  ```yaml
  version: '3.8'

  services:
    postgres:
      image: postgres:15-alpine
      environment:
        POSTGRES_DB: ticketdb
        POSTGRES_USER: ticketuser
        POSTGRES_PASSWORD: ticketpass
      volumes:
        - postgres_data:/var/lib/postgresql/data

    backend:
      build: ./backend
      environment:
        DATABASE_URL: postgresql://ticketuser:ticketpass@postgres:5432/ticketdb
      depends_on:
        - postgres
      ports:
        - "8000:8000"

    frontend:
      build: ./frontend
      ports:
        - "80:80"
      depends_on:
        - backend

  volumes:
    postgres_data:
  ```

**验收标准**:
- ✅ Docker 镜像构建成功
- ✅ `docker-compose up` 可以正常启动所有服务
- ✅ 数据持久化正常

### 5.2 Nginx 配置

**工期**: 0.5 天

**任务清单**:
- [ ] 配置 Nginx 反向代理
  ```nginx
  server {
      listen 80;
      server_name localhost;

      # 前端静态文件
      location / {
          root /usr/share/nginx/html;
          try_files $uri $uri/ /index.html;
      }

      # API 代理
      location /api {
          proxy_pass http://backend:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;

          # CORS headers
          add_header Access-Control-Allow-Origin *;
          add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS';
          add_header Access-Control-Allow-Headers 'Content-Type, Authorization';
      }

      # Gzip 压缩
      gzip on;
      gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
  }
  ```

**验收标准**:
- ✅ 静态文件正常访问
- ✅ API 代理正常工作
- ✅ CORS 配置正确

### 5.3 性能优化

**工期**: 0.5 天

**任务清单**:
- [ ] 前端优化
  - 代码分割(Vite 自动)
  - 路由懒加载
  - 图片压缩和懒加载
  - 启用 Gzip 压缩

- [ ] 后端优化
  - 数据库查询优化(添加索引)
  - 使用连接池
  - API 响应缓存(可选)
  - 分页查询

- [ ] 数据库优化
  - 添加必要的索引
  - 定期 VACUUM
  - 查询分析(EXPLAIN ANALYZE)

**验收标准**:
- ✅ 页面加载时间 < 2s
- ✅ API 响应时间 < 200ms
- ✅ 数据库查询时间 < 50ms

---

## 6. 验收交付阶段

**工期**: 2-3 天
**目标**: 完成文档编写和项目交付

### 6.1 文档编写

**工期**: 1 天

**任务清单**:
- [ ] README.md
  - 项目介绍
  - 功能特性
  - 技术栈
  - 快速开始
  - 开发指南
  - 部署指南

- [ ] API 文档
  - FastAPI 自动生成 (`/docs`)
  - 导出为 PDF/HTML(可选)

- [ ] 用户手册
  - 功能说明
  - 操作指南
  - 常见问题

- [ ] 开发文档
  - 架构设计
  - 数据库设计
  - 代码规范
  - 测试指南

**验收标准**:
- ✅ 文档结构清晰
- ✅ 内容完整准确
- ✅ 图文并茂

### 6.2 测试验收

**工期**: 1 天

**任务清单**:
- [ ] 功能测试
  - 所有功能点测试
  - 边界条件测试
  - 异常场景测试

- [ ] 兼容性测试
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+

- [ ] 性能测试
  - Lighthouse 测试
  - API 性能测试
  - 数据库性能测试

- [ ] 安全测试
  - SQL 注入测试
  - XSS 测试
  - CORS 测试

**验收标准**:
- ✅ 所有测试通过
- ✅ 无严重 Bug
- ✅ 性能达标

### 6.3 项目交付

**工期**: 1 天

**任务清单**:
- [ ] 代码交付
  - 推送到 Git 仓库
  - 打 tag(如 v1.0.0)
  - 生成 Release Note

- [ ] 部署交付
  - 提供部署文档
  - 提供部署脚本
  - 生产环境部署

- [ ] 培训交付(可选)
  - 用户培训
  - 开发者培训
  - 运维培训

**验收标准**:
- ✅ 代码仓库完整
- ✅ 文档齐全
- ✅ 部署成功

---

## 附录

### A. 开发环境检查清单

**开发工具**:
- [ ] Python 3.11+
- [ ] Node.js 20+
- [ ] Docker & Docker Compose
- [ ] Git
- [ ] VS Code / WebStorm

**浏览器**:
- [ ] Chrome 90+
- [ ] Firefox 88+ (测试用)

**数据库**:
- [ ] PostgreSQL 15+ (或 Docker 版)

### B. Git 工作流建议

**分支策略**:
- `main` - 主分支,生产环境代码
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

**提交规范**:
```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

### C. 风险点和注意事项

**技术风险**:
1. **数据库迁移**: 初次迁移可能失败,需要测试
   - 缓解: 在本地充分测试后再执行

2. **前后端数据格式不一致**: 类型定义可能不同步
   - 缓解: 使用 OpenAPI 生成前端类型

3. **性能问题**: 大量数据时可能变慢
   - 缓解: 及时做性能测试和优化

**进度风险**:
1. **需求变更**: 可能导致返工
   - 缓解: 明确需求后再开发

2. **技术难度**: 某些功能可能比预期复杂
   - 缓解: 预留缓冲时间

### D. 常见问题 FAQ

**Q1: 数据库连接失败?**
```bash
# 检查 PostgreSQL 是否运行
docker ps

# 检查连接字符串
DATABASE_URL=postgresql://ticketuser:ticketpass@localhost:5432/ticketdb
```

**Q2: CORS 错误?**
```python
# 确保后端配置了正确的 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    # ...
)
```

**Q3: 前端打包后 404?**
```nginx
# Nginx 配置需要添加
try_files $uri $uri/ /index.html;
```

### E. 后续优化方向

**短期优化**:
- [ ] 添加用户认证
- [ ] 添加优先级字段
- [ ] 添加截止日期
- [ ] 支持拖拽排序

**长期优化**:
- [ ] 实时更新(WebSocket)
- [ ] 全文搜索(Elasticsearch)
- [ ] 缓存优化(Redis)
- [ ] 移动端 App
- [ ] 数据分析仪表板

---

**文档版本**: v1.0
**创建日期**: 2025-01-15
**最后更新**: 2025-01-15
**作者**: AI Assistant
**基于文档**: 0001-spec-by-claude.md
