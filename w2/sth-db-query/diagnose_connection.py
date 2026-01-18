#!/usr/bin/env python3
"""
PostgreSQL连接诊断脚本
用于诊断数据库连接问题
"""

import psycopg2
import socket
import subprocess
import sys
from urllib.parse import urlparse

def test_port_connectivity(host, port):
    """测试端口连通性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"端口测试错误: {e}")
        return False

def check_postgresql_service():
    """检查PostgreSQL服务状态"""
    try:
        # Windows服务检查
        result = subprocess.run(['sc', 'query', 'postgresql-x64-14'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            if 'RUNNING' in result.stdout:
                print("✅ PostgreSQL服务正在运行")
                return True
            else:
                print("❌ PostgreSQL服务未运行")
                print("服务状态:", result.stdout)
                return False
        else:
            # 尝试其他常见的服务名
            services = ['postgresql-x64-13', 'postgresql-x64-12', 'postgresql', 'PostgreSQL']
            for service in services:
                result = subprocess.run(['sc', 'query', service], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0 and 'RUNNING' in result.stdout:
                    print(f"✅ PostgreSQL服务正在运行 ({service})")
                    return True
            
            print("❌ 未找到运行中的PostgreSQL服务")
            return False
    except Exception as e:
        print(f"检查服务状态时出错: {e}")
        return False

def test_database_connection(url):
    """测试数据库连接"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/')
        username = parsed.username
        password = parsed.password
        
        print(f"\n🔍 连接参数:")
        print(f"  主机: {host}")
        print(f"  端口: {port}")
        print(f"  数据库: {database}")
        print(f"  用户名: {username}")
        print(f"  密码: {'*' * len(password) if password else 'None'}")
        
        # 1. 测试端口连通性
        print(f"\n1️⃣ 测试端口连通性 ({host}:{port})")
        if test_port_connectivity(host, port):
            print("✅ 端口连通")
        else:
            print("❌ 端口不通 - PostgreSQL可能未运行或端口被阻止")
            return False
        
        # 2. 测试数据库连接
        print(f"\n2️⃣ 测试数据库连接")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=5
        )
        
        # 3. 测试查询
        print("3️⃣ 测试基本查询")
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ 连接成功! PostgreSQL版本: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        error_str = str(e)
        print(f"❌ 连接失败: {error_str}")
        
        # 分析常见错误
        if "could not connect to server" in error_str:
            print("💡 建议: PostgreSQL服务可能未启动")
        elif "password authentication failed" in error_str:
            print("💡 建议: 用户名或密码错误")
        elif "database" in error_str and "does not exist" in error_str:
            print("💡 建议: 数据库不存在，需要先创建")
        elif "role" in error_str and "does not exist" in error_str:
            print("💡 建议: 用户不存在，需要先创建用户")
        
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def check_common_issues():
    """检查常见问题"""
    print("\n🔧 常见问题检查:")
    
    # 检查常见端口占用
    ports_to_check = [5432, 5433, 5434]
    for port in ports_to_check:
        if test_port_connectivity('localhost', port):
            print(f"✅ 端口 {port} 有服务监听")
        else:
            print(f"❌ 端口 {port} 无服务监听")

def main():
    print("🔍 PostgreSQL连接诊断工具")
    print("=" * 50)
    
    # 测试URL
    test_url = "postgresql://postgres:123456@localhost:5432/projectalpha"
    print(f"测试连接: {test_url}")
    
    # 1. 检查PostgreSQL服务
    print("\n📋 步骤1: 检查PostgreSQL服务状态")
    service_running = check_postgresql_service()
    
    # 2. 检查常见问题
    check_common_issues()
    
    # 3. 测试连接
    print(f"\n📋 步骤2: 测试数据库连接")
    connection_success = test_database_connection(test_url)
    
    # 4. 总结和建议
    print("\n📋 诊断总结:")
    if service_running and connection_success:
        print("✅ 所有检查通过，连接应该正常工作")
    else:
        print("❌ 发现问题，请根据上述建议进行修复")
        
        if not service_running:
            print("\n🔧 启动PostgreSQL服务:")
            print("  net start postgresql-x64-14")
            print("  (或者使用服务管理器启动)")
        
        print("\n🔧 其他可能的解决方案:")
        print("1. 检查PostgreSQL配置文件 (postgresql.conf)")
        print("2. 检查客户端认证配置 (pg_hba.conf)")
        print("3. 确保数据库 'projectalpha' 存在")
        print("4. 确保用户 'postgres' 有正确的权限")
        print("5. 检查防火墙设置")

if __name__ == "__main__":
    main()