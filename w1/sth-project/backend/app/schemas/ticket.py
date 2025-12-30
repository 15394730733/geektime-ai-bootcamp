"""
Ticket Pydantic Schema
定义 Ticket 相关的数据验证模型
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Tag 基础模型"""
    id: UUID
    name: str
    color: str
    
    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    """Ticket 基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="Ticket 标题")
    description: Optional[str] = Field(None, description="Ticket 描述")


class TicketCreate(TicketBase):
    """Ticket 创建模型"""
    tags: Optional[List[str]] = Field(None, description="标签名称列表")


class TicketUpdate(TicketBase):
    """Ticket 更新模型"""
    is_completed: Optional[bool] = Field(None, description="是否完成")


class TicketResponse(TicketBase):
    """Ticket 响应模型"""
    id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    tags: List[TagBase] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Ticket 列表响应模型"""
    tickets: List[TicketResponse]
    total: int
