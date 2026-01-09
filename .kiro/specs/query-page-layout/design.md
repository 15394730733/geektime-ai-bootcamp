# Design Document: Query Page Layout

## Overview

重构数据库查询工具的前端布局，实现专业级的左右分栏界面。基于现有的 React + Ant Design + Tailwind CSS 技术栈，使用 `react-resizable-panels` 库实现可拖拽的分割面板。

### 目标布局

```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Database Selector                                       │
├──────────────┬──────────────────────────────────────────────────┤
│              │  Tab Bar: [Query 1] [Query 2] [+]                 │
│  Metadata    ├──────────────────────────────────────────────────┤
│  Panel       │                                                   │
│              │  Query Editor (Monaco)                            │
│  - Search    │                                                   │
│  - Schema    │  [Execute] [Format] [Clear]                       │
│    Tree      ├──────────────────────────────────────────────────┤
│              │                                                   │
│  280px       │  Results Table                                    │
│  (resizable) │                                                   │
│              │  [Export CSV] [Export JSON]    Page: 1/10         │
└──────────────┴──────────────────────────────────────────────────┘
```

## Architecture

### 技术选型

- **分割面板**: `react-resizable-panels` - 轻量级、高性能的可拖拽分割面板库
- **UI 组件**: Ant Design 5.x - 保持与现有代码一致
- **样式**: Tailwind CSS - 快速布局和响应式设计
- **状态管理**: React Context + useState - 复用现有的 AppStateContext
- **编辑器**: Monaco Editor - 已有实现

### 组件层次结构

```
QueryPage
├── DatabaseSelector (header)
├── PanelGroup (horizontal split)
│   ├── Panel (left - metadata)
│   │   └── MetadataPanel
│   │       ├── SearchInput
│   │       └── SchemaTree
│   ├── PanelResizeHandle
│   └── Panel (right - query)
│       └── QueryPanel
│           ├── TabBar
│           ├── PanelGroup (vertical split)
│           │   ├── Panel (top - editor)
│           │   │   └── QueryEditor
│           │   ├── PanelResizeHandle
│           │   └── Panel (bottom - results)
│           │       └── QueryResults
```

## Components and Interfaces

### 1. QueryPage (重构)

主页面组件，管理整体布局和状态。

```typescript
interface QueryPageProps {}

interface QueryTab {
  id: string;
  name: string;
  query: string;
  results: QueryResult | null;
  isDirty: boolean;
}

interface QueryPageState {
  tabs: QueryTab[];
  activeTabId: string;
  horizontalSplitSize: number; // percentage
  verticalSplitSize: number;   // percentage
}
```

### 2. MetadataPanel (新组件)

左侧元数据面板，包含搜索和树形结构。

```typescript
interface MetadataPanelProps {
  databaseName: string | null;
  metadata: DatabaseMetadata | null;
  loading: boolean;
  onTableClick: (schema: string, tableName: string) => void;
  onColumnClick: (schema: string, tableName: string, columnName: string) => void;
}
```

### 3. SchemaTree (重构 MetadataViewer)

数据库结构树形组件。

```typescript
interface SchemaTreeProps {
  metadata: DatabaseMetadata | null;
  searchQuery: string;
  onTableSelect: (schema: string, tableName: string) => void;
  onColumnSelect: (schema: string, tableName: string, columnName: string) => void;
}
```

### 4. QueryPanel (新组件)

右侧查询面板，包含标签页、编辑器和结果。

```typescript
interface QueryPanelProps {
  tabs: QueryTab[];
  activeTabId: string;
  databaseName: string | null;
  onTabChange: (tabId: string) => void;
  onTabCreate: () => void;
  onTabClose: (tabId: string) => void;
  onQueryChange: (tabId: string, query: string) => void;
  onExecute: (tabId: string) => void;
}
```

### 5. TabBar (新组件)

查询标签栏组件。

```typescript
interface TabBarProps {
  tabs: QueryTab[];
  activeTabId: string;
  databaseName: string | null;
  onTabChange: (tabId: string) => void;
  onTabCreate: () => void;
  onTabClose: (tabId: string) => void;
}
```

## Data Models

### QueryTab

```typescript
interface QueryTab {
  id: string;           // UUID
  name: string;         // "Query HH:MM:SS"
  query: string;        // SQL content
  results: QueryResult | null;
  isDirty: boolean;     // Has unsaved changes
  createdAt: Date;
}
```

### LayoutPreferences (localStorage)

