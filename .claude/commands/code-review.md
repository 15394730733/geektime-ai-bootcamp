---
description: 对 Python 和 TypeScript 代码进行深度审查，检查架构设计、代码质量、SOLID 原则、KISS/DRY/YAGNI 原则、函数复杂度和 Builder 模式使用
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

对指定文件或目录进行深度代码审查，基于以下核心原则：

- **架构与设计**：Python 和 TypeScript 最佳实践、清晰的接口设计、可扩展性
- **KISS 原则**：保持简单直接，避免过度设计
- **代码质量**：DRY、YAGNI、SOLID 原则
- **函数复杂度**：函数不超过 150 行，参数不超过 7 个
- **Builder 模式**：复杂对象构建使用 Builder 模式

## Operating Constraints

**READ-ONLY 分析**：不修改任何文件，仅生成结构化审查报告。

**语言特定规范**：
- Python：遵循 PEP 8、PEP 257、类型注解 (PEP 484)、数据类、上下文管理器
- TypeScript：遵循官方风格指南、严格类型、接口优于类型别名、装饰器使用

## Execution Steps

### 1. 解析输入参数

解析 `$ARGUMENTS` 确定审查目标：

**格式支持**：
- 单个文件：`path/to/file.py` 或 `path/to/file.ts`
- 目录：`path/to/directory/`（递归审查所有 .py/.ts/.tsx 文件）
- Glob 模式：`**/*.py`、`src/**/*.ts`
- 指定行号范围：`path/to/file.py:100-200`

**示例**：
- `code-review backend/app/services/`
- `code-review src/components/QueryEditor.tsx:50-150`
- `code-review "**/*.py" --focus architecture`

**选项解析**：
- `--focus <area>`: 聚焦特定领域 (architecture|quality|complexity|security|all)
- `--severity <level>`: 最低严重级别 (critical|high|medium|low)
- `--format <type>`: 输出格式 (markdown|json|table)

### 2. 语言检测与文件分组

```bash
# 查找目标文件
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" \) | head -50
```

**语言检测规则**：
- `.py` → Python
- `.ts` / `.tsx` → TypeScript
- 跳过 `__pycache__`、`node_modules`、`.next`、`dist`、测试文件（除非指定）

### 3. 加载代码上下文

对每个目标文件：

1. **读取完整文件内容**（使用 Read 工具）
2. **解析结构**：
   - Python：提取类定义、函数定义、导入语句、装饰器
   - TypeScript：提取类、接口、函数、类型定义、React 组件

3. **构建抽象语法树 (AST) 等价表示**：
   - 识别模块依赖关系
   - 映射类继承层次
   - 追踪函数调用链（局部）

### 4. 深度审查分析

#### A. 架构与设计审查

**Python 特定检查**：

| 检查项 | 原则 | 严重级别 |
|--------|------|----------|
| 缺少类型注解 (PEP 484) | 类型安全 | Medium |
| 过度使用 `Any` 类型 | 类型安全 | High |
| 缺少抽象基类 (ABC) | 可扩展性 | Medium |
| 魔术方法缺失或实现不当 | Python 最佳实践 | Medium |
| 未使用上下文管理器处理资源 | 资源管理 | High |
| 数据类未使用 `@dataclass` | 代码简洁性 | Low |
| 异常处理过于宽泛 (`except Exception`) | 错误处理 | High |
| 全局变量使用 | 封装性 | High |

**TypeScript 特定检查**：

| 检查项 | 原则 | 严重级别 |
|--------|------|----------|
| 使用 `any` 而非 `unknown` | 类型安全 | High |
| 接口缺失或使用 `type` 别名 | 类型设计 | Medium |
| 缺少泛型约束 | 类型安全 | Medium |
| 组件缺少 Props 类型定义 | React 最佳实践 | High |
| 过度使用类型断言 (`as`) | 类型安全 | High |
| 缺少访问修饰符 (private/public) | 封装性 | Medium |
| 未使用实用工具类型 (Partial, Required 等) | 类型系统利用 | Low |
| 装饰器使用不当 (类装饰器 vs 方法装饰器) | TypeScript 最佳实践 | Medium |

**通用架构检查**：

```
评估维度：
1. 接口设计清晰度
   - 方法命名是否语义化
   - 参数数量是否合理 (≤7 个)
   - 返回类型是否明确

2. 可扩展性
   - 是否使用抽象基类/接口
   - 是否遵循开闭原则 (对扩展开放，对修改封闭)
   - 依赖注入是否合理

3. 模块化程度
   - 单一职责原则 (SRP)
   - 模块间耦合度
   - 依赖方向是否正确
```

