# Query Results Export Feature Specification

**Feature**: Export Query Results to CSV/JSON
**Date**: 2026-01-18
**Status**: Design
**Related Feature**: Database Query Tool (001-db-query-tool)

## Overview

增强数据库查询工具的结果导出功能,允许用户通过界面按钮手动导出查询结果,以及在查询执行时自动导出为CSV或JSON格式文件到本地。

## User Stories

### User Story 1 - Manual Export (Priority: P1)

用户可以通过点击QueryResults组件中的CSV或JSON按钮,将当前查询结果导出为对应格式的文件。

**Why this priority**: 基础功能,按钮已存在但功能未实现。

**Current Status**: UI按钮已存在(QueryResults.tsx:200-215),导出函数已实现(handleExportCSV, handleExportJSON),但需要验证功能完整性。

**Acceptance Scenarios**:

1. **Given** 查询返回了1000行结果,**When** 用户点击CSV按钮,**Then** 浏览器下载包含所有结果的CSV文件
2. **Given** 查询返回了包含特殊字符(逗号、引号、换行符)的数据,**When** 用户导出为CSV,**Then** 特殊字符被正确转义,文件可用Excel打开
3. **Given** 查询结果包含null值,**When** 用户导出为CSV或JSON,**Then** null值被正确处理(CSV中为空,JSON中为null)
4. **Given** 查询结果包含日期时间类型,**When** 用户导出为JSON,**Then** 日期时间以ISO 8601格式保存

**Implementation Notes**:
- 导出功能已在 QueryResults.tsx 中实现
- convertToCSV函数处理CSV格式转换
- convertToJSON函数处理JSON格式转换
- downloadFile函数触发浏览器下载
- 文件名包含时间戳: `query-results-{timestamp}.csv` 或 `.json`

---

### User Story 2 - Auto Export Configuration (Priority: P2)

用户可以在执行SQL查询前,通过勾选checkbox选择是否自动导出结果为CSV和/或JSON格式。

**Why this priority**: 提升用户体验,避免每次手动导出的重复操作。

**Independent Test**: 可以独立测试checkbox状态管理和自动导出触发逻辑。

**Acceptance Scenarios**:

1. **Given** 用户打开查询页面,**When** 页面加载,**Then** CSV和JSON checkbox默认被选中
2. **Given** 用户只勾选了CSV checkbox,**When** 执行查询,**Then** 结果显示在页面上并自动下载CSV文件
3. **Given** 用户同时勾选CSV和JSON checkbox,**When** 执行查询,**Then** 结果显示并自动下载两个文件(CSV和JSON)
4. **Given** 用户取消勾选所有checkbox,**When** 执行查询,**Then** 结果仅显示在页面上,不自动下载文件
5. **Given** 用户选择了自动导出,**When** 查询执行失败或无结果,**Then** 不触发自动下载,不显示错误提示

**UI Design**:

```
┌─────────────────────────────────────────────────────────────┐
│ Query Panel                                                  │
├─────────────────────────────────────────────────────────────┤
│ ☑ CSV  ☑ JSON  [▶ Execute (Ctrl+Enter)]                    │
│                                                              │
│ [SQL Editor Area]                                           │
└─────────────────────────────────────────────────────────────┘
```

**Component Changes**:
- **QueryEditor.tsx**: 添加checkbox控件和状态管理
- **QueryPanel.tsx**: 传递auto-export配置给QueryResults
- **QueryResults.tsx**: 接收auto-export配置,在结果返回时触发自动导出

---

## Functional Requirements

### Manual Export (US1)

- **FR-E001**: System MUST export query results to CSV format when CSV button is clicked
- **FR-E002**: System MUST export query results to JSON format when JSON button is clicked
- **FR-E003**: CSV export MUST properly escape commas, quotes, and newlines
- **FR-E004**: Export files MUST include timestamp in filename
- **FR-E005**: Export MUST preserve column order from query results
- **FR-E006**: NULL values MUST be handled correctly (empty in CSV, null in JSON)
- **FR-E007**: Export buttons MUST be disabled when no results available

### Auto Export (US2)

- **FR-E008**: System MUST provide checkboxes for CSV and JSON auto-export configuration
- **FR-E009**: CSV and JSON checkboxes MUST be checked by default on page load
- **FR-E010**: System MUST auto-export results in selected format(s) after successful query execution
- **FR-E011**: Auto-export MUST NOT download files when query returns no results
- **FR-E012**: Auto-export MUST NOT download files when query execution fails
- **FR-E013**: Checkbox state MUST persist during session (not across page reloads)
- **FR-E014**: Auto-export files MUST use same format as manual export (same filename pattern)

