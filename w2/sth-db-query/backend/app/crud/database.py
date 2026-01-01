"""
CRUD operations for database connections.
"""

from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import DatabaseConnection
from app.schemas.database import DatabaseCreate


async def get_databases(db: AsyncSession) -> List[DatabaseConnection]:
    """Get all database connections."""
    result = await db.execute(select(DatabaseConnection))
    return result.scalars().all()


async def get_database(db: AsyncSession, name: str) -> Optional[DatabaseConnection]:
    """Get a database connection by name."""
    result = await db.execute(
        select(DatabaseConnection).where(DatabaseConnection.name == name)
    )
    return result.scalar_one_or_none()


async def create_database(db: AsyncSession, database: DatabaseCreate) -> DatabaseConnection:
    """Create a new database connection."""
    db_obj = DatabaseConnection(
        id=str(uuid4()),
        **database.model_dump()
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_database(db: AsyncSession, name: str, database: DatabaseCreate) -> Optional[DatabaseConnection]:
    """Update a database connection."""
    db_obj = await get_database(db, name)
    if db_obj:
        for field, value in database.model_dump().items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
    return db_obj


async def delete_database(db: AsyncSession, name: str) -> bool:
    """Delete a database connection."""
    db_obj = await get_database(db, name)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
        return True
    return False
