# Frontend - Database Query Tool

## 技术栈

- **React 19** - 用户界面框架
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 快速构建工具
- **Tailwind CSS v4** - 实用优先的 CSS 框架
- **Ant Design** - 企业级 UI 组件库
- **Refine** - React 框架，用于构建数据密集型应用
- **Vitest** - 现代测试框架

## Tailwind CSS v4 更新

项目已升级到 Tailwind CSS v4，带来了以下改进：

### 新特性
- 🚀 **更快的编译速度** - 显著提升开发和构建性能
- 🎨 **CSS-first 配置** - 使用 CSS 变量进行主题配置
- 📦 **更好的树摇优化** - 只打包使用的样式
- 🔧 **改进的开发者体验** - 更好的错误提示和调试

### 配置方式
- **传统配置**: `tailwind.config.js` (保持向后兼容)
- **新配置**: `src/styles/tailwind.css` (推荐用于 v4)

### 自定义主题
```css
/* src/styles/tailwind.css */
@theme {
  --color-primary-50: #e6f7ff;
  --color-primary-500: #1890ff;
  /* ... 其他颜色变量 */
}
```

## 开发

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 运行测试
```bash
npm run test          # 运行所有测试
npm run test:ui       # 启动测试 UI
npm run test:coverage # 生成覆盖率报告
```

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
npm run type-check
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── DatabaseList.tsx # 数据库连接列表
│   │   ├── DatabaseForm.tsx # 数据库连接表单
│   │   └── ...
│   ├── pages/              # 页面组件
│   │   ├── databases.tsx   # 数据库管理页面
│   │   └── Query.tsx       # 查询页面
│   ├── services/           # API 服务
│   ├── styles/             # 样式文件
│   │   ├── globals.css     # 全局样式
│   │   └── tailwind.css    # Tailwind CSS 配置
│   └── types/              # TypeScript 类型定义
├── tailwind.config.js      # Tailwind 配置 (兼容模式)
├── vitest.config.ts        # 测试配置
└── package.json
```

## 样式指南

### Tailwind CSS 类名使用
- 使用 `@apply` 指令创建组件类
- 遵循移动优先的设计原则
- 使用语义化的颜色名称

### 自定义组件样式
```css
@layer components {
  .btn-primary {
    @apply bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md;
  }
}
```

## 测试

项目使用 Vitest 进行单元测试和集成测试：

- **单元测试**: 测试单个组件和工具函数
- **集成测试**: 测试组件间的交互
- **E2E 测试**: 测试完整用户流程

### 编写测试
```typescript
import { render, screen } from '@testing-library/react';
import { DatabaseList } from './DatabaseList';

test('renders database list', () => {
  render(<DatabaseList />);
  expect(screen.getByText('Databases')).toBeInTheDocument();
});
```
