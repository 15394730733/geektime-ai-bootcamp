"""
数据库事务测试
测试数据库事务的正确性，包括回滚和提交
"""
import pytest
from sqlalchemy import select
from app.models.ticket import Ticket
from app.models.tag import Tag


@pytest.mark.asyncio
async def test_create_ticket_success_commit(client, db_session):
    """测试成功创建 Ticket 后事务正确提交"""
    response = await client.post(
        "/api/v1/addTickets",
        json={
            "title": "测试 Ticket",
            "description": "这是一个测试 Ticket"
        }
    )
    assert response.status_code == 200
    data = response.json()
    ticket_id = data["data"]
    
    # 验证数据已提交到数据库
    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    assert ticket is not None
    assert ticket.title == "测试 Ticket"
    assert ticket.description == "这是一个测试 Ticket"


@pytest.mark.asyncio
async def test_create_tag_success_commit(client, db_session):
    """测试成功创建 Tag 后事务正确提交"""
    response = await client.post(
        "/api/v1/addTags",
        json={
            "name": "测试标签",
            "color": "#ff0000"
        }
    )
    assert response.status_code == 200
    data = response.json()
    tag_id = data["data"]
    
    # 验证数据已提交到数据库
    result = await db_session.execute(
        select(Tag).where(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    assert tag is not None
    assert tag.name == "测试标签"
    assert tag.color == "#ff0000"


@pytest.mark.asyncio
async def test_create_duplicate_tag_rollback(client, db_session):
    """测试创建重复 Tag 时事务正确回滚"""
    # 创建第一个 Tag
    await client.post(
        "/api/v1/addTags",
        json={"name": "重复标签", "color": "#00ff00"}
    )
    
    # 尝试创建重复的 Tag
    response = await client.post(
        "/api/v1/addTags",
        json={"name": "重复标签", "color": "#0000ff"}
    )
    assert response.status_code == 409
    
    # 验证数据库中只有一个该名称的 Tag
    result = await db_session.execute(
        select(Tag).where(Tag.name == "重复标签")
    )
    tags = result.scalars().all()
    assert len(tags) == 1
    assert tags[0].color == "#00ff00"


@pytest.mark.asyncio
async def test_delete_ticket_transaction(client, db_session):
    """测试删除 Ticket 时事务正确处理"""
    # 创建一个 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "待删除 Ticket"}
    )
    ticket_id = create_response.json()["data"]
    
    # 验证 Ticket 存在
    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    assert result.scalar_one_or_none() is not None
    
    # 删除 Ticket
    delete_response = await client.delete(f"/api/v1/tickets/{ticket_id}")
    assert delete_response.status_code == 200
    
    # 验证 Ticket 已从数据库中删除
    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_update_ticket_transaction(client, db_session):
    """测试更新 Ticket 时事务正确处理"""
    # 创建一个 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "原始标题", "description": "原始描述"}
    )
    ticket_id = create_response.json()["data"]
    
    # 更新 Ticket
    update_response = await client.put(
        f"/api/v1/updateTickets/{ticket_id}",
        json={"title": "更新标题", "description": "更新描述"}
    )
    assert update_response.status_code == 200
    
    # 验证数据库中的数据已更新
    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    assert ticket.title == "更新标题"
    assert ticket.description == "更新描述"


@pytest.mark.asyncio
async def test_ticket_with_tags_transaction(client, db_session):
    """测试创建带标签的 Ticket 时事务正确处理"""
    # 创建 Tag
    tag_response = await client.post(
        "/api/v1/addTags",
        json={"name": "测试标签", "color": "#ff0000"}
    )
    tag_id = tag_response.json()["data"]
    
    # 创建带标签的 Ticket
    ticket_response = await client.post(
        "/api/v1/addTickets",
        json={
            "title": "带标签的 Ticket",
            "tags": ["测试标签"]
        }
    )
    assert ticket_response.status_code == 200
    ticket_id = ticket_response.json()["data"]
    
    # 验证 Ticket 和 Tag 关系已正确保存
    result = await db_session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    assert ticket is not None
    assert len(ticket.tags) == 1
    assert ticket.tags[0].id == tag_id


@pytest.mark.asyncio
async def test_multiple_operations_in_transaction(client, db_session):
    """测试多个操作在同一个事务中的正确性"""
    # 创建多个 Tag
    tags = []
    for i in range(3):
        response = await client.post(
            "/api/v1/addTags",
            json={"name": f"标签{i}", "color": f"#ff{i:02d}00"}
        )
        tags.append(response.json()["data"])
    
    # 创建多个 Ticket
    tickets = []
    for i in range(3):
        response = await client.post(
            "/api/v1/addTickets",
            json={"title": f"Ticket{i}"}
        )
        tickets.append(response.json()["data"])
    
    # 验证所有数据都已正确保存
    tag_result = await db_session.execute(select(Tag))
    all_tags = tag_result.scalars().all()
    assert len(all_tags) == 3
    
    ticket_result = await db_session.execute(select(Ticket))
    all_tickets = ticket_result.scalars().all()
    assert len(all_tickets) == 3
