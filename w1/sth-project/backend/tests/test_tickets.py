"""
测试 Ticket API
"""
import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_ticket(client):
    """测试创建 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={
            "title": "测试 Ticket",
            "description": "这是一个测试 Ticket",
            "tags": ["测试", "重要"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Ticket 创建成功"
    assert "data" in data


@pytest.mark.asyncio
async def test_get_tickets(client):
    """测试获取 Ticket 列表"""
    response = await client.get("/api/v1/listTickets")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "tickets" in data["data"]
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_get_tickets_with_search(client):
    """测试带搜索关键词获取 Ticket 列表"""
    response = await client.get("/api/v1/listTickets?search=测试")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_get_ticket_not_found(client):
    """测试获取不存在的 Ticket"""
    fake_id = uuid4()
    response = await client.get(f"/api/v1/tickets/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_ticket_not_found(client):
    """测试更新不存在的 Ticket"""
    fake_id = uuid4()
    response = await client.put(
        f"/api/v1/updateTickets/{fake_id}",
        json={"title": "更新标题"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_ticket_not_found(client):
    """测试删除不存在的 Ticket"""
    fake_id = uuid4()
    response = await client.delete(f"/api/v1/tickets/{fake_id}")
    assert response.status_code == 404
