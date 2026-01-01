"""
Database configuration and session management.

This module provides SQLAlchemy async session configuration and utilities
for the SQLite database used to store connections and metadata.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..core.config import settings


# Create async engine for SQLite
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Yields an async database session and ensures it's closed after use.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables.

    This function should be called during application startup to ensure
    all tables are created in the SQLite database.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from ..models import Base  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all database tables.

    WARNING: This will delete all data. Use with caution.
    """
    async with engine.begin() as conn:
        from ..models import Base  # noqa: F401
        await conn.run_sync(Base.metadata.drop_all)
