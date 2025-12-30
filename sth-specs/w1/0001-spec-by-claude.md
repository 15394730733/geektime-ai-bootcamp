# Ticket 标签管理系统 - 需求与设计文档

## 1. 项目概述

### 1.1 项目背景
构建一个简单而高效的 Ticket 标签分类和管理工具，帮助用户通过标签系统组织和管理任务/工单（ticket）。

### 1.2 项目目标
- 提供直观的 Ticket 管理界面
- 实现灵活的标签分类系统
- 支持快速搜索和筛选
- 简洁的用户体验，无需复杂的用户系统

### 1.3 技术栈
- **后端**: Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **前端**: TypeScript, Vite, Vue 3, Element Plus, UnoCSS
- **开发工具**: Docker, Docker Compose, Git

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 Ticket 管理
- **创建 Ticket**
  - 输入标题（必填，最多 200 字符）
  - 输入描述（可选，最多 2000 字符）
  - 选择标签（可选，支持多选）
  - 默认状态为未完成

- **编辑 Ticket**
  - 修改标题、描述、标签
  - 保留原有状态

- **删除 Ticket**
  - 单个删除
  - 批量删除
  - 删除前二次确认

- **完成/取消完成 Ticket**
  - 一键切换完成状态
  - 视觉上区分完成/未完成状态

#### 2.1.2 标签管理
- **创建标签**
  - 标签名称（必填，最多 50 字符）
  - 自动生成唯一颜色（可自定义）
  - 标签名称唯一性校验

- **删除标签**
  - 删除标签时从所有 Ticket 中移除该标签
  - 删除前二次确认

- **查看标签**
  - 标签列表展示（名称、颜色、使用次数）
  - 按创建时间或使用次数排序

#### 2.1.3 筛选与搜索
- **按标签筛选**
  - 单标签筛选
  - 多标签组合筛选（AND/OR 逻辑）
  - 显示无标签的 Ticket

- **按标题搜索**
  - 实时搜索（输入时即时筛选）
  - 支持模糊匹配
  - 搜索结果高亮显示

- **组合筛选**
  - 标签 + 搜索关键词组合
  - 完成状态 + 标签组合

#### 2.1.4 数据展示
- **Ticket 列表**
  - 卡片式或列表式展示
  - 显示：标题、描述预览、标签、状态、创建时间
  - 支持排序：创建时间、更新时间、标题
  - 支持批量操作：批量删除、批量完成

- **统计信息**
  - 总 Ticket 数量
  - 已完成/未完成数量
  - 标签使用统计

### 2.2 辅助功能

#### 2.2.1 数据持久化
- 所有数据存储在 PostgreSQL 数据库
- 自动保存，无需手动操作

#### 2.2.2 响应式设计
- 支持桌面端（1200px+）
- 支持平板端（768px-1199px）
- 支持移动端（<768px）

#### 2.2.3 错误处理
- 网络错误提示
- 表单验证提示
- 操作失败重试机制

---

## 3. 非功能性需求

### 3.1 性能要求
- 页面首次加载时间 < 2s
- API 响应时间 < 200ms（本地网络）
- 支持 1000+ Ticket 数据流畅运行
- 搜索响应时间 < 100ms

### 3.2 安全要求
- SQL 注入防护
- XSS 攻击防护
- API 输入验证和清理
- CORS 配置

### 3.3 可维护性
- 代码结构清晰，模块化设计
- 完善的类型定义（TypeScript + Pydantic）
- 代码注释覆盖率 > 60%
- 遵循 PEP 8 和 ESLint 规范

### 3.4 可扩展性
- 预留用户系统扩展接口
- 预留优先级字段扩展
- 预留截止日期字段扩展
- API 版本化管理（v1）

### 3.5 兼容性
- 支持 Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- 支持 Python 3.11+
- 支持 PostgreSQL 14+

---

## 4. 技术架构设计