#### B. 代码质量审查 (DRY, YAGNI, SOLID)

**DRY (Don't Repeat Yourself) 检测**：

```python
# 检测模式
- 重复的代码块 (>10 行相似度 >80%)
- 重复的业务逻辑
- 重复的数据验证逻辑
- 重复的错误处理模式
```

**检测算法**：
1. 提取函数体和类方法体
2. 计算相似度（基于 AST 结构相似性）
3. 报告重复代码位置和重构建议

**YAGNI (You Aren't Gonna Need It) 检测**：

```python
# 检测模式
- 未使用的函数、类、方法
- 未使用的导入
- 注释掉的代码块
- 过度抽象（为"未来可能"的需求）
- 参数未使用的函数
```

**SOLID 原则违反检测**：

| 原则 | 检测项 | 示例 |
|------|--------|------|
| S (SRP) | 类/函数职责过多 | 一个类处理数据库、网络、UI |
| O (OCP) | 硬编码行为 | 大量 if-elif-else 类型判断 |
| L (LSP) | 子类型破坏父类型契约 | 子类抛出父类未声明的异常 |
| I (ISP) | 胖接口 | 接口方法未被部分实现类使用 |
| D (DIP) | 依赖具体实现 | 直接 new 具体类而非使用接口 |

#### C. 复杂度分析

**函数复杂度检查**：

```python
# 指标
1. 行数统计（不包括注释/空行）
2. 参数数量
3. 圈复杂度 (Cyclomatic Complexity)
4. 嵌套深度
```

**阈值**：

| 指标 | 警告 | 危险 |
|------|------|------|
| 函数行数 | >100 | >150 |
| 参数数量 | >5 | >7 |
| 圈复杂度 | >10 | >15 |
| 嵌套深度 | >4 | >6 |

**圈复杂度计算**：
```
基础复杂度 = 1
+1 每个 if、elif、else、for、while、try、except
+1 每个 case (switch/match)
+1 每个 and/or 逻辑运算符
```

#### D. Builder 模式识别

**应使用 Builder 模式的场景**：

```python
# 检测触发条件
- 构造函数参数 >4 个
- 可选参数过多 (>3 个)
- 参数组合多样性
- 复杂对象构建逻辑

# 评估现有 Builder 实现
- 流式接口 (Fluent Interface) 设计
- 链式调用支持
- 构建步骤的清晰性
- 默认值处理
- 验证逻辑位置
```

**示例评判**：

❌ **反模式**：
```python
# 参数过多，难以使用
class DatabaseConfig:
    def __init__(self, host, port, user, password, database,
                 ssl_mode, timeout, pool_size, encoding):
        ...
```

✅ **Builder 模式**：
```python
class DatabaseConfig:
    class Builder:
        def __init__(self):
            self._host = "localhost"
            self._port = 5432
            # ... 默认值

        def host(self, value):
            self._host = value
            return self

        def build(self) -> DatabaseConfig:
            return DatabaseConfig(self)

config = DatabaseConfig.Builder() \
    .host("localhost") \
    .port(5432) \
    .build()
```

#### E. KISS 原则评估

**过度复杂化检测**：

```python
# 检测模式
- 不必要的抽象层
- 简单问题过度工程化
- 设计模式误用（简单场景用复杂模式）
- 过早优化
- 复杂的泛型/类型层级
```

**评估标准**：
```
对于每个函数/类：
1. 能否用更简单的方式实现？
2. 抽象是否增加了价值？
3. 未来的开发者能否快速理解？
```

#### F. 安全与最佳实践

**Python 安全检查**：

| 检查项 | 风险级别 |
|--------|----------|
| SQL 注入风险（字符串拼接 SQL） | Critical |
| 硬编码密钥/密码 | Critical |
| 不安全的反序列化 (pickle) | Critical |
| eval() 或 exec() 使用 | Critical |
| 随机数生成使用 random 而非 secrets | High |
| 路径遍历风险 | High |

**TypeScript 安全检查**：

| 检查项 | 风险级别 |
|--------|----------|
| dangerouslySetInnerHTML 使用 | High |
| 用户输入直接作为 innerHTML | Critical |
| 缺少 XSS 防护 | High |
| 敏感数据暴露给客户端 | Critical |
| 缺少 CSRF 保护 | High |

### 5. 问题优先级与分类

**严重级别定义**：

| 级别 | 标准 | 示例 |
|------|------|------|
| **Critical** | 安全漏洞、数据丢失风险、严重架构缺陷 | SQL 注入、硬编码密钥、循环依赖 |
| **High** | 严重违反原则、显著影响可维护性 | 函数 >200 行、参数 >10 个、大量重复代码 |
| **Medium** | 中等原则违反、影响代码质量 | 缺少类型注解、圈复杂度 >10、适度重复 |
| **Low** | 轻微改进建议、风格问题 | 命名不规范、缺少文档字符串 |

### 6. 生成审查报告

**输出结构**：

```markdown
# 代码审查报告

## 📊 审查概览

| 指标 | 值 |
|------|-----|
| 审查文件数 | N |
| 总代码行数 | N |
| 发现问题数 | N (Critical: N, High: N, Medium: N, Low: N) |
| 函数复杂度超标 | N |
| 设计建议 | N |

## 🔴 Critical 问题 (N 个)

### [C-001] SQL 注入风险
- **位置**: `backend/app/services/database.py:45`
- **类别**: 安全
- **描述**:
  ```python
  query = f"SELECT * FROM users WHERE name = '{user_input}'"
  ```
- **建议**: 使用参数化查询
  ```python
  query = "SELECT * FROM users WHERE name = $1"
  await conn.fetch(query, user_input)
  ```

## 🟠 High 优先级问题 (N 个)

### [H-001] 函数复杂度过高
- **位置**: `frontend/src/components/QueryEditor.tsx:120-280`
- **类别**: 复杂度
- **描述**:
  - 行数: 160 行 (阈值: 150)
  - 参数: 8 个 (阈值: 7)
  - 圈复杂度: 18 (阈值: 10)
- **重构建议**:
  1. 提取验证逻辑到 `validateQuery()`
  2. 提取 UI 渲染到子组件
  3. 使用 Builder 模式简化配置对象

## 🟡 Medium 优先级问题 (N 个)

## 🟢 Low 优先级问题 (N 个)

## 🏗️ 架构与设计建议

### 接口设计
- [建议内容]

### 可扩展性
- [建议内容]

## 📐 SOLID 原则分析

| 原则 | 状态 | 发现 |
|------|------|------|
| SRP | ⚠️ 部分违反 | `UserService` 同时处理认证和数据访问 |
| OCP | ✅ 良好 | 使用策略模式支持不同数据库 |
| LSP | ✅ 良好 | 无子类型契约破坏 |
| ISP | ⚠️ 需改进 | `IDataProvider` 接口方法过多 |
| DIP | ✅ 良好 | 正确使用依赖注入 |

## 🔧 Builder 模式建议

### 应使用 Builder 模式的类
1. `QueryConfig` (5 个参数)
   - 位置: `backend/app/models/query.py`
   - 建议: 实现 Fluent Builder 接口

### 现有 Builder 实现
- `QueryBuilder`: ✅ 设计良好

## 📊 复杂度热点

| 文件 | 函数/方法 | 行数 | 参数 | 圈复杂度 | 级别 |
|------|-----------|------|------|----------|------|
| `services/database.py` | `execute_query` | 165 | 8 | 18 | 🔴 |
| `components/QueryEditor.tsx` | `handleSubmit` | 142 | 7 | 12 | 🟠 |

## 🔄 DRY 违规检测

### 重复代码块
1. **相似度 85%** - 在 3 个位置重复
   - `backend/app/services/auth.py:45-60`
   - `backend/app/services/user.py:78-93`
   - `backend/app/services/admin.py:120-135`
   - **建议**: 提取到共享的 `validate_password()` 函数

## 📋 KISS 原则评估

### 过度工程化
- `AbstractFactoryBuilderSingleton` 模式过度复杂
- 建议简化为简单的工厂函数

### 简化建议
- 用简单的函数替代 `ConfigLoaderStrategy` 类

## 🎯 优先改进建议

### 立即行动 (Critical + High)
1. [ ] 修复 SQL 注入漏洞 (C-001)
2. [ ] 重构 `execute_query` 函数 (H-001)
3. [ ] 实现参数化查询 (C-002)

### 短期改进 (Medium)
1. [ ] 添加类型注解
2. [ ] 提取重复代码
3. [ ] 实现 Builder 模式

### 长期优化 (Low)
1. [ ] 统一命名规范
2. [ ] 完善文档字符串

## 📈 代码质量评分

| 维度 | 得分 | 备注 |
|------|------|------|
| 架构设计 | 7/10 | 接口清晰，可扩展性良好 |
| 代码质量 | 6/10 | 存在重复代码，需要重构 |
| 复杂度控制 | 5/10 | 多个函数超标 |
| 安全性 | 4/10 | 存在关键安全漏洞 |
| **总体评分** | **5.5/10** | 需要重点改进安全性和复杂度 |
```

### 7. 提供重构建议

对于每个 High/Critical 问题，提供：

1. **问题描述**：当前代码的问题
2. **重构后的代码示例**：遵循最佳实践的示例
3. **迁移步骤**：逐步重构的指导

### 8. 交互式审查选项

在报告末尾询问用户：

```
## 🔍 后续操作

您希望我：
1. 生成详细的重构代码示例 [R]
2. 自动创建重构任务列表 [T]
3. 深入审查特定文件/函数 [S]
4. 仅输出 JSON 格式报告 [J]

请选择操作（输入选项字母）:
```

## Operating Principles

### 审查原则

1. **建设性反馈**：指出问题的同时提供解决方案
2. **上下文感知**：考虑代码的实际用途和业务需求
3. **渐进式改进**：优先解决 Critical/High 问题
4. **尊重业务逻辑**：不质疑合理的复杂性

### 输出格式

- **Markdown**（默认）：易读的报告格式
- **JSON**：可被其他工具解析
- **Table**：紧凑的表格格式（适合终端）

### Token 效率

- 按需加载文件内容（不超过 20 个文件/次）
- 聚合相似问题
- 限制每个严重级别最多 10 个问题
- 提供"汇总+详情"的两级视图

## 语言特定最佳实践

### Python 最佳实践

```python
# ✅ 推荐
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
from contextlib import contextmanager

@dataclass
class User:
    """用户数据类"""
    name: str
    email: str
    age: Optional[int] = None

class UserRepository(ABC):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        pass

@contextmanager
def database_transaction():
    """数据库事务上下文管理器"""
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# 使用 Builder 模式
class QueryBuilder:
    """查询构建器"""

    def __init__(self):
        self._select = "*"
        self._from = ""
        self._where = []
        self._limit = None

    def select(self, fields: str) -> "QueryBuilder":
        self._select = fields
        return self

    def from_(self, table: str) -> "QueryBuilder":
        self._from = table
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._where.append(condition)
        return self

    def limit(self, count: int) -> "QueryBuilder":
        self._limit = count
        return self

    def build(self) -> str:
        query = f"SELECT {self._select} FROM {self._from}"
        if self._where:
            query += " WHERE " + " AND ".join(self._where)
        if self._limit:
            query += f" LIMIT {self._limit}"
        return query

# 使用
query = (QueryBuilder()
    .select("name, email")
    .from_("users")
    .where("age > 18")
    .where("status = 'active'")
    .limit(10)
    .build())
```

### TypeScript 最佳实践

```typescript
// ✅ 推荐
interface DatabaseConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
}

// 使用 Builder 模式
class DatabaseConfigBuilder {
  private config: Partial<DatabaseConfig> = {
    host: "localhost",
    port: 5432,
  };

  withHost(host: string): this {
    this.config.host = host;
    return this;
  }

  withPort(port: number): this {
    this.config.port = port;
    return this;
  }

  withCredentials(username: string, password: string): this {
    this.config.username = username;
    this.config.password = password;
    return this;
  }

  withDatabase(database: string): this {
    this.config.database = database;
    return this;
  }

  build(): DatabaseConfig {
    if (!this.config.host || !this.config.username || !this.config.password) {
      throw new Error("Missing required configuration");
    }
    return this.config as DatabaseConfig;
  }
}

// 使用
const config = new DatabaseConfigBuilder()
  .withHost("localhost")
  .withPort(5432)
  .withCredentials("user", "pass")
  .withDatabase("mydb")
  .build();

// React 组件最佳实践
interface Props {
  onSubmit: (query: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const QueryEditor: React.FC<Props> = ({
  onSubmit,
  placeholder = "Enter query...",
  disabled = false,
}) => {
  // 组件逻辑
};

// 使用工具类型
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
```

## Context

$ARGUMENTS
