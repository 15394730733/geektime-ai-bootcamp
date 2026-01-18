# Design Document: Database Selector Fix

## Problem Analysis

根据代码分析和用户反馈，数据库选择器存在以下问题：

1. **状态更新问题**: `selectDatabase` 是异步函数，但 `onChange` 处理可能不等待完成
2. **元数据加载时机**: 当数据库切换时，元数据清空和重新加载的时机可能有问题
3. **UI 反馈缺失**: 切换数据库时没有明确的加载状态或成功提示

## Root Cause

在 `AppStateContext.tsx` 中：

```typescript
const selectDatabase = async (databaseName: string | null) => {
  dispatch({ type: 'SET_SELECTED_DATABASE', payload: databaseName });
};
```

这个函数虽然是 async，但实际上是同步执行的 dispatch。问题在于：

1. Reducer 中清空 metadata 的逻辑：
```typescript
metadata: action.payload === state.selectedDatabase ? state.metadata : null,
```
这个条件判断有问题 - 当切换到新数据库时，`action.payload !== state.selectedDatabase`，所以会清空 metadata，但这是正确的。

2. 在 `useEffect` 中加载 metadata：
```typescript
useEffect(() => {
  if (state.selectedDatabase) {
    loadMetadata(state.selectedDatabase);
  }
}, [state.selectedDatabase]);
```

这个逻辑看起来是对的，但可能存在竞态条件。

## Solution Design

### 方案 1: 改进状态管理（推荐）

1. **添加数据库切换状态**
   - 在 state 中添加 `switchingDatabase` 标志
   - 在切换过程中显示加载状态

2. **改进 selectDatabase 函数**
   - 添加切换开始和结束的状态更新
   - 添加成功/失败的用户反馈

3. **改进 Select 组件**
   - 在切换过程中禁用 Select
   - 显示加载状态

### 方案 2: 简化状态管理

1. **移除 async 关键字**
   - `selectDatabase` 不需要是 async，因为它只是 dispatch
   - 元数据加载由 useEffect 处理

2. **添加调试日志**
   - 在关键位置添加 console.log
   - 帮助诊断问题

## Implementation Plan

### Step 1: 修复 AppStateContext

```typescript
// 添加新的 action type
type AppAction =
  | { type: 'START_DATABASE_SWITCH' }
  | { type: 'COMPLETE_DATABASE_SWITCH' }
  | ...existing actions

// 更新 state interface
interface AppState {
  ...existing fields
  switchingDatabase: boolean;
}

// 更新 reducer
case 'START_DATABASE_SWITCH':
  return {
    ...state,
    switchingDatabase: true,
  };
case 'COMPLETE_DATABASE_SWITCH':
  return {
    ...state,
    switchingDatabase: false,
  };

// 改进 selectDatabase
const selectDatabase = async (databaseName: string | null) => {
  console.log('Selecting database:', databaseName);
  dispatch({ type: 'START_DATABASE_SWITCH' });
  dispatch({ type: 'SET_SELECTED_DATABASE', payload: databaseName });
  
  // Wait for metadata to load
  if (databaseName) {
    try {
      await loadMetadata(databaseName);
      message.success(`Switched to database: ${databaseName}`);
    } catch (error) {
      // Error already handled in loadMetadata
    }
  }
  
  dispatch({ type: 'COMPLETE_DATABASE_SWITCH' });
};
```

### Step 2: 更新 Query 页面

```typescript
<Select
  style={{ minWidth: 250 }}
  placeholder="Choose a database"
  value={state.selectedDatabase || undefined}
  onChange={actions.selectDatabase}
  loading={state.loading.databases || state.switchingDatabase}
  disabled={state.switchingDatabase}
>
  {activeDatabases.map(db => (
    <Select.Option key={db.name} value={db.name}>
      {db.name}
      {db.description && ` - ${db.description}`}
    </Select.Option>
  ))}
</Select>
```

### Step 3: 添加调试日志

在关键位置添加 console.log：
- selectDatabase 调用时
- reducer 处理 SET_SELECTED_DATABASE 时
- useEffect 触发 loadMetadata 时
- loadMetadata 完成时

## Testing Strategy

1. **手动测试**
   - 打开 Query 页面
   - 从下拉列表选择不同的数据库
   - 验证：
     - Select 显示正确的数据库名称
     - 元数据面板更新为新数据库的 schema
     - 有明确的加载状态和成功提示

2. **边界情况**
   - 快速连续切换数据库
   - 在元数据加载过程中切换数据库
   - 切换到没有元数据的数据库

## Rollback Plan

如果修复导致新问题：
1. 恢复 AppStateContext.tsx 到原始版本
2. 恢复 Query.tsx 到原始版本
3. 使用 git 回滚更改

## Success Criteria

- [ ] 点击数据库选项后，Select 立即显示选中的数据库
- [ ] 元数据面板显示正确数据库的 schema
- [ ] 有明确的加载状态指示
- [ ] 有成功切换的提示消息
- [ ] 快速切换数据库不会导致竞态条件
- [ ] 控制台没有错误日志
