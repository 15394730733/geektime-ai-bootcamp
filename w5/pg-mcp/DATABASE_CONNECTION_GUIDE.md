# 数据库连接配置指南

## 问题诊断

你遇到的错误表明数据库连接配置有问题：

```
connection to server at "localhost" (::1), port 5173 failed: received invalid response to SSL negotiation
```

## 问题分析

1. **端口错误**: 你使用了端口 `5173`，但这通常是前端开发服务器的端口
2. **PostgreSQL 默认端口**: PostgreSQL 数据库的默认端口是 `5432`

## 正确的连接配置

### 标准 PostgreSQL 连接 URL 格式：
```
postgresql://用户名:密码@主机:端口/数据库名
```

### 示例配置：

#### 本地 PostgreSQL (默认配置)：
```
postgresql://postgres:123456@localhost:5432/projectalpha
```

#### 如果使用 Docker 运行的 PostgreSQL：
```
postgresql://postgres:123456@localhost:5432/projectalpha
```

#### 如果 PostgreSQL 运行在不同端口：
```
postgresql://postgres:123456@localhost:自定义端口/projectalpha
```

## 修复步骤

1. **检查 PostgreSQL 服务状态**：
   - 确保 PostgreSQL 服务正在运行
   - 检查服务运行的端口（通常是 5432）

2. **更新连接 URL**：
   - 将端口从 `5173` 改为 `5432`
   - 确保数据库名 `projectalpha` 存在

3. **验证连接参数**：
   - 用户名: `postgres`
   - 密码: `123456`
   - 主机: `localhost`
   - 端口: `5432`
   - 数据库: `projectalpha`

## 测试连接

使用正确的 URL 重新测试连接：
```
postgresql://postgres:123456@localhost:5432/projectalpha
```

## 常见问题

1. **数据库不存在**: 确保 `projectalpha` 数据库已创建
2. **认证失败**: 检查用户名和密码是否正确
3. **服务未运行**: 启动 PostgreSQL 服务
4. **防火墙问题**: 确保端口 5432 未被阻止

## 如何检查 PostgreSQL 状态

### Windows:
```cmd
# 检查服务状态
sc query postgresql-x64-14

# 启动服务
net start postgresql-x64-14
```

### 使用 psql 命令行测试连接:
```bash
psql -h localhost -p 5432 -U postgres -d projectalpha
```