---

## Technical Implementation Plan

### Phase 1: Verify Manual Export (US1)

**Files to Verify/Modify**:
1. `frontend/src/components/QueryResults.tsx`
   - 验证 convertToCSV 函数正确处理所有数据类型
   - 验证 convertToJSON 函数正确处理所有数据类型
   - 验证特殊字符转义逻辑
   - 验证 null 值处理
   - 测试手动导出按钮功能

**Test Cases**:
- 导出包含1000行数据的结果集
- 导出包含特殊字符的数据 (逗号, 引号, 换行符)
- 导出包含 null/undefined 值的数据
- 导出包含各种数据类型 (int, float, string, boolean, date)
- 验证CSV文件可用Excel/Google Sheets打开
- 验证JSON文件格式正确,可被解析

### Phase 2: Implement Auto Export (US2)

**New Features**:
1. **UI Changes**:
   - 在 QueryEditor.tsx 工具栏添加两个 Checkbox
   - Checkbox 位置: Execute 按钮左侧
   - Checkbox 标签: "CSV" 和 "JSON"
   - 默认状态: 两个都选中

2. **State Management**:
   ```typescript
   interface QueryEditorProps {
     // ... existing props
     autoExportCSV?: boolean;
     autoExportJSON?: boolean;
     onAutoExportChange?: (csv: boolean, json: boolean) => void;
   }
   ```

3. **Auto Export Logic**:
   - 在 QueryResults.tsx 添加 useEffect 监听结果变化
   - 当 rows 从空变为有数据时,检查 auto-export 配置
   - 根据配置触发对应的导出函数
   - 使用 useRef 避免重复导出

**Files to Modify**:
1. `frontend/src/components/QueryEditor.tsx`
   - 添加 Checkbox 组件导入
   - 添加 state: `autoExportCSV` 和 `autoExportJSON`
   - 添加回调: `onAutoExportChange`
   - 在工具栏渲染 Checkbox 控件

2. `frontend/src/components/QueryResults.tsx`
   - 添加 props: `autoExportCSV` 和 `autoExportJSON`
   - 添加 `useRef` 跟踪上次导出的结果集
   - 添加 `useEffect` 监听 rows 变化
   - 实现 auto-export 逻辑

3. `frontend/src/pages/Query.tsx` 或 `QueryPanel.tsx`
   - 管理 auto-export state
   - 传递 state 给 QueryEditor 和 QueryResults

---

## Data Format Specifications

### CSV Format

```csv
column1,column2,column3
value1,value2,value3
value"with"quotes,"value,with,commas",value3
,"",value3
```

**Rules**:
- 第一行: 列名
- 数据行: 每行一个记录
- 字段分隔: 逗号 (`,`)
- 引号包裹: 如果字段包含逗号、引号或换行符
- 引号转义: 双引号 (`""`)
- NULL值: 空字段
- 行分隔: `\n`

### JSON Format

```json
[
  {
    "column1": "value1",
    "column2": "value2",
    "column3": "value3"
  },
  {
    "column1": "value\"with\"quotes",
    "column2": "value,with,commas",
    "column3": null
  }
]
```

**Rules**:
- 数组格式: 对象数组
- 每个对象: 一行数据
- 键名: 列名
- 值类型: 保持原始类型 (string, number, boolean, null)
- NULL值: JSON `null`
- 日期时间: ISO 8601 字符串格式

---

## File Naming Convention

**Pattern**: `query-results-{timestamp}.{extension}`

**Timestamp Format**: ISO 8601 with `:` and `.` replaced by `-`

**Examples**:
- `query-results-2026-01-18T14-30-45-123Z.csv`
- `query-results-2026-01-18T14-30-45-123Z.json`

**Rationale**:
- 包含完整时间信息避免文件名冲突
- 替换特殊字符确保文件名在所有OS上有效
- 清晰的命名方便用户识别文件

---

## Edge Cases & Error Handling

### Edge Cases

1. **Empty Result Set**
   - Manual export: 按钮应该禁用或显示提示
   - Auto export: 不触发下载

2. **Large Result Sets** (> 1000 rows)
   - 当前已有限制: LIMIT 1000
   - 导出功能正常工作
   - 考虑未来: 添加进度提示

3. **Special Characters**
   - CSV: 正确转义逗号、引号、换行符
   - JSON: JSON.stringify 自动处理

4. **NULL Values**
   - CSV: 空字段
   - JSON: null