### 4.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                           │
│                 (Vue 3 + Element Plus + UnoCSS)         │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI 后端                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   API 路由   │  │  业务逻辑层 │  │  数据访问层  │     │
│  │  (routes)   │  │ (services)  │  │   (CRUD)    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL 数据库                        │
│         (tickets, tags, ticket_tags 表)                 │
└─────────────────────────────────────────────────────────┘
```

### 4.2 后端架构

#### 4.2.1 目录结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── crud/                   # CRUD 操作
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── tickets.py
│   │   └── tags.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── color_generator.py  # 标签颜色生成
├── alembic/                    # 数据库迁移
│   ├── versions/
│   └── env.py
├── tests/                      # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_tickets.py
│   └── test_tags.py
├── alembic.ini                 # Alembic 配置
├── pyproject.toml              # 项目依赖
└── .env.example                # 环境变量示例
```

#### 4.2.2 技术选型理由
- **FastAPI**: 高性能、自动文档生成、类型验证
- **SQLAlchemy**: 成熟的 ORM，支持复杂查询
- **Alembic**: 数据库版本控制和迁移
- **Pydantic**: 数据验证和序列化
- **pytest**: 测试框架

### 4.3 前端架构

#### 4.3.1 目录结构
```
frontend/
├── src/
│   ├── main.ts                 # 应用入口
│   ├── App.vue                 # 根组件
│   ├── components/             # 组件
│   │   ├── tickets/            # Ticket 相关组件
│   │   │   ├── TicketList.vue
│   │   │   ├── TicketCard.vue
│   │   │   ├── TicketForm.vue
│   │   │   └── BatchActions.vue
│   │   ├── tags/               # 标签相关组件
│   │   │   ├── TagManager.vue
│   │   │   ├── TagBadge.vue
│   │   │   └── TagSelector.vue
│   │   ├── layout/             # 布局组件
│   │   │   ├── Header.vue
│   │   │   └── FilterSidebar.vue
│   │   └── common/             # 通用组件
│   │       ├── SearchBar.vue
│   │       ├── ConfirmDialog.vue
│   │       └── SortControl.vue
│   ├── services/               # API 服务
│   │   └── api.ts
│   ├── stores/                 # Pinia 状态管理
│   │   ├── ticket.ts
│   │   └── tag.ts
│   ├── types/                  # TypeScript 类型
│   │   ├── ticket.ts
│   │   └── tag.ts
│   ├── utils/                  # 工具函数
│   │   ├── index.ts
│   │   └── colorUtils.ts
│   └── styles/                 # 样式文件
│       ├── index.css
│       └── design-tokens.css
├── public/                     # 静态资源
├── index.html
├── vite.config.ts              # Vite 配置
├── unocss.config.ts            # UnoCSS 配置
├── tsconfig.json               # TypeScript 配置
├── package.json                # 依赖管理
└── auto-imports.d.ts           # UnoCSS 自动导入类型
```

#### 4.3.2 技术选型理由
- **Vue 3**: 渐进式框架，Composition API 提供更好的逻辑复用
- **Element Plus**: Vue 3 优秀的 UI 组件库，组件丰富，中文文档友好
- **TypeScript**: 类型安全，提升开发效率
- **Vite**: 快速的开发服务器和构建工具
- **UnoCSS**: 原子化 CSS，高性能按需生成
- **Pinia**: Vue 3 官方推荐的状态管理库，轻量且类型友好

---

## 5. 数据库设计

### 5.1 ER 图

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│      tickets     │         │   ticket_tags    │         │      tags        │
├──────────────────┤         ├──────────────────┤         ├──────────────────┤
│ id (PK)         │◄────────│ ticket_id (FK)   │────────►│ id (PK)         │
│ title           │         │ tag_id (FK)      │         │ name (UNIQUE)   │
│ description     │         └──────────────────┘         │ color           │
│ is_completed    │                                    │ created_at      │
│ created_at      │                                    │ updated_at      │
│ updated_at      │                                    └──────────────────┘
└──────────────────┘
```

### 5.2 表结构设计

#### 5.2.1 tickets 表
```sql
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tickets_is_completed ON tickets(is_completed);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
```

#### 5.2.2 tags 表
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) NOT NULL,  -- Hex color, e.g., #FF5733
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
```

