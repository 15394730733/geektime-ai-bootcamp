#!/usr/bin/env python3
"""
测试PATCH编辑数据库连接API
"""

import requests
import json

def test_patch_database():
    # 首先确保数据库连接存在
    create_url = "http://localhost:8000/api/v1/dbs/test"
    create_data = {
        "name": "test",
        "url": "postgresql://postgres:123456@localhost:5432/projectalpha",
        "description": "测试数据库"
    }
    
    print("1. 确保数据库连接存在...")
    try:
        response = requests.put(create_url, json=create_data, timeout=10)
        print(f"创建/更新状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ 数据库连接就绪")
        else:
            print(f"❌ 准备失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 准备请求失败: {e}")
        return False

    # 测试PATCH编辑
    patch_url = "http://localhost:8000/api/v1/dbs/test"
    patch_data = {
        "description": "任务清单的库，编辑一下",
        "url": "postgresql://postgres:123456@localhost:5432/projectalpha"
    }
    
    print("\n2. 使用PATCH编辑数据库连接...")
    try:
        response = requests.patch(patch_url, json=patch_data, timeout=10)
        print(f"PATCH状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 数据库连接PATCH编辑成功!")
            return True
        else:
            print("❌ PATCH编辑失败")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ PATCH请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 后端服务可能未运行")
        return False
    except Exception as e:
        print(f"❌ PATCH请求失败: {e}")
        return False

if __name__ == "__main__":
    success = test_patch_database()
    if success:
        print("\n🎉 PATCH测试通过!")
    else:
        print("\n❌ PATCH测试失败")