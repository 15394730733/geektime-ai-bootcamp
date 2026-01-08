#!/usr/bin/env python3
"""
简单的PostgreSQL连接测试
"""

import psycopg2
import sys
from urllib.parse import urlparse

def test_connection():
    url = "postgresql://postgres:123456@localhost:5432/projectalpha"
    
    try:
        print(f"测试连接: {url}")
        
        # 解析URL
        parsed = urlparse(url)
        print(f"主机: {parsed.hostname}")
        print(f"端口: {parsed.port or 5432}")
        print(f"数据库: {parsed.path.lstrip('/')}")
        print(f"用户: {parsed.username}")
        
        # 尝试连接
        print("\n正在连接...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            connect_timeout=5
        )
        
        # 测试查询
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ 连接成功!")
        print(f"PostgreSQL版本: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        error_str = str(e)
        print(f"❌ 连接失败: {error_str}")
        
        if "could not connect to server" in error_str:
            print("💡 PostgreSQL服务可能未启动")
        elif "password authentication failed" in error_str:
            print("💡 用户名或密码错误")
        elif "database" in error_str and "does not exist" in error_str:
            print("💡 数据库 'projectalpha' 不存在")
        elif "role" in error_str and "does not exist" in error_str:
            print("💡 用户 'postgres' 不存在")
        
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)