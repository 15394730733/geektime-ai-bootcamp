# MySQL数据库和表创建指南

## 方法1：使用MySQL Workbench（最简单）

1. 打开MySQL Workbench
2. 点击"Database" → "Connect to Database"
3. 选择你的MySQL连接（通常是Local instance MySQL80）
4. 输入密码连接
5. 连接成功后，点击"File" → "Open SQL Script"
6. 选择文件：`e:\ai编程实战营\geektime-ai-bootcamp\create_mysql_tables.sql`
7. 点击执行按钮（闪电图标）

## 方法2：使用命令行

1. 打开PowerShell或CMD
2. 执行以下命令：
   ```bash
   mysql -u root -p
   ```
3. 输入密码
4. 在MySQL命令行中执行：
   ```sql
   source e:\ai编程实战营\geektime-ai-bootcamp\create_mysql_tables.sql
   ```

## 方法3：重置root密码（如果忘记密码）

如果忘记了root密码，可以按照以下步骤重置：

1. 停止MySQL服务：
   ```powershell
   Stop-Service MySQL80
   ```

2. 创建一个临时配置文件：
   ```powershell
   Add-Content "C:\ProgramData\MySQL\MySQL Server 8.0\my-init.ini" "[mysqld]`nskip-grant-tables"
   ```

3. 启动MySQL服务：
   ```powershell
   Start-Service MySQL80
   ```

4. 连接到MySQL：
   ```bash
   mysql -u root
   ```

5. 重置密码：
   ```sql
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED BY '你的新密码';
   ```

6. 删除临时配置文件并重启MySQL服务：
   ```powershell
   Remove-Item "C:\ProgramData\MySQL\MySQL Server 8.0\my-init.ini"
   Restart-Service MySQL80
   ```

## 验证创建结果

执行完成后，可以运行以下命令验证：

```sql
USE test_db;
SHOW TABLES;
DESC database_connections;
DESC database_metadata;
DESC query_history;
```

## 注意事项

- 确保MySQL服务正在运行
- 如果使用命令行，确保已将MySQL的bin目录添加到PATH
- SQL脚本会创建test_db数据库和3个表
- 如果数据库已存在，脚本会跳过创建