#### 5.2.3 ticket_tags 表（多对多关系）
```sql
CREATE TABLE ticket_tags (
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (ticket_id, tag_id)
);

CREATE INDEX idx_ticket_tags_ticket_id ON ticket_tags(ticket_id);
CREATE INDEX idx_ticket_tags_tag_id ON ticket_tags(tag_id);
```

### 5.3 数据完整性
- 删除标签时自动从 ticket_tags 中移除关联
- 删除 Ticket 时自动从 ticket_tags 中移除关联
- 标签名称唯一性约束
- 更新时间自动更新触发器

---

## 6. API 设计

### 6.1 API 规范
- **基础 URL**: `http://localhost:8000/api/v1`
- **数据格式**: JSON
- **认证**: 当前版本无需认证
- **错误响应**: 统一格式

```typescript
// 错误响应格式
{
  "detail": "错误信息描述"
}
```

### 6.2 Ticket API

#### 6.2.1 获取 Ticket 列表
```http
GET /api/v1/tickets
```

**Query 参数:**
- `search`: 搜索关键词（可选）
- `tag_ids`: 标签 ID 列表，逗号分隔（可选）
- `is_completed`: 完成状态（可选）
- `skip`: 跳过数量，默认 0
- `limit`: 返回数量，默认 100

**响应示例:**
```json
{
  "total": 150,
  "items": [
    {
      "id": 1,
      "title": "修复登录 Bug",
      "description": "用户无法正常登录",
      "is_completed": false,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "tags": [
        {
          "id": 1,
          "name": "Bug",
          "color": "#EF4444"
        },
        {
          "id": 2,
          "name": "高优先级",
          "color": "#F59E0B"
        }
      ]
    }
  ]
}
```

#### 6.2.2 创建 Ticket
```http
POST /api/v1/tickets
```

**请求体:**
```json
{
  "title": "修复登录 Bug",
  "description": "用户无法正常登录",
  "tag_ids": [1, 2]
}
```

**响应:** 返回创建的 Ticket 对象

#### 6.2.3 获取单个 Ticket
```http
GET /api/v1/tickets/{ticket_id}
```

**响应:** Ticket 对象

#### 6.2.4 更新 Ticket
```http
PUT /api/v1/tickets/{ticket_id}
```

**请求体:**
```json
{
  "title": "修复登录 Bug",
  "description": "更新后的描述",
  "tag_ids": [1, 2, 3],
  "is_completed": false
}
```

**响应:** 更新后的 Ticket 对象

#### 6.2.5 删除 Ticket
```http
DELETE /api/v1/tickets/{ticket_id}
```

**响应:**
```json
{
  "message": "Ticket deleted successfully"
}
```

#### 6.2.6 批量删除 Ticket
```http
DELETE /api/v1/tickets
```

**请求体:**
```json
{
  "ticket_ids": [1, 2, 3]
}
```

#### 6.2.7 切换完成状态
```http
PATCH /api/v1/tickets/{ticket_id}/toggle
```

**响应:** 更新后的 Ticket 对象

#### 6.2.8 批量完成/取消完成
```http
PATCH /api/v1/tickets/batch-complete
```

**请求体:**
```json
{
  "ticket_ids": [1, 2, 3],
  "is_completed": true
}
```

### 6.3 Tag API

#### 6.3.1 获取标签列表
```http
GET /api/v1/tags
```

**Query 参数:**
- `include_usage_count`: 是否包含使用次数（可选，默认 true）

