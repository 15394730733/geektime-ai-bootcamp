#!/usr/bin/env python3
"""
测试API连接
"""

import requests
import json

def test_connection_api():
    url = "http://localhost:8000/api/v1/dbs/test-connection"
    
    data = {
        "name": "test",
        "url": "postgresql://postgres:123456@localhost:5432/projectalpha",
        "description": ""
    }
    
    try:
        print(f"测试API: {url}")
        print(f"数据: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ API测试成功!")
            return True
        else:
            print("❌ API测试失败")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 后端服务可能未运行")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    test_connection_api()