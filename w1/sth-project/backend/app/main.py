"""
FastAPI 应用主入口
配置并启动 FastAPI 应用
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import tickets, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI 应用实例
    """
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Ticket 标签管理工具 API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
app.include_router(tags.router)


@app.get("/")
async def root():
    """
    根路径
    
    Returns:
        欢迎消息
    """
    return {
        "message": "Ticket Manager API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    """
    健康检查
    
    Returns:
        健康状态
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }
