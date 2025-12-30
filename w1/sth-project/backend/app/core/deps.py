"""
依赖注入模块
提供 FastAPI 依赖注入函数
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: dict = Depends(security)
) -> str:
    """
    获取当前用户 ID
    
    Args:
        credentials: HTTP Bearer 凭证
    
    Returns:
        用户 ID
    
    Raises:
        HTTPException: 未授权时抛出
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息"
        )
    
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息"
        )
    
    return token
