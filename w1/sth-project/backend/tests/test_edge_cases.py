"""
边界条件和错误处理测试
测试 API 端点的边界条件和各种错误情况
"""
import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_ticket_empty_title(client):
    """测试创建标题为空的 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "", "description": "测试描述"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_ticket_missing_title(client):
    """测试创建缺少标题的 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={"description": "测试描述"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_ticket_very_long_title(client):
    """测试创建标题过长的 Ticket"""
    long_title = "A" * 1000
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": long_title}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_ticket_very_long_description(client):
    """测试创建描述过长的 Ticket"""
    long_description = "A" * 10000
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "测试 Ticket", "description": long_description}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_ticket_with_invalid_tags(client):
    """测试创建带无效标签的 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "测试 Ticket", "tags": ["不存在的标签"]}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_ticket_with_empty_tags(client):
    """测试创建带空标签列表的 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "测试 Ticket", "tags": []}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_tickets_invalid_skip(client):
    """测试使用无效的 skip 参数获取 Ticket 列表"""
    response = await client.get("/api/v1/listTickets?skip=-1")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_tickets_invalid_limit(client):
    """测试使用无效的 limit 参数获取 Ticket 列表"""
    response = await client.get("/api/v1/listTickets?limit=0")
    assert response.status_code == 422
    
    response = await client.get("/api/v1/listTickets?limit=101")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_tickets_boundary_limit(client):
    """测试使用边界 limit 参数获取 Ticket 列表"""
    response = await client.get("/api/v1/listTickets?limit=1")
    assert response.status_code == 200
    
    response = await client.get("/api/v1/listTickets?limit=100")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_ticket_invalid_id(client):
    """测试使用无效 ID 获取 Ticket"""
    response = await client.get("/api/v1/tickets/invalid-id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_ticket_empty_title(client):
    """测试更新 Ticket 时标题为空"""
    # 创建 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "原始标题"}
    )
    ticket_id = create_response.json()["data"]
    
    # 尝试更新为空标题
    response = await client.put(
        f"/api/v1/updateTickets/{ticket_id}",
        json={"title": ""}
    )
    assert response.status_code == 422


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
async def test_delete_ticket_invalid_id(client):
    """测试删除 Ticket 时使用无效 ID"""
    response = await client.delete("/api/v1/tickets/invalid-id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_ticket_not_found(client):
    """测试删除不存在的 Ticket"""
    fake_id = uuid4()
    response = await client.delete(f"/api/v1/tickets/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_tag_empty_name(client):
    """测试创建名称为空的 Tag"""
    response = await client.post(
        "/api/v1/addTags",
        json={"name": "", "color": "#ff0000"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_missing_name(client):
    """测试创建缺少名称的 Tag"""
    response = await client.post(
        "/api/v1/addTags",
        json={"color": "#ff0000"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_invalid_color(client):
    """测试创建颜色格式无效的 Tag"""
    response = await client.post(
        "/api/v1/addTags",
        json={"name": "测试标签", "color": "invalid-color"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_missing_color(client):
    """测试创建缺少颜色的 Tag"""
    response = await client.post(
        "/api/v1/addTags",
        json={"name": "测试标签"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_very_long_name(client):
    """测试创建名称过长的 Tag"""
    long_name = "A" * 100
    response = await client.post(
        "/api/v1/addTags",
        json={"name": long_name, "color": "#ff0000"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_tag_invalid_id(client):
    """测试删除 Tag 时使用无效 ID"""
    response = await client.delete("/api/v1/tags/invalid-id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_tag_not_found(client):
    """测试删除不存在的 Tag"""
    fake_id = uuid4()
    response = await client.delete(f"/api/v1/tags/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_with_special_characters(client):
    """测试使用特殊字符搜索"""
    await client.post(
        "/api/v1/addTickets",
        json={"title": "测试特殊字符 !@#$%^&*()"}
    )
    
    response = await client.get("/api/v1/listTickets?search=!@#$%^&*()")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_unicode(client):
    """测试使用 Unicode 字符搜索"""
    await client.post(
        "/api/v1/addTickets",
        json={"title": "测试中文 🎉 测试日文 テスト 测试韩文 테스트"}
    )
    
    response = await client.get("/api/v1/listTickets?search=中文")
    assert response.status_code == 200
    
    response = await client.get("/api/v1/listTickets?search=🎉")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pagination_with_empty_result(client):
    """测试空结果集的分页"""
    response = await client.get("/api/v1/listTickets?skip=100&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] == 0
    assert len(data["data"]["tickets"]) == 0


@pytest.mark.asyncio
async def test_create_ticket_with_null_fields(client):
    """测试创建包含 null 字段的 Ticket"""
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "测试 Ticket", "description": None}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_ticket_with_null_fields(client):
    """测试更新 Ticket 时使用 null 字段"""
    # 创建 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "原始标题", "description": "原始描述"}
    )
    ticket_id = create_response.json()["data"]
    
    # 更新时只提供部分字段
    response = await client.put(
        f"/api/v1/updateTickets/{ticket_id}",
        json={"title": "更新标题"}
    )
    assert response.status_code == 200
    
    # 验证描述未被清除
    get_response = await client.get(f"/api/v1/tickets/{ticket_id}")
    ticket = get_response.json()["data"]
    assert ticket["description"] == "原始描述"


@pytest.mark.asyncio
async def test_concurrent_create_duplicate_tags(client):
    """测试并发创建重复标签"""
    import asyncio
    
    async def create_tag():
        return await client.post(
            "/api/v1/addTags",
            json={"name": "并发测试标签", "color": "#ff0000"}
        )
    
    tasks = [create_tag() for _ in range(5)]
    responses = await asyncio.gather(*tasks)
    
    # 只有一个应该成功，其他的应该失败
    success_count = sum(1 for r in responses if r.status_code == 200)
    conflict_count = sum(1 for r in responses if r.status_code == 409)
    
    assert success_count == 1
    assert conflict_count == 4


@pytest.mark.asyncio
async def test_get_tickets_with_multiple_filters(client):
    """测试使用多个筛选条件获取 Ticket 列表"""
    # 创建 Tag
    await client.post(
        "/api/v1/addTags",
        json={"name": "多条件标签", "color": "#ff0000"}
    )
    
    # 创建带标签的 Ticket
    await client.post(
        "/api/v1/addTickets",
        json={
            "title": "多条件测试 Ticket",
            "description": "包含搜索关键词",
            "tags": ["多条件标签"]
        }
    )
    
    # 同时使用标签和搜索条件
    response = await client.get("/api/v1/listTickets?tag=多条件标签&search=搜索")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["tickets"]) >= 1