**响应示例:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Bug",
      "color": "#EF4444",
      "usage_count": 15,
      "created_at": "2025-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "name": "功能请求",
      "color": "#3B82F6",
      "usage_count": 8,
      "created_at": "2025-01-15T10:05:00Z"
    }
  ]
}
```

#### 6.3.2 创建标签
```http
POST /api/v1/tags
```

**请求体:**
```json
{
  "name": "Bug",
  "color": "#EF4444"
}
```

**响应:** 创建的标签对象

#### 6.3.3 获取单个标签
```http
GET /api/v1/tags/{tag_id}
```

**响应:** 标签对象

#### 6.3.4 更新标签
```http
PUT /api/v1/tags/{tag_id}
```

**请求体:**
```json
{
  "name": "严重 Bug",
  "color": "#DC2626"
}
```

**响应:** 更新后的标签对象

#### 6.3.5 删除标签
```http
DELETE /api/v1/tags/{tag_id}
```

**响应:**
```json
{
  "message": "Tag deleted successfully"
}
```

---

## 7. 前端设计

### 7.1 页面布局

```
┌──────────────────────────────────────────────────────────┐
│                      Header                               │
│  Logo | 统计信息 | 搜索框                                 │
├──────────────────────────────────────────────────────────┤
│                          │                                │
│    Filter Sidebar         │      Ticket List              │
│                          │                                │
│  ┌─────────────────┐    │  ┌─────────────────────────┐  │
│  │ 标签筛选         │    │  │ Ticket Card 1           │  │
│  │ □ Bug (5)       │    │  │ Title                   │  │
│  │ □ 功能 (3)      │    │  │ Tags | Status           │  │
│  │ □ 优化 (2)      │    │  └─────────────────────────┘  │
│  │                 │    │                                │
│  │ 状态筛选         │    │  ┌─────────────────────────┐  │
│  │ ○ 全部          │    │  │ Ticket Card 2           │  │
│  │ ○ 未完成        │    │  │ Title                   │  │
│  │ ○ 已完成        │    │  │ Tags | Status           │  │
│  │                 │    │  └─────────────────────────┘  │
│  │ 管理标签按钮     │    │                                │
│  └─────────────────┘    │  ...                          │
│                          │                                │
│                          │  批量操作栏                     │
└──────────────────────────────────────────────────────────┘
```

### 7.2 核心组件设计

#### 7.2.1 TicketCard 组件
```typescript
// Props 定义
interface Props {
  ticket: Ticket
  onEdit: (ticket: Ticket) => void
  onDelete: (id: number) => void
  onToggle: (id: number) => void
  onSelect: (id: number) => void
  isSelected: boolean
}

// Vue 3 组件示例
<script setup lang="ts">
import { defineProps } from 'vue'

interface Props {
  ticket: Ticket
  onEdit: (ticket: Ticket) => void
  onDelete: (id: number) => void
  onToggle: (id: number) => void
  onSelect: (id: number) => void
  isSelected: boolean
}

defineProps<Props>()
</script>

// 功能:
// - 显示 Ticket 信息
// - 标签徽章展示
// - 完成/未完成视觉区分
// - 快捷操作按钮
// - 选择框（批量操作）
```

#### 7.2.2 TicketForm 组件
```typescript
interface Props {
  ticket?: Ticket
}

interface Emits {
  (e: 'submit', data: TicketFormData): void
  (e: 'cancel'): void
}

// 功能:
// - 标题输入（必填，200 字符限制）
// - 描述输入（可选，2000 字符限制）
// - 标签多选
// - 表单验证
// - 提交/取消按钮
```

#### 7.2.3 TagBadge 组件
```typescript
interface Props {
  tag: Tag
  onRemove?: (tagId: number) => void
  clickable?: boolean
}

interface Emits {
  (e: 'click', tag: Tag): void
}

// 功能:
// - 显示标签名称和颜色
// - 可移除（在表单中）
// - 可点击（筛选）
// - 悬停效果
```

#### 7.2.4 TagSelector 组件
```typescript
interface Props {
  selectedTags: Tag[]
  availableTags: Tag[]
  showCreateButton?: boolean
}

interface Emits {
  (e: 'update:selectedTags', tags: Tag[]): void
  (e: 'create-new', name: string): void
}

