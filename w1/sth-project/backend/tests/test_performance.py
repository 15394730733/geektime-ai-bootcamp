"""
性能测试
测试 API 端点的性能，包括响应时间和并发处理能力
"""
import pytest
import asyncio
import time
from typing import List


@pytest.mark.asyncio
async def test_create_ticket_performance(client):
    """测试创建 Ticket 的性能"""
    start_time = time.time()
    
    response = await client.post(
        "/api/v1/addTickets",
        json={"title": "性能测试 Ticket", "description": "性能测试描述"}
    )
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0, f"创建 Ticket 响应时间 {response_time:.3f}s 超过 1s"


@pytest.mark.asyncio
async def test_get_tickets_performance(client):
    """测试获取 Ticket 列表的性能"""
    # 先创建一些 Ticket
    for i in range(10):
        await client.post(
            "/api/v1/addTickets",
            json={"title": f"性能测试 Ticket {i}"}
        )
    
    start_time = time.time()
    response = await client.get("/api/v1/listTickets")
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.5, f"获取 Ticket 列表响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_search_tickets_performance(client):
    """测试搜索 Ticket 的性能"""
    # 创建一些 Ticket
    for i in range(20):
        await client.post(
            "/api/v1/addTickets",
            json={"title": f"搜索测试 Ticket {i}", "description": "包含搜索关键词"}
        )
    
    start_time = time.time()
    response = await client.get("/api/v1/listTickets?search=搜索")
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.5, f"搜索 Ticket 响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_filter_by_tag_performance(client):
    """测试按标签筛选 Ticket 的性能"""
    # 创建 Tag
    tag_response = await client.post(
        "/api/v1/addTags",
        json={"name": "性能测试标签", "color": "#ff0000"}
    )
    
    # 创建带标签的 Ticket
    for i in range(15):
        await client.post(
            "/api/v1/addTickets",
            json={"title": f"标签测试 Ticket {i}", "tags": ["性能测试标签"]}
        )
    
    start_time = time.time()
    response = await client.get("/api/v1/listTickets?tag=性能测试标签")
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.5, f"按标签筛选响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_concurrent_create_tickets(client):
    """测试并发创建 Ticket 的性能"""
    async def create_ticket(index: int):
        return await client.post(
            "/api/v1/addTickets",
            json={"title": f"并发测试 Ticket {index}"}
        )
    
    start_time = time.time()
    
    tasks = [create_ticket(i) for i in range(20)]
    responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    assert all(r.status_code == 200 for r in responses)
    assert total_time < 5.0, f"并发创建 20 个 Ticket 总时间 {total_time:.3f}s 超过 5s"
    print(f"平均每个 Ticket 创建时间: {total_time / 20:.3f}s")


@pytest.mark.asyncio
async def test_concurrent_get_tickets(client):
    """测试并发获取 Ticket 列表的性能"""
    # 先创建一些 Ticket
    for i in range(10):
        await client.post(
            "/api/v1/addTickets",
            json={"title": f"并发读取测试 Ticket {i}"}
        )
    
    async def get_tickets():
        return await client.get("/api/v1/listTickets")
    
    start_time = time.time()
    
    tasks = [get_tickets() for _ in range(30)]
    responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    assert all(r.status_code == 200 for r in responses)
    assert total_time < 3.0, f"并发读取 30 次 Ticket 列表总时间 {total_time:.3f}s 超过 3s"
    print(f"平均每次读取时间: {total_time / 30:.3f}s")


@pytest.mark.asyncio
async def test_update_ticket_performance(client):
    """测试更新 Ticket 的性能"""
    # 创建 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "原始标题"}
    )
    ticket_id = create_response.json()["data"]
    
    start_time = time.time()
    
    response = await client.put(
        f"/api/v1/updateTickets/{ticket_id}",
        json={"title": "更新标题", "description": "更新描述"}
    )
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.5, f"更新 Ticket 响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_delete_ticket_performance(client):
    """测试删除 Ticket 的性能"""
    # 创建 Ticket
    create_response = await client.post(
        "/api/v1/addTickets",
        json={"title": "待删除 Ticket"}
    )
    ticket_id = create_response.json()["data"]
    
    start_time = time.time()
    
    response = await client.delete(f"/api/v1/tickets/{ticket_id}")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 0.5, f"删除 Ticket 响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_pagination_performance(client):
    """测试分页查询的性能"""
    # 创建大量 Ticket
    for i in range(100):
        await client.post(
            "/api/v1/addTickets",
            json={"title": f"分页测试 Ticket {i}"}
        )
    
    # 测试不同页面的查询时间
    for page in [0, 2, 5, 9]:
        start_time = time.time()
        response = await client.get(f"/api/v1/listTickets?skip={page * 10}&limit=10")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 0.5, f"第 {page} 页查询响应时间 {response_time:.3f}s 超过 0.5s"


@pytest.mark.asyncio
async def test_large_dataset_performance(client):
    """测试大数据集下的性能"""
    # 创建大量 Ticket
    for i in range(50):
        await client.post(
            "/api/v1/addTickets",
            json={
                "title": f"大数据集测试 Ticket {i}",
                "description": "这是一个较长的描述文本，用于测试大数据集下的性能表现"
            }
        )
    
    # 测试获取所有数据
    start_time = time.time()
    response = await client.get("/api/v1/listTickets?limit=50")
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0, f"获取 50 条数据响应时间 {response_time:.3f}s 超过 1s"
    
    data = response.json()
    assert data["data"]["total"] >= 50
