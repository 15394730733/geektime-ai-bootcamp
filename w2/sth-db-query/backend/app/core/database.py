"""
Database configuration and session management.

This module provides SQLAlchemy session configuration and utilities
for the SQLite database used to store connections and metadata.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator

from ..core.config import settings


# Create async engine for SQLite
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
SessionLocal = async_sessionmaker(
    engine, 
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# Export async session for direct use
async_session = SessionLocal


# Create base class for models
Base: DeclarativeBase = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields a database session and ensures it's closed after use.
    """
    async with SessionLocal() as session:
        yield session


async def create_tables():
    """
    Create all database tables.

    This function should be called during application startup to ensure
    all tables are created in the SQLite database.
    """
    # Import all models to ensure they are registered
    from ..models import Base  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all database tables.

    WARNING: This will delete all data. Use with caution.
    """
    # Import all models to ensure they are registered
    from ..models import Base  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
