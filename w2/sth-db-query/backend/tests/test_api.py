"""
API tests for the Database Query Tool.
"""

import json


def test_health_check(client):
    """Test health check endpoint.

    验证健康检查端点的正确性：
    - 响应状态码为200
    - 返回JSON数据包含status字段为"healthy"
    - 返回JSON数据包含service字段为"database-query-tool"
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database-query-tool"


def test_openapi_docs_available(client):
    """Test that OpenAPI documentation is available.

    验证OpenAPI文档端点的可用性：
    - 能够成功获取OpenAPI JSON文档
    - 文档包含info和paths字段
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "paths" in data


def test_cors_headers(client):
    """Test CORS headers are present.

    验证跨域资源共享（CORS）配置：
    - OPTIONS请求到数据库API端点应返回CORS头
    - 包含access-control-allow-origin头
    """
    response = client.options("/api/v1/dbs",
                            headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_get_databases_empty(client):
    """Test getting empty database list.

    验证获取数据库列表API在没有数据库时的行为：
    - 响应状态码为200
    - 返回成功的响应格式
    - 数据字段为空列表
    """
    response = client.get("/api/v1/dbs")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


def test_create_database(client, sample_database_data):
    """Test creating a database connection.

    验证创建数据库连接的API功能：
    - 能够成功创建数据库连接
    - 返回的数据库信息包含正确的字段（id, name, url, description等）
    - 自动设置创建时间和更新时间
    - 默认状态为激活（is_active为true）
    """
    response = client.post("/api/v1/dbs", json=sample_database_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == sample_database_data["name"]
    assert data["data"]["url"] == sample_database_data["url"]
    assert data["data"]["description"] == sample_database_data["description"]
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]
    assert data["data"]["is_active"] is True


def test_get_databases_after_create(client, sample_database_data):
    """Test getting database list after creating one.

    验证创建数据库后获取数据库列表的功能：
    - 先创建数据库连接
    - 然后获取数据库列表
    - 列表中应包含刚创建的数据库
    - 验证数据库信息正确性
    """
    # First create a database
    client.post("/api/v1/dbs", json=sample_database_data)

    # Then get the list
    response = client.get("/api/v1/dbs")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == sample_database_data["name"]


def test_get_database_by_name(client, sample_database_data):
    """Test getting a specific database by name.

    验证通过数据库名称获取特定数据库的功能：
    - 先创建数据库连接
    - 通过名称查询数据库
    - 返回正确的数据库信息
    - 验证响应格式和数据正确性
    """
    # Create a database first
    client.post("/api/v1/dbs", json=sample_database_data)

    # Get the specific database
    response = client.get(f"/api/v1/dbs/{sample_database_data['name']}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == sample_database_data["name"]


def test_get_database_not_found(client):
    """Test getting a non-existent database.

    验证查询不存在数据库时的错误处理：
    - 请求不存在的数据库名称
    - 返回404状态码
    - 错误响应中包含"not found"相关信息
    """
    response = client.get("/api/v1/dbs/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


def test_update_database(client, sample_database_data):
    """Test updating a database connection.

    验证更新数据库连接信息的API功能：
    - 先创建数据库连接
    - 更新数据库描述信息
    - 验证更新后的信息正确保存
    - 检查响应格式和数据一致性
    """
    # Create a database first
    client.post("/api/v1/dbs", json=sample_database_data)

    # Update it
    updated_data = sample_database_data.copy()
    updated_data["description"] = "Updated description"
    response = client.put(f"/api/v1/dbs/{sample_database_data['name']}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["description"] == "Updated description"


def test_delete_database(client, sample_database_data):
    """Test deleting a database connection.

    验证删除数据库连接的API功能：
    - 先创建数据库连接
    - 删除指定的数据库
    - 验证删除操作成功
    - 确认数据库已被彻底删除（再次查询返回404）
    """
    # Create a database first
    client.post("/api/v1/dbs", json=sample_database_data)

    # Delete it
    response = client.delete(f"/api/v1/dbs/{sample_database_data['name']}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify it's gone
    response = client.get(f"/api/v1/dbs/{sample_database_data['name']}")
    assert response.status_code == 404


def test_create_duplicate_database(client, sample_database_data):
    """Test creating a database with duplicate name.

    验证创建重复名称数据库时的处理逻辑：
    - 先创建一个数据库连接
    - 尝试使用相同名称创建另一个数据库
    - 验证系统正确处理重复创建的情况（返回失败响应）
    """
    # Create first database
    client.post("/api/v1/dbs", json=sample_database_data)

    # Try to create another with same name
    response = client.post("/api/v1/dbs", json=sample_database_data)
    # This might return 400 or 500 depending on implementation
    # For now, we'll just check that it's not successful
    data = response.json()
    assert data["success"] is False


def test_create_database_invalid_url(client):
    """Test creating a database with invalid URL.

    验证输入验证功能，测试无效URL的处理：
    - 使用无效的数据库URL尝试创建连接
    - 验证返回422验证错误状态码
    - 确认错误响应格式正确
    """
    invalid_data = {
        "name": "invalid_db",
        "url": "not_a_valid_url",
        "description": "Invalid database"
    }
    response = client.post("/api/v1/dbs", json=invalid_data)
    assert response.status_code == 422  # Validation error
    data = response.json()
    assert data["success"] is False


def test_create_database_invalid_name(client):
    """Test creating a database with invalid name.

    验证输入验证功能，测试无效数据库名称的处理：
    - 使用包含空格的无效数据库名称尝试创建连接
    - 验证返回422验证错误状态码
    - 确认错误响应格式正确
    """
    invalid_data = {
        "name": "invalid name with spaces",
        "url": "postgresql://user:pass@localhost:5432/test",
        "description": "Invalid name"
    }
    response = client.post("/api/v1/dbs", json=invalid_data)
    assert response.status_code == 422  # Validation error
    data = response.json()
    assert data["success"] is False
