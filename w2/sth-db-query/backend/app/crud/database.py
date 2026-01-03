"""
CRUD operations for database connections.
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import DatabaseConnection
from app.models.metadata import DatabaseMetadata
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


# Metadata CRUD operations
async def get_database_metadata(db: AsyncSession, connection_id: str) -> List[DatabaseMetadata]:
    """Get all metadata for a database connection."""
    result = await db.execute(
        select(DatabaseMetadata).where(DatabaseMetadata.connection_id == connection_id)
    )
    return result.scalars().all()


async def create_database_metadata(db: AsyncSession, metadata_list: List[Dict[str, Any]]) -> List[DatabaseMetadata]:
    """Create multiple metadata entries."""
    import json
    metadata_objects = []
    for metadata in metadata_list:
        # Convert columns list to JSON string if it's a list
        if isinstance(metadata.get('columns'), list):
            metadata = metadata.copy()
            metadata['columns'] = json.dumps(metadata['columns'], ensure_ascii=False)

        metadata_obj = DatabaseMetadata(
            id=str(uuid4()),
            **metadata
        )
        db.add(metadata_obj)
        metadata_objects.append(metadata_obj)

    await db.commit()
    for obj in metadata_objects:
        await db.refresh(obj)
    return metadata_objects


async def delete_database_metadata(db: AsyncSession, connection_id: str) -> int:
    """Delete all metadata for a database connection."""
    result = await db.execute(
        select(DatabaseMetadata).where(DatabaseMetadata.connection_id == connection_id)
    )
    metadata_objects = result.scalars().all()

    count = len(metadata_objects)
    for obj in metadata_objects:
        await db.delete(obj)

    await db.commit()
    return count
