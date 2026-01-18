# Scripts 目录

本目录包含数据库查询工具项目的所有脚本文件。

## 目录结构

```
scripts/
├── sql/                    # SQL 脚本文件
│   ├── check_indexes.sql                    # 检查数据库索引
│   ├── create_interview_db.sql              # 创建面试管理数据库
│   ├── create_mysql_tables.sql              # 创建 MySQL 数据表
│   ├── mysql_setup.sql                      # MySQL 初始化脚本
│   └── mysql_setup_fixed.sql                # 修复版 MySQL 初始化脚本
├── check_db.py             # 数据库连接检查脚本
├── init_db.bat             # 数据库初始化批处理脚本（Windows）
├── setup_mysql.bat         # MySQL 安装配置脚本（Windows）
├── setup_mysql.ps1         # MySQL 安装配置脚本（PowerShell）
└── start_backend.bat       # 启动后端服务脚本（Windows）
```

## 使用说明

### SQL 脚本

SQL 脚本位于 `sql/` 子目录中，主要用于：

- **数据库初始化**: `create_interview_db.sql` 创建完整的面试管理数据库结构
- **表结构创建**: `create_mysql_tables.sql` 创建基础数据表
- **索引检查**: `check_indexes.sql` 检查数据库索引状态

使用方法：
```bash
# 在 MySQL 命令行中
mysql -u root -p < scripts/sql/create_interview_db.sql
```

### Python 脚本

- **check_db.py**: 检查数据库连接状态
  ```bash
  python scripts/check_db.py
  ```

### Windows 批处理脚本

- **init_db.bat**: 初始化数据库
- **setup_mysql.bat**: 设置 MySQL（命令提示符）
- **setup_mysql.ps1**: 设置 MySQL（PowerShell）
- **start_backend.bat**: 启动后端开发服务器

## 维护说明

- 添加新脚本时，请遵循此目录结构
- SQL 脚本统一放在 `sql/` 子目录
- 为新脚本添加适当的使用说明
- 确保脚本具有执行权限（Linux/Mac）
