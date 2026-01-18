#!/usr/bin/env python3
"""
测试编辑数据库连接API
"""

import requests
import json

def test_edit_database():
    # 首先创建一个数据库连接
    create_url = "http://localhost:8000/api/v1/dbs/test"
    create_data = {
        "name": "test",
        "url": "postgresql://postgres:123456@localhost:5432/projectalpha",
        "description": "测试数据库"
    }
    
    print("1. 创建数据库连接...")
    try:
        response = requests.put(create_url, json=create_data, timeout=10)
        print(f"创建状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ 数据库连接创建成功")
        else:
            print(f"❌ 创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建请求失败: {e}")
        return False

    # 然后测试编辑
    edit_url = "http://localhost:8000/api/v1/dbs/test"
    edit_data = {
        "description": "任务清单的库，编辑一下",
        "url": "postgresql://postgres:123456@localhost:5432/projectalpha"
    }
    
    print("\n2. 编辑数据库连接...")
    try:
        response = requests.put(edit_url, json=edit_data, timeout=10)
        print(f"编辑状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 数据库连接编辑成功!")
            return True
        else:
            print("❌ 编辑失败")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 编辑请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 后端服务可能未运行")
        return False
    except Exception as e:
        print(f"❌ 编辑请求失败: {e}")
        return False

if __name__ == "__main__":
    success = test_edit_database()
    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 测试失败")