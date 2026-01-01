"""
Database management endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database import DatabaseService, DatabaseServiceError
from app.schemas import database as database_schema

router = APIRouter()
database_service = DatabaseService()


@router.get("/", response_model=List[database_schema.Database])
async def get_databases(db: AsyncSession = Depends(get_db)):
    """Get all database connections."""
    try:
        return await database_service.list_databases(db)
    except DatabaseServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")


@router.put("/{name}", response_model=database_schema.Database)
async def create_or_update_database(
    name: str,
    database: database_schema.DatabaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create or update a database connection."""
    try:
        # Check if database already exists
        existing = await database_service.get_database(db, name)

        if existing:
            # Update existing database
            result = await database_service.update_database(db, name, database)
            if not result:
                raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
            return result
        else:
            # Validate that the name in URL matches the name in data
            if name != database.name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Database name in URL '{name}' must match name in request body '{database.name}'"
                )

            # Create new database
            return await database_service.create_database(db, database)

    except DatabaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update database: {str(e)}")


@router.get("/{name}", response_model=database_schema.Database)
async def get_database(name: str, db: AsyncSession = Depends(get_db)):
    """Get a specific database connection."""
    try:
        database = await database_service.get_database(db, name)
        if not database:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
        return database
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database: {str(e)}")


@router.delete("/{name}")
async def delete_database(name: str, db: AsyncSession = Depends(get_db)):
    """Delete a database connection."""
    try:
        success = await database_service.delete_database(db, name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
        return {"message": f"Database '{name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete database: {str(e)}")