// 功能:
// - 多选下拉框
// - 搜索标签
// - 创建新标签
// - 已选标签展示
```

#### 7.2.5 SearchBar 组件
```typescript
interface Props {
  modelValue: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

// 功能:
// - 实时搜索
// - 防抖处理（300ms）
// - 清空按钮
// - 搜索历史记录（可选）
```

### 7.3 状态管理

使用 Pinia 进行状态管理：

```typescript
// stores/ticket.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTicketStore = defineStore('ticket', () => {
  // 状态
  const tickets = ref<Ticket[]>([])
  const tags = ref<Tag[]>([])
  const filters = ref<Filters>({
    search: '',
    tagIds: [],
    isCompleted: null,
    sortBy: 'created_at',
    sortOrder: 'desc'
  })
  const selectedTickets = ref<number[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const filteredTickets = computed(() => {
    // 筛选逻辑
  })

  const completedCount = computed(() =>
    tickets.value.filter(t => t.isCompleted).length
  )

  // Actions
  async function fetchTickets() {
    isLoading.value = true
    try {
      const response = await api.getTickets()
      tickets.value = response.items
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function createTicket(data: TicketFormData) {
    const response = await api.createTicket(data)
    tickets.value.unshift(response)
  }

  async function updateTicket(id: number, data: TicketFormData) {
    const response = await api.updateTicket(id, data)
    const index = tickets.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tickets.value[index] = response
    }
  }

  async function deleteTicket(id: number) {
    await api.deleteTicket(id)
    tickets.value = tickets.value.filter(t => t.id !== id)
  }

  async function toggleTicket(id: number) {
    const ticket = tickets.value.find(t => t.id === id)
    if (ticket) {
      const response = await api.toggleTicket(id)
      Object.assign(ticket, response)
    }
  }

  async function batchDelete(ids: number[]) {
    await api.batchDelete(ids)
    tickets.value = tickets.value.filter(t => !ids.includes(t.id))
  }

  async function batchComplete(ids: number[], isCompleted: boolean) {
    await api.batchComplete(ids, isCompleted)
    ids.forEach(id => {
      const ticket = tickets.value.find(t => t.id === id)
      if (ticket) ticket.isCompleted = isCompleted
    })
  }

  function setFilters(newFilters: Partial<Filters>) {
    Object.assign(filters.value, newFilters)
  }

  function setSelectedTickets(ids: number[]) {
    selectedTickets.value = ids
  }

  return {
    // 状态
    tickets,
    tags,
    filters,
    selectedTickets,
    isLoading,
    error,
    // Getters
    filteredTickets,
    completedCount,
    // Actions
    fetchTickets,
    fetchTags,
    createTicket,
    updateTicket,
    deleteTicket,
    toggleTicket,
    batchDelete,
    batchComplete,
    setFilters,
    setSelectedTickets
  }
})

interface Filters {
  search: string
  tagIds: number[]
  isCompleted: boolean | null
  sortBy: 'created_at' | 'updated_at' | 'title'
  sortOrder: 'asc' | 'desc'
}
```

### 7.4 样式系统

#### 7.4.1 设计令牌（Design Tokens）
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

#### 7.4.2 UnoCSS 配置
```typescript
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

### 7.5 响应式设计

#### 7.5.1 断点定义
```typescript
const breakpoints = {
  sm: '640px',   // 手机
  md: '768px',   // 平板
  lg: '1024px',  // 桌面
  xl: '1280px',  // 大屏幕
}
```

#### 7.5.2 布局适配
- **移动端（<768px）**: 单列布局，侧边栏折叠为下拉菜单
- **平板（768px-1023px）**: 侧边栏可折叠
- **桌面（≥1024px）**: 完整双列布局

---

## 8. 开发计划

### 8.1 第一阶段：基础框架（2-3 天）
- [ ] 项目初始化
  - [ ] 后端 FastAPI 项目搭建
  - [ ] 前端 Vite + Vue 3 项目搭建
  - [ ] Docker Compose 配置
  - [ ] 数据库初始化

- [ ] 数据库设计
  - [ ] 创建表结构
  - [ ] 编写 Alembic 迁移脚本
  - [ ] 准备测试数据

### 8.2 第二阶段：后端开发（3-4 天）
- [ ] 基础功能
  - [ ] Ticket CRUD API
  - [ ] Tag CRUD API
  - [ ] 多对多关系处理
  - [ ] 搜索和筛选功能

- [ ] 测试
  - [ ] 单元测试
  - [ ] API 集成测试
  - [ ] 测试覆盖率 > 80%

### 8.3 第三阶段：前端开发（4-5 天）
- [ ] 核心组件
  - [ ] TicketCard 组件
  - [ ] TicketForm 组件
  - [ ] TagBadge 组件
  - [ ] TagSelector 组件
  - [ ] SearchBar 组件

- [ ] 页面开发
  - [ ] 主页面布局
  - [ ] Ticket 列表页
  - [ ] 标签管理模态框
  - [ ] 批量操作功能

- [ ] 状态管理
  - [ ] Pinia Store 配置
  - [ ] API 服务封装
  - [ ] 错误处理

### 8.4 第四阶段：集成与优化（2-3 天）
- [ ] 功能集成
  - [ ] 前后端联调
  - [ ] 端到端测试

- [ ] 性能优化
  - [ ] 前端代码分割
  - [ ] API 响应优化
  - [ ] 数据库查询优化

- [ ] UI/UX 优化
  - [ ] 加载状态
  - [ ] 错误提示
  - [ ] 动画效果
  - [ ] 响应式适配

### 8.5 第五阶段：测试与部署（2-3 天）
- [ ] 测试
  - [ ] 功能测试
  - [ ] 兼容性测试
  - [ ] 性能测试

- [ ] 部署准备
  - [ ] Docker 镜像构建
  - [ ] 部署文档编写
  - [ ] 用户手册编写

**预计总工期**: 13-18 天

---

## 9. 测试策略

### 9.1 后端测试

#### 9.1.1 单元测试
- **测试工具**: pytest
- **覆盖范围**:
  - CRUD 操作逻辑
  - 数据验证
  - 业务逻辑函数
  - 工具函数

**示例:**
```python
def test_create_ticket(db_session):
    ticket = TicketCreate(title="Test Ticket")
    created = crud.create_ticket(db_session, ticket)
    assert created.id is not None
    assert created.title == "Test Ticket"
```

#### 9.1.2 API 集成测试
- **测试工具**: pytest + FastAPI TestClient
- **覆盖范围**:
  - 所有 API 端点
  - 请求验证
  - 响应格式
  - 错误处理

**示例:**
```python
def test_create_ticket_api(client):
    response = client.post(
        "/api/v1/tickets",
        json={"title": "Test Ticket"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Ticket"
```

#### 9.1.3 测试覆盖率
- **目标**: > 80%
- **工具**: pytest-cov

### 9.2 前端测试

#### 9.2.1 组件测试
- **测试工具**: Vitest + Vue Test Utils
- **覆盖范围**:
  - 组件渲染
  - 用户交互
  - Props 传递
  - 事件触发

**示例:**
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TicketCard from '@/components/tickets/TicketCard.vue'

describe('TicketCard', () => {
  it('renders ticket information', () => {
    const wrapper = mount(TicketCard, {
      props: {
        ticket: mockTicket,
        onEdit: vi.fn(),
        onDelete: vi.fn(),
        onToggle: vi.fn(),
        onSelect: vi.fn(),
        isSelected: false
      }
    })

    expect(wrapper.text()).toContain('Test Ticket')
  })

  it('emits toggle event when button clicked', async () => {
    const wrapper = mount(TicketCard, {
      props: {
        ticket: mockTicket,
        onToggle: vi.fn(),
        // ... other props
      }
    })

    await wrapper.find('.toggle-button').trigger('click')
    expect(wrapper.props('onToggle')).toHaveBeenCalledWith(1)
  })
})
```

#### 9.2.2 E2E 测试
- **测试工具**: Playwright
- **覆盖范围**:
  - 完整用户流程
  - 关键功能场景

**示例:**
```typescript
test('create a new ticket', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await page.click('button:has-text("New Ticket")')
  await page.fill('[name="title"]', 'Test Ticket')
  await page.click('button:has-text("Create")')
  await expect(page.locator('text=Test Ticket')).toBeVisible()
})
```

### 9.3 测试数据准备

#### 9.3.1 种子数据
```sql
-- 标签
INSERT INTO tags (name, color) VALUES
  ('Bug', '#EF4444'),
  ('功能请求', '#3B82F6'),
  ('优化', '#10B981'),
  ('文档', '#F59E0B'),
  ('紧急', '#DC2626');

