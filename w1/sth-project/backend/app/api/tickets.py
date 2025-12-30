"""
Ticket API 路由
提供 Ticket 相关的 API 端点
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.crud.ticket import get_ticket, get_tickets, create_ticket, update_ticket, delete_ticket
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/api/v1", tags=["tickets"])


@router.post("/addTickets", response_model=dict)
async def create_ticket_endpoint(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建 Ticket
    
    Args:
        ticket: Ticket 创建数据
        db: 数据库会话
    
    Returns:
        创建成功的响应
    """
    db_ticket = await create_ticket(db, ticket)
    return success_response(data=str(db_ticket.id), message="Ticket 创建成功", code=200)


@router.get("/listTickets", response_model=dict)
async def get_tickets_endpoint(
    tag: Optional[str] = Query(None, description="按标签筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取 Ticket 列表
    
    Args:
        tag: 标签筛选
        search: 搜索关键词
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
    
    Returns:
        Ticket 列表响应
    """
    tickets, total = await get_tickets(db, skip=skip, limit=limit, tag=tag, search=search)
    
    ticket_responses = []
    for ticket in tickets:
        tags = []
        for ticket_tag in ticket.tags:
            tags.append({
                "id": ticket_tag.tag.id,
                "name": ticket_tag.tag.name,
                "color": ticket_tag.tag.color
            })
        
        ticket_responses.append({
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "is_completed": ticket.is_completed,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "tags": tags
        })
    
    return success_response(data={
        "tickets": ticket_responses,
        "total": total
    })


@router.get("/tickets/{ticket_id}", response_model=dict)
async def get_ticket_endpoint(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个 Ticket 详情
    
    Args:
        ticket_id: Ticket ID
        db: 数据库会话
    
    Returns:
        Ticket 详情响应
    """
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket 不存在")
    
    tags = []
    for ticket_tag in ticket.tags:
        tags.append({
            "id": ticket_tag.tag.id,
            "name": ticket_tag.tag.name,
            "color": ticket_tag.tag.color
        })
    
    return success_response(data={
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "is_completed": ticket.is_completed,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "tags": tags
    })


@router.put("/updateTickets/{ticket_id}", response_model=dict)
async def update_ticket_endpoint(
    ticket_id: UUID,
    ticket: TicketUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新 Ticket
    
    Args:
        ticket_id: Ticket ID
        ticket: Ticket 更新数据
        db: 数据库会话
    
    Returns:
        更新成功的响应
    """
    db_ticket = await update_ticket(db, ticket_id, ticket)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket 不存在")
    
    return success_response(message="Ticket 更新成功")


@router.delete("/tickets/{ticket_id}", response_model=dict)
async def delete_ticket_endpoint(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    删除 Ticket
    
    Args:
        ticket_id: Ticket ID
        db: 数据库会话
    
    Returns:
        删除成功的响应
    """
    success = await delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket 不存在")
    
    return success_response(message="Ticket 删除成功", code=200)
