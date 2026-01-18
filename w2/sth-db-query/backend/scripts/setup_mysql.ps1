# MySQL数据库和表创建脚本
# 使用方法：在PowerShell中运行此脚本，然后输入MySQL root密码

$env:Path += ";C:\Program Files\MySQL\MySQL Server 8.0\bin"
$sqlFile = "e:\ai编程实战营\geektime-ai-bootcamp\create_mysql_tables.sql"

Write-Host "正在创建MySQL数据库和表..." -ForegroundColor Green
Write-Host "请输入MySQL root密码：" -ForegroundColor Yellow

$password = Read-Host -AsSecureString
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

Get-Content $sqlFile | & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p$plainPassword

if ($LASTEXITCODE -eq 0) {
    Write-Host "数据库和表创建成功！" -ForegroundColor Green
} else {
    Write-Host "创建失败，请检查错误信息。" -ForegroundColor Red
}