-- Tickets
INSERT INTO tickets (title, description, is_completed) VALUES
  ('修复登录 Bug', '用户无法正常登录系统', false),
  ('添加搜索功能', '实现标题和描述搜索', false),
  ('优化性能', '减少页面加载时间', true);
```

---

## 10. 部署方案

### 10.1 开发环境

#### 10.1.1 Docker Compose 配置
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ticketdb
      POSTGRES_USER: ticketuser
      POSTGRES_PASSWORD: ticketpass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://ticketuser:ticketpass@postgres:5432/ticketdb
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

#### 10.1.2 启动命令
```bash
# 克隆项目
git clone <repo-url>
cd ticket-manager

# 启动所有服务
docker-compose up -d

# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 访问应用
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
```

### 10.2 生产环境

#### 10.2.1 推荐配置
- **服务器**: 2 Core CPU, 4GB RAM
- **数据库**: PostgreSQL 15（独立服务器或托管服务）
- **反向代理**: Nginx
- **进程管理**: Systemd 或 Docker Swarm

#### 10.2.2 Nginx 配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/ticket-manager/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 10.2.3 环境变量
```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/ticketdb
CORS_ORIGINS=["https://your-domain.com"]
LOG_LEVEL=info
```

---

## 11. 项目交付物

### 11.1 代码交付
- [ ] 完整的后端代码（包含注释和类型定义）
- [ ] 完整的前端代码（包含注释和类型定义）
- [ ] 数据库迁移脚本
- [ ] Docker 配置文件
- [ ] 测试代码（覆盖率 > 80%）

### 11.2 文档交付
- [ ] API 文档（自动生成）
- [ ] 部署文档
- [ ] 用户手册
- [ ] 开发文档
- [ ] README.md

### 11.3 测试交付
- [ ] 单元测试报告
- [ ] 集成测试报告
- [ ] E2E 测试报告
- [ ] 测试覆盖率报告

---

## 12. 后续扩展方向

### 12.1 功能扩展
- [ ] 用户系统和权限管理
- [ ] Ticket 优先级
- [ ] Ticket 截止日期
- [ ] Ticket 评论系统
- [ ] 文件附件功能
- [ ] Ticket 模板
- [ ] 导入/导出功能（CSV, JSON）
- [ ] 回收站功能

### 12.2 技术优化
- [ ] 实时更新（WebSocket）
- [ ] 离线支持（PWA）
- [ ] 移动端 App（Vue + Capacitor 或 UniApp）
- [ ] 数据分析仪表板
- [ ] 全文搜索（Elasticsearch）
- [ ] 缓存优化（Redis）

---

## 13. 附录

### 13.1 依赖版本

#### 后端
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.5.3
pytest==7.4.4
pytest-cov==4.1.0
```

#### 前端
```json
{
  "vue": "^3.4.15",
  "vue-router": "^4.2.5",
  "pinia": "^2.1.7",
  "element-plus": "^2.5.2",
  "@element-plus/icons-vue": "^2.3.1",
  "typescript": "^5.3.3",
  "vite": "^5.0.11",
  "unocss": "^0.58.0",
  "axios": "^1.6.5",
  "@vueuse/core": "^10.7.2"
}
```

### 13.2 参考资料
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Vue 3 文档](https://cn.vuejs.org/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [UnoCSS 文档](https://unocss.dev/)
- [Pinia 文档](https://pinia.vuejs.org/zh/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

---

**文档版本**: v1.0
**创建日期**: 2025-01-15
**最后更新**: 2025-01-15
**作者**: AI Assistant
