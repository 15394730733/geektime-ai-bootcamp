"""
Tag CRUD 操作
提供 Tag 数据库操作函数
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


async def get_tag(db: AsyncSession, tag_id: UUID) -> Optional[Tag]:
    """
    根据 ID 获取 Tag
    
    Args:
        db: 数据库会话
        tag_id: Tag ID
    
    Returns:
        Tag 对象或 None
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_tags(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Tag], int]:
    """
    获取 Tag 列表
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数
    
    Returns:
        Tag 列表和总数
    """
    total_query = select(func.count()).select_from(Tag)
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    result = await db.execute(select(Tag).offset(skip).limit(limit))
    tags = result.scalars().all()
    
    return list(tags), total


async def get_tag_by_name(db: AsyncSession, name: str) -> Optional[Tag]:
    """
    根据名称获取 Tag
    
    Args:
        db: 数据库会话
        name: Tag 名称
    
    Returns:
        Tag 对象或 None
    """
    result = await db.execute(select(Tag).where(Tag.name == name))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, tag: TagCreate) -> Tag:
    """
    创建 Tag
    
    Args:
        db: 数据库会话
        tag: Tag 创建数据
    
    Returns:
        创建的 Tag 对象
    """
    db_tag = Tag(name=tag.name, color=tag.color)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    
    return db_tag


async def update_tag(
    db: AsyncSession,
    tag_id: UUID,
    tag: TagUpdate
) -> Optional[Tag]:
    """
    更新 Tag
    
    Args:
        db: 数据库会话
        tag_id: Tag ID
        tag: Tag 更新数据
    
    Returns:
        更新后的 Tag 对象或 None
    """
    db_tag = await get_tag(db, tag_id)
    if not db_tag:
        return None
    
    update_data = tag.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)
    
    await db.commit()
    await db.refresh(db_tag)
    
    return db_tag


async def delete_tag(db: AsyncSession, tag_id: UUID) -> bool:
    """
    删除 Tag
    
    Args:
        db: 数据库会话
        tag_id: Tag ID
    
    Returns:
        是否删除成功
    """
    db_tag = await get_tag(db, tag_id)
    if not db_tag:
        return False
    
    await db.delete(db_tag)
    await db.commit()
    
    return True
