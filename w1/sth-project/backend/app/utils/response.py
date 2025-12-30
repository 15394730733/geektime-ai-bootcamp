"""
统一响应格式工具
提供统一的 API 响应格式
"""
from typing import Any, Optional
import time


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
    timestamp: Optional[float] = None
) -> dict:
    """
    生成成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应状态码
        timestamp: 时间戳
    
    Returns:
        统一格式的响应字典
    """
    response = {
        "code": code,
        "message": message,
        "timestamp": timestamp or time.time()
    }
    if data is not None:
        response["data"] = data
    return response


def error_response(
    message: str = "error",
    code: int = 500,
    details: Optional[Any] = None,
    timestamp: Optional[float] = None
) -> dict:
    """
    生成错误响应
    
    Args:
        message: 错误消息
        code: 错误状态码
        details: 错误详情
        timestamp: 时间戳
    
    Returns:
        统一格式的错误响应字典
    """
    response = {
        "code": code,
        "message": message,
        "timestamp": timestamp or time.time()
    }
    if details is not None:
        response["details"] = details
    return response