```typescript
interface LayoutPreferences {
  horizontalSplitSize: number;  // 0-100, default 20
  verticalSplitSize: number;    // 0-100, default 50
  metadataPanelCollapsed: boolean;
}

const LAYOUT_STORAGE_KEY = 'db-query-layout-preferences';
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Layout Persistence Round-Trip

*For any* layout configuration (horizontal split size, vertical split size), saving to localStorage and then reloading the page SHALL restore the exact same layout configuration.

**Validates: Requirements 1.5, 5.3**

### Property 2: Panel Resize Constraints

*For any* drag operation on the horizontal splitter, the left panel width SHALL remain between the minimum (200px) and maximum (50% of viewport) constraints.

**Validates: Requirements 1.4, 6.3**

### Property 3: Schema Tree Hierarchy Rendering

*For any* valid DatabaseMetadata object, the SchemaTree SHALL render all schemas, tables, views, and columns in the correct hierarchical structure with appropriate icons.

**Validates: Requirements 2.1, 2.3, 2.4**

### Property 4: Click-to-Insert Behavior

*For any* table or column in the SchemaTree, clicking on it SHALL insert the correctly formatted identifier (schema.table or column_name) at the cursor position in the active QueryEditor.

**Validates: Requirements 2.5, 2.6**

### Property 5: Search Filter Accuracy

*For any* search query string and metadata set, the filtered SchemaTree SHALL display only items whose names contain the search query (case-insensitive), including parent nodes necessary to show the hierarchy.

**Validates: Requirements 2.7**

### Property 6: Tab Independence

*For any* set of query tabs, each tab SHALL maintain its own independent query content and results, and switching tabs SHALL preserve the state of all tabs.

**Validates: Requirements 3.1**

### Property 7: Results Display Completeness

*For any* QueryResult object, the ResultsTable SHALL display the correct row count, execution time, all columns with headers, and all rows with proper pagination.

**Validates: Requirements 4.1, 4.2, 4.6**

## Navigation Flow

### 移除侧边栏导航

当前应用使用 Refine 的 `ThemedLayoutV2` 和 `ThemedSiderV2` 创建了左侧导航栏。需要移除这个导航，改为直接的页面流程：

1. **移除 ThemedLayoutV2 包装器**
   - 不使用 Refine 的布局组件
   - 直接渲染页面内容

2. **数据库列表页面改进**
   - 点击数据库卡片直接跳转到 `/query?db={databaseName}`
   - 自动选择该数据库并加载元数据

3. **查询页面头部**
   - 添加返回数据库列表的按钮
   - 显示当前数据库名称
   - 保持数据库选择器用于切换

### 路由结构

```typescript
<Routes>
  <Route path="/" element={<DatabaseListPage />} />
  <Route path="/databases" element={<DatabaseListPage />} />
  <Route path="/query" element={<QueryPage />} />
  <Route path="*" element={<ErrorComponent />} />
</Routes>
```

## Error Handling

### 布局错误

- **localStorage 不可用**: 使用默认布局值，不持久化
- **无效的存储数据**: 重置为默认值
- **面板尺寸超出范围**: 自动调整到有效范围

### 数据加载错误

- **元数据加载失败**: 显示错误提示，允许重试
- **查询执行失败**: 在结果区域显示错误信息

### 响应式处理

- **小屏幕 (<768px)**: 自动折叠左侧面板为抽屉
- **面板过窄**: 强制最小宽度

## Testing Strategy

### 单元测试

使用 Vitest + React Testing Library：

1. **组件渲染测试**
   - MetadataPanel 正确渲染搜索框和树
   - TabBar 正确渲染标签页
   - QueryPanel 正确渲染编辑器和结果

2. **交互测试**
   - 点击表名/列名触发正确的回调
   - 标签页切换保持状态
   - 搜索过滤正确工作

3. **边界条件测试**
   - 空元数据处理
   - 单个标签页不可关闭
   - 最小/最大面板尺寸

### 属性测试

使用 fast-check 进行属性测试：

1. **Property 1**: 生成随机布局配置，验证 localStorage 往返一致性
2. **Property 3**: 生成随机元数据结构，验证树形渲染完整性
3. **Property 5**: 生成随机搜索词和元数据，验证过滤准确性
4. **Property 6**: 生成随机标签操作序列，验证状态独立性

### 集成测试

1. 完整的查询流程测试
2. 响应式布局测试
3. 键盘快捷键测试
