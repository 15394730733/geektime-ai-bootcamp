"""
Tag Pydantic Schema
定义 Tag 相关的数据验证模型
"""
from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Tag 基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: str = Field(
        default="#0070f3",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="标签颜色，格式为 #RRGGBB"
    )


class TagCreate(TagBase):
    """Tag 创建模型"""
    pass


class TagUpdate(TagBase):
    """Tag 更新模型"""
    pass


class TagResponse(TagBase):
    """Tag 响应模型"""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Tag 列表响应模型"""
    tags: List[TagResponse]
    total: int
