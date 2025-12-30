"""
Tag API 路由
提供 Tag 相关的 API 端点
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.schemas.tag import TagCreate, TagResponse
from app.crud.tag import get_tag, get_tags, get_tag_by_name, create_tag, delete_tag
from app.crud.ticket import get_ticket
from app.models.ticket import TicketTag
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/api/v1", tags=["tags"])


@router.get("/listTags", response_model=dict)
async def get_tags_endpoint(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取 Tag 列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
    
    Returns:
        Tag 列表响应
    """
    tags, total = await get_tags(db, skip=skip, limit=limit)
    
    tag_responses = []
    for tag in tags:
        tag_responses.append({
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at
        })
    
    return success_response(data={
        "tags": tag_responses,
        "total": total
    })


@router.post("/addTags", response_model=dict)
async def create_tag_endpoint(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建 Tag
    
    Args:
        tag: Tag 创建数据
        db: 数据库会话
    
    Returns:
        创建成功的响应
    """
    existing_tag = await get_tag_by_name(db, tag.name)
    if existing_tag:
        raise HTTPException(status_code=409, detail="标签已存在")
    
    db_tag = await create_tag(db, tag)
    return success_response(data=str(db_tag.id), message="标签创建成功", code=200)


@router.post("/addTicketTags/{ticket_id}", response_model=dict)
async def add_ticket_tags_endpoint(
    ticket_id: UUID,
    tag_ids: List[UUID],
    db: AsyncSession = Depends(get_db)
):
    """
    为 Ticket 添加标签
    
    Args:
        ticket_id: Ticket ID
        tag_ids: Tag ID 列表
        db: 数据库会话
    
    Returns:
        添加成功的响应
    """
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket 不存在")
    
    for tag_id in tag_ids:
        tag = await get_tag(db, tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail=f"标签 {tag_id} 不存在")
        
        existing_relation = await db.execute(
            select(TicketTag).where(
                and_(TicketTag.ticket_id == ticket_id, TicketTag.tag_id == tag_id)
            )
        )
        if not existing_relation.scalar_one_or_none():
            ticket_tag = TicketTag(ticket_id=ticket_id, tag_id=tag_id)
            db.add(ticket_tag)
    
    await db.commit()
    return success_response(message="标签添加成功")


@router.delete("/deleteTicketTags/{ticket_id}/{tag_id}", response_model=dict)
async def delete_ticket_tag_endpoint(
    ticket_id: UUID,
    tag_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    从 Ticket 移除标签
    
    Args:
        ticket_id: Ticket ID
        tag_id: Tag ID
        db: 数据库会话
    
    Returns:
        移除成功的响应
    """
    ticket_tag = await db.execute(
        select(TicketTag).where(
            and_(TicketTag.ticket_id == ticket_id, TicketTag.tag_id == tag_id)
        )
    )
    ticket_tag = ticket_tag.scalar_one_or_none()
    if not ticket_tag:
        raise HTTPException(status_code=404, detail="标签关联不存在")
    
    await db.delete(ticket_tag)
    await db.commit()
    return success_response(message="标签移除成功")


@router.delete("/tags/{tag_id}", response_model=dict)
async def delete_tag_endpoint(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    删除 Tag
    
    Args:
        tag_id: Tag ID
        db: 数据库会话
    
    Returns:
        删除成功的响应
    """
    success = await delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    return success_response(message="标签删除成功", code=200)
