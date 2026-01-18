@echo off
chcp 65001 >nul
echo ========================================
echo MySQL 数据库和表创建工具
echo ========================================
echo.

set MYSQL_PATH=C:\Program Files\MySQL\MySQL Server 8.0\bin
set SQL_FILE=e:\ai编程实战营\geektime-ai-bootcamp\create_mysql_tables.sql

echo 正在检查MySQL路径...
if not exist "%MYSQL_PATH%\mysql.exe" (
    echo 错误：找不到MySQL，请检查路径
    pause
    exit /b 1
)

echo MySQL路径正确
echo.

echo 请选择连接方式：
echo 1. 使用密码连接
echo 2. 无密码连接（如果root用户没有设置密码）
echo.
set /p choice="请输入选项 (1 或 2): "

if "%choice%"=="1" goto with_password
if "%choice%"=="2" goto without_password

echo 无效选项
pause
exit /b 1

:with_password
echo.
echo 正在连接MySQL...
echo 请输入root密码：
"%MYSQL_PATH%\mysql.exe" -u root -p < "%SQL_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 创建成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 创建失败，请检查密码是否正确
    echo ========================================
)
goto end

:without_password
echo.
echo 正在连接MySQL（无密码）...
"%MYSQL_PATH%\mysql.exe" -u root < "%SQL_FILE%"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 创建成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 创建失败，可能需要密码
    echo ========================================
)
goto end

:end
echo.
pause
