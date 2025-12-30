"""
Ticket CRUD 操作
提供 Ticket 数据库操作函数
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ticket import Ticket, TicketTag
from app.models.tag import Tag
from app.schemas.ticket import TicketCreate, TicketUpdate


async def get_ticket(db: AsyncSession, ticket_id: UUID) -> Optional[Ticket]:
    """
    根据 ID 获取 Ticket
    
    Args:
        db: 数据库会话
        ticket_id: Ticket ID
    
    Returns:
        Ticket 对象或 None
    """
    result = await db.execute(
        select(Ticket)
        .options(selectinload(Ticket.tags).selectinload(TicketTag.tag))
        .where(Ticket.id == ticket_id)
    )
    return result.scalar_one_or_none()


async def get_tickets(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None,
    search: Optional[str] = None
) -> tuple[List[Ticket], int]:
    """
    获取 Ticket 列表
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数
        tag: 标签筛选
        search: 搜索关键词
    
    Returns:
        Ticket 列表和总数
    """
    query = select(Ticket).options(selectinload(Ticket.tags).selectinload(TicketTag.tag))
    
    if tag:
        query = query.join(TicketTag).join(Tag).where(Tag.name == tag)
    
    if search:
        query = query.where(Ticket.title.ilike(f"%{search}%"))
    
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return list(tickets), total


async def get_or_create_tag_by_name(db: AsyncSession, name: str) -> Tag:
    """
    根据名称获取或创建 Tag
    
    Args:
        db: 数据库会话
        name: Tag 名称
    
    Returns:
        Tag 对象
    """
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    
    return tag


async def create_ticket(db: AsyncSession, ticket: TicketCreate) -> Ticket:
    """
    创建 Ticket
    
    Args:
        db: 数据库会话
        ticket: Ticket 创建数据
    
    Returns:
        创建的 Ticket 对象
    """
    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description
    )
    db.add(db_ticket)
    await db.flush()
    
    if ticket.tags:
        for tag_name in ticket.tags:
            tag = await get_or_create_tag_by_name(db, tag_name)
            ticket_tag = TicketTag(ticket_id=db_ticket.id, tag_id=tag.id)
            db.add(ticket_tag)
    
    await db.commit()
    await db.refresh(db_ticket)
    
    return await get_ticket(db, db_ticket.id)


async def update_ticket(
    db: AsyncSession,
    ticket_id: UUID,
    ticket: TicketUpdate
) -> Optional[Ticket]:
    """
    更新 Ticket
    
    Args:
        db: 数据库会话
        ticket_id: Ticket ID
        ticket: Ticket 更新数据
    
    Returns:
        更新后的 Ticket 对象或 None
    """
    db_ticket = await get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    
    update_data = ticket.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    await db.commit()
    await db.refresh(db_ticket)
    
    return db_ticket


async def delete_ticket(db: AsyncSession, ticket_id: UUID) -> bool:
    """
    删除 Ticket
    
    Args:
        db: 数据库会话
        ticket_id: Ticket ID
    
    Returns:
        是否删除成功
    """
    db_ticket = await get_ticket(db, ticket_id)
    if not db_ticket:
        return False
    
    await db.delete(db_ticket)
    await db.commit()
    
    return True