5. **Data Type Preservation**
   - 数字: 保持为数字类型(JSON)
   - 布尔值: true/false
   - 日期时间: ISO 8601字符串

6. **Browser Compatibility**
   - 使用 Blob API
   - 降级方案: 数据URI (如果需要)

7. **Concurrent Exports**
   - 用户快速连续点击导出按钮
   - 文件名时间戳确保唯一性

### Error Handling

1. **Export Failure**
   - 显示错误消息: "Failed to export CSV/JSON file"
   - 记录错误到控制台
   - 不中断用户操作

2. **Browser Restriction**
   - 某些浏览器可能限制自动下载
   - 显示提示: "Please allow downloads for this site"

3. **Memory Limit**
   - 大数据集可能导致内存问题
   - 当前已有限制(LIMIT 1000),风险较低

---

## Success Criteria

### Measurable Outcomes

- **SC-E001**: Manual CSV export works correctly for all data types (100% success rate)
- **SC-E002**: Manual JSON export works correctly for all data types (100% success rate)
- **SC-E003**: CSV files can be opened in Excel/Google Sheets without formatting issues
- **SC-E004**: Auto-export checkboxes are checked by default on page load
- **SC-E005**: Auto-export downloads files within 1 second of query completion
- **SC-E006**: Auto-export does NOT trigger when query returns 0 rows
- **SC-E007**: Auto-export does NOT trigger when query fails
- **SC-E008**: Export filename format matches specification (100% compliance)

---

## Dependencies

### Internal Dependencies
- QueryResults component (已存在)
- QueryEditor component (需要修改)
- QueryPanel/Query page (需要修改)
- API response format (已定义,符合contracts/api.yaml)

### External Dependencies
- Ant Design (Checkbox组件)
- React (useState, useEffect, useRef)
- Browser APIs (Blob, URL, navigator.clipboard)

---

## Testing Strategy

### Unit Tests
1. `convertToCSV` 函数测试
   - 正常数据
   - 特殊字符
   - NULL值
   - 边界情况(空数组)

2. `convertToJSON` 函数测试
   - 正常数据
   - 特殊字符
   - NULL值
   - 数据类型保持

### Integration Tests
1. 手动导出流程
   - 渲染QueryResults组件
   - 点击CSV按钮
   - 验证文件下载

2. 自动导出流程
   - 渲染QueryEditor和QueryResults
   - 设置auto-export配置
   - 执行查询
   - 验证自动下载

### Manual Testing
1. 浏览器兼容性
   - Chrome
   - Firefox
   - Safari
   - Edge

2. 文件打开测试
   - Excel (Windows)
   - Numbers (Mac)
   - Google Sheets
   - 文本编辑器

---

## Implementation Checklist

### Phase 1: Manual Export Verification
- [ ] 验证现有导出功能代码
- [ ] 测试CSV导出各种数据类型
- [ ] 测试JSON导出各种数据类型
- [ ] 测试特殊字符转义
- [ ] 测试NULL值处理
- [ ] 修复发现的问题(如有)

### Phase 2: Auto Export Implementation
- [ ] 在QueryEditor添加Checkbox UI
- [ ] 实现auto-export state管理
- [ ] 在QueryResults添加auto-export逻辑
- [ ] 传递配置props
- [ ] 测试auto-export触发逻辑
- [ ] 测试边界情况(空结果、查询失败)
- [ ] 验证默认checkbox状态

### Phase 3: Polish
- [ ] 添加加载状态提示
- [ ] 优化用户体验
- [ ] 更新文档(如有需要)
- [ ] 代码审查和重构

---

## Future Enhancements

### Potential Improvements
1. **Export Format Options**
   - Excel (.xlsx) 格式
   - TSV (Tab-Separated Values)
   - XML 格式

2. **Export Customization**
   - 自定义文件名
   - 选择特定列导出
   - 过滤行导出

3. **Export History**
   - 保存最近的导出记录
   - 快速重新导出之前的结果

4. **Advanced Auto Export**
   - 导出到云存储 (Google Drive, Dropbox)
   - 定时导出任务
   - 导出模板保存

5. **Performance**
   - 大数据集流式导出
   - 后台导出队列
   - 导出进度显示

---

## Notes

- 导出功能使用纯前端实现,无需后端API修改
- 文件下载通过触发浏览器原生下载行为实现
- 文件名时间戳格式确保跨平台兼容性
- 自动导出逻辑需要注意避免重复触发(使用useRef跟踪)
- 所有导出操作都在客户端完成,不增加服务器负载
