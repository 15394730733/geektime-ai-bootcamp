"""
测试 Tag API
"""
import pytest


@pytest.mark.asyncio
async def test_create_tag(client):
    """测试创建 Tag"""
    response = await client.post(
        "/api/v1/addTags",
        json={
            "name": "测试标签",
            "color": "#ff0000"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "标签创建成功"
    assert "data" in data


@pytest.mark.asyncio
async def test_create_duplicate_tag(client):
    """测试创建重复的 Tag"""
    await client.post(
        "/api/v1/addTags",
        json={"name": "重复标签", "color": "#00ff00"}
    )
    
    response = await client.post(
        "/api/v1/addTags",
        json={"name": "重复标签", "color": "#0000ff"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_tags(client):
    """测试获取 Tag 列表"""
    response = await client.get("/api/v1/listTags")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "tags" in data["data"]
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_delete_tag_not_found(client):
    """测试删除不存在的 Tag"""
    from uuid import uuid4
    fake_id = uuid4()
    response = await client.delete(f"/api/v1/tags/{fake_id}")
    assert response.status_code == 404
