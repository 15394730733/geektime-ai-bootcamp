# Implementation Plan: Query Page Layout

## Overview

重构数据库查询工具前端，实现专业级左右分栏布局。使用 `react-resizable-panels` 实现可拖拽分割面板，保持现有技术栈。

## Tasks

- [x] 1. 安装依赖和基础设置
  - 安装 `react-resizable-panels` 包
  - 创建布局相关的类型定义
  - 创建 localStorage 工具函数用于布局持久化
  - _Requirements: 1.5, 5.3_

- [x] 2. 实现 MetadataPanel 组件
  - [x] 2.1 创建 MetadataPanel 组件框架
    - 包含搜索输入框和 SchemaTree 容器
    - 实现搜索状态管理
    - _Requirements: 2.7_
  - [x] 2.2 重构 SchemaTree 组件
    - 从 MetadataViewer 提取树形逻辑
    - 添加搜索过滤功能
    - 实现点击表名/列名的回调
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [x] 2.3 编写 SchemaTree 属性测试
    - **Property 3: Schema Tree Hierarchy Rendering**
    - **Property 5: Search Filter Accuracy**
    - **Validates: Requirements 2.1, 2.3, 2.4, 2.7**

- [x] 3. 实现 TabBar 组件
  - [x] 3.1 创建 TabBar 组件
    - 显示查询标签页列表
    - 支持新建、切换、关闭标签页
    - 显示当前数据库名称
    - _Requirements: 3.1, 3.2, 3.3, 3.7_
  - [x] 3.2 编写 TabBar 单元测试
    - 测试标签页创建、切换、关闭
    - 测试未保存更改提示
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. 实现 QueryPanel 组件
  - [x] 4.1 创建 QueryPanel 组件框架
    - 集成 TabBar、QueryEditor、QueryResults
    - 实现垂直分割布局
    - _Requirements: 5.1, 5.2_
  - [x] 4.2 实现多标签页状态管理
    - 每个标签页独立的查询内容和结果
    - 标签页切换时保持状态
    - _Requirements: 3.1_
  - [x] 4.3 编写 QueryPanel 属性测试
    - **Property 6: Tab Independence**
    - **Validates: Requirements 3.1**

- [x] 5. 重构 QueryPage 主页面
  - [x] 5.1 实现水平分割布局
    - 使用 react-resizable-panels 创建左右分割
    - 左侧 MetadataPanel，右侧 QueryPanel
    - 默认左侧宽度 280px
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x] 5.2 实现布局持久化
    - 保存/恢复水平和垂直分割比例到 localStorage
    - _Requirements: 1.5, 5.3_
  - [x] 5.3 实现点击插入功能
    - 点击表名插入完整限定名 (schema.table)
    - 点击列名插入列名
    - _Requirements: 2.5, 2.6_
  - [x] 5.4 编写布局持久化属性测试
    - **Property 1: Layout Persistence Round-Trip**
    - **Property 2: Panel Resize Constraints**
    - **Validates: Requirements 1.4, 1.5, 5.3, 6.3**

- [x] 6. 实现响应式设计
  - [x] 6.1 添加小屏幕适配
    - viewport < 768px 时折叠左侧面板为抽屉
    - 添加显示/隐藏切换按钮
    - _Requirements: 6.1, 6.2_
  - [x] 6.2 添加最小宽度约束
    - 左侧面板最小 200px
    - 右侧面板最小 400px
    - _Requirements: 6.3_

- [x] 7. Checkpoint - 确保所有测试通过
  - 运行所有单元测试和属性测试
  - 如有问题请询问用户

- [x] 8. 样式优化和收尾
  - [x] 8.1 添加分割线样式
    - 拖拽手柄的视觉反馈
    - hover 和 active 状态样式
  - [x] 8.2 优化整体视觉效果
    - 确保与现有 Ant Design 主题一致
    - 调整间距和边框
    - 确保与现有 Ant Design 主题一致
    - 调整间距和边框

- [x] 9. 移除侧边栏导航并简化流程
  - [x] 9.1 重构 App.tsx 移除 Refine 布局组件
    - 移除 ThemedLayoutV2 和 ThemedSiderV2
    - 直接渲染路由内容
    - 保留 Refine 的核心功能（dataProvider, notificationProvider）
    - _Requirements: 7.1, 7.3_
  - [x] 9.2 更新数据库列表页面
    - 点击数据库卡片跳转到 `/query?db={databaseName}`
    - 添加数据库卡片的点击处理
    - _Requirements: 7.2_
  - [x] 9.3 更新查询页面头部
    - 添加返回数据库列表的按钮
    - 从 URL 参数读取并自动选择数据库
    - 优化头部布局
    - _Requirements: 7.4_

## Notes

- 所有任务均为必需，包括测试任务
- 每个任务都引用了具体的需求条目以便追溯
- 属性测试验证核心正确性属性
- 单元测试覆盖边界条件和错误处理
