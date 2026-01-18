# Database Selector Debug Guide

## 调试工具已添加

我已经添加了详细的调试日志和一个可视化调试面板来帮助诊断问题。

## 如何使用

### 1. 重新启动前端开发服务器

确保前端重新编译了最新的代码：

```bash
cd w2/sth-db-query/frontend
npm run dev
```

或者如果已经在运行，按 `Ctrl+C` 停止，然后重新启动。

### 2. 打开浏览器开发者工具

1. 打开应用程序
2. 按 `F12` 打开开发者工具
3. 切换到 **Console** 标签

### 3. 导航到 Query 页面

你会在右下角看到一个 **Debug Info** 面板，显示：
- Selected Database（当前选中的数据库）
- Switching（是否正在切换）
- Databases Count（可用数据库数量）
- Metadata（元数据是否已加载）
- Loading Metadata（是否正在加载元数据）
- Available DBs（可用数据库列表）

### 4. 测试数据库选择

点击数据库选择器，选择一个不同的数据库。

### 5. 观察控制台输出

你应该看到类似这样的日志：

```
Select onChange triggered with value: test
=== selectDatabase called ===
New database: test
Current database: test2
Are they equal? false
Dispatching START_DATABASE_SWITCH
Dispatching SET_SELECTED_DATABASE with: test
Reducer: SET_SELECTED_DATABASE {oldValue: 'test2', newValue: 'test', willClearMetadata: true}
=== DatabaseSelectorDebug: State Changed ===
selectedDatabase: test
switchingDatabase: true
databases count: 2
metadata: null
loading.metadata: false
Loading metadata for database: test
Dispatching COMPLETE_DATABASE_SWITCH
=== DatabaseSelectorDebug: State Changed ===
selectedDatabase: test
switchingDatabase: false
databases count: 2
metadata: null
loading.metadata: true
Metadata loaded successfully: {...}
=== DatabaseSelectorDebug: State Changed ===
selectedDatabase: test
switchingDatabase: false
databases count: 2
metadata: loaded
loading.metadata: false
```

## 诊断问题

### 问题 1: onChange 没有触发

**症状**: 点击数据库选项后，控制台没有 "Select onChange triggered" 日志

**可能原因**:
- Select 组件被禁用
- 事件被其他组件拦截
- React 没有重新渲染

**检查**:
- Debug 面板中 "Switching" 是否为 true（如果是，Select 被禁用了）
- 检查浏览器元素检查器，Select 是否有 `disabled` 属性

### 问题 2: selectDatabase 没有被调用

**症状**: 有 "Select onChange triggered" 但没有 "=== selectDatabase called ==="

**可能原因**:
- actions.selectDatabase 引用错误
- Context 没有正确提供

**检查**:
- 在 Console 中输入: `window.location.reload()` 强制刷新
- 检查是否有 React 错误

### 问题 3: State 没有更新

**症状**: 有所有日志，但 Debug 面板中 "Selected Database" 没有变化

**可能原因**:
- Reducer 没有正确返回新状态
- React 状态更新被批处理延迟

**检查**:
- 观察 "Reducer: SET_SELECTED_DATABASE" 日志中的 oldValue 和 newValue
- 检查 Debug 面板是否最终更新（可能有延迟）

### 问题 4: Select 显示值没有更新

**症状**: State 更新了（Debug 面板显示正确），但 Select 下拉框显示的还是旧值

**可能原因**:
- Select 的 value 属性绑定问题
- Ant Design Select 组件的受控模式问题

**解决方案**:
尝试添加 `key` 属性强制重新渲染：

```typescript
<Select
  key={state.selectedDatabase}  // 添加这行
  value={state.selectedDatabase || undefined}
  ...
>
```

### 问题 5: 元数据没有加载

**症状**: Database 切换成功，但元数据面板没有更新

**可能原因**:
- useEffect 依赖没有触发
- API 调用失败

**检查**:
- 查看 "Loading metadata for database" 日志
- 查看是否有 "Metadata loaded successfully" 或错误日志
- 检查 Network 标签，看是否有 API 请求

## 常见解决方案

### 解决方案 1: 强制刷新

```bash
# 清除浏览器缓存
Ctrl + Shift + Delete

# 或者硬刷新
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### 解决方案 2: 重新安装依赖

```bash
cd w2/sth-db-query/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 解决方案 3: 检查 Ant Design 版本

```bash
cd w2/sth-db-query/frontend
npm list antd
```

确保使用的是兼容版本（建议 5.x）。

### 解决方案 4: 添加 key 属性

如果 Select 值不更新，在 Query.tsx 中修改：

```typescript
<Select
  key={`db-select-${state.selectedDatabase}`}
  value={state.selectedDatabase || undefined}
  onChange={(value) => {
    console.log('Select onChange triggered with value:', value);
    actions.selectDatabase(value);
  }}
  ...
>
```

## 收集信息

如果问题仍然存在，请提供以下信息：

1. **完整的控制台日志**（从点击到结束的所有日志）
2. **Debug 面板的截图**（点击前和点击后）
3. **Network 标签的截图**（显示 API 请求）
4. **具体的症状描述**：
   - Select 下拉框显示什么？
   - 点击后有什么变化？
   - 元数据面板显示什么？

## 移除调试工具

问题解决后，移除调试组件：

1. 从 Query.tsx 中删除 `<DatabaseSelectorDebug />` 行
2. 删除 `w2/sth-db-query/frontend/src/components/DatabaseSelectorDebug.tsx` 文件
3. 可以保留 console.log（或者也删除它们）
