# Quick Test Instructions

## 立即测试步骤

### 1. 确保前端正在运行并已重新编译

```bash
# 如果前端正在运行，停止它 (Ctrl+C)
# 然后重新启动
cd w2/sth-db-query/frontend
npm run dev
```

等待看到类似这样的输出：
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 2. 打开浏览器

1. 打开 http://localhost:5173
2. 按 F12 打开开发者工具
3. 切换到 Console 标签
4. 清空控制台（点击 🚫 图标）

### 3. 导航到 Query 页面

- 点击 "Query Tool" 或直接访问 http://localhost:5173/query

### 4. 你应该看到

**在页面右下角**：
- 一个白色的 "Debug Info" 卡片，显示当前状态

**在控制台**：
- 当页面加载时，应该有一些初始化日志

### 5. 测试数据库选择

1. 点击 "Current Database:" 旁边的下拉框
2. 选择一个数据库（例如从 "test2" 切换到 "test"）
3. **立即查看控制台**

### 6. 预期的控制台输出

你应该看到这样的日志序列：

```
=== Select onChange triggered ===
Value: test
Type: string
Current state.selectedDatabase: test2
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
...
```

### 7. 预期的 UI 变化

**Debug Info 面板应该显示**：
- Selected Database: `test` (新的数据库名)
- Switching: `true` → 然后变成 `false`
- Metadata: `null` → `loaded`

**Select 下拉框应该显示**：
- 新选择的数据库名称（例如 "test - 测试数据库, 编辑一下"）

**元数据面板（左侧）应该**：
- 显示新数据库的表和列

## 如果没有看到预期输出

### 情况 A: 没有任何控制台日志

**问题**: 代码没有重新编译

**解决**:
1. 停止前端服务器 (Ctrl+C)
2. 删除 `.vite` 缓存：
   ```bash
   cd w2/sth-db-query/frontend
   rm -rf node_modules/.vite
   ```
3. 重新启动：
   ```bash
   npm run dev
   ```
4. 硬刷新浏览器 (Ctrl+Shift+R)

### 情况 B: 看到 "Select onChange triggered" 但没有后续日志

**问题**: `actions.selectDatabase` 可能是 undefined 或错误

**检查**:
在浏览器控制台输入：
```javascript
// 检查 context 是否正常
console.log('Testing context...');
```

然后尝试手动调用（在控制台）：
```javascript
// 这会失败，但能看到错误信息
actions.selectDatabase('test')
```

### 情况 C: 有所有日志，但 Select 显示值没变

**问题**: Ant Design Select 的受控组件问题

**已修复**: 我已经添加了 `key` 属性来强制重新渲染

**如果还是不行**，尝试在控制台输入：
```javascript
// 检查 state
console.log(document.querySelector('[class*="ant-select"]'));
```

### 情况 D: Debug Info 面板没有出现

**问题**: 组件导入失败或 React 错误

**检查**:
1. 查看控制台是否有 React 错误（红色文字）
2. 检查 Network 标签是否有 404 错误
3. 确认文件存在：
   ```bash
   ls w2/sth-db-query/frontend/src/components/DatabaseSelectorDebug.tsx
   ```

## 收集诊断信息

如果问题仍然存在，请提供：

1. **完整的控制台输出**（复制所有文字）
2. **截图**：
   - 整个页面（包括 Debug Info 面板）
   - 点击下拉框时的状态
   - 选择数据库后的状态
3. **浏览器信息**：
   - 浏览器名称和版本
   - 操作系统
4. **前端启动日志**：
   - npm run dev 的输出

## 下一步

根据你看到的情况，我们可以：
- 如果有日志但 UI 不更新 → 修复 Select 组件
- 如果没有日志 → 检查编译和导入
- 如果有错误 → 修复具体错误

请告诉我你看到了什么！
