"""
Database management endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database import DatabaseService, DatabaseServiceError
from app.schemas import database as database_schema
from app.utils.response import APIResponse

router = APIRouter()
database_service = DatabaseService()


@router.get("/")
async def get_databases(db: AsyncSession = Depends(get_db)):
    """Get all database connections."""
    try:
        databases = await database_service.list_databases(db)
        return APIResponse.success_response("Databases retrieved successfully", databases)
    except DatabaseServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")


@router.put("/{name}")
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
            return APIResponse.success_response("Database updated successfully", result)
        else:
            # Validate that the name in URL matches the name in data
            if name != database.name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Database name in URL '{name}' must match name in request body '{database.name}'"
                )

            # Create new database
            result = await database_service.create_database(db, database)

            # Extract and cache metadata
            try:
                await database_service.refresh_database_metadata(db, result.url, result.id)
                print(f"Successfully extracted metadata for database '{name}'")
            except Exception as e:
                # Log error but don't fail the database creation
                print(f"Warning: Failed to extract metadata for database '{name}': {str(e)}")

            return APIResponse.success_response("Database created successfully", result)

    except DatabaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update database: {str(e)}")


@router.get("/{name}")
async def get_database_metadata(name: str, db: AsyncSession = Depends(get_db)):
    """Get metadata for a specific database."""
    try:
        # First get the database connection to ensure it exists
        database = await database_service.get_database(db, name)
        if not database:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

        # Get metadata for this database
        metadata = await database_service.get_database_metadata(db, name)

        # If no metadata exists, try to refresh it
        if not metadata.get('tables') and not metadata.get('views'):
            try:
                print(f"No metadata found for database '{name}', attempting to refresh...")
                await database_service.refresh_database_metadata(db, database.url, database.id)
                # Get metadata again after refresh
                metadata = await database_service.get_database_metadata(db, name)
                print(f"Successfully refreshed metadata for database '{name}'")
            except Exception as refresh_error:
                print(f"Failed to refresh metadata for database '{name}': {str(refresh_error)}")
                # Don't fail the request, just return empty metadata

        return APIResponse.success_response("Database metadata retrieved successfully", metadata)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database metadata: {str(e)}")


@router.post("/{name}/refresh")
async def refresh_database_metadata(name: str, db: AsyncSession = Depends(get_db)):
    """Refresh metadata for a specific database."""
    try:
        # First get the database connection to ensure it exists
        database = await database_service.get_database(db, name)
        if not database:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

        # Refresh metadata
        metadata = await database_service.refresh_database_metadata(db, database.url, database.id)

        return APIResponse.success_response(f"Database '{name}' metadata refreshed successfully", metadata)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh database metadata: {str(e)}")


@router.delete("/{name}")
async def delete_database(name: str, db: AsyncSession = Depends(get_db)):
    """Delete a database connection."""
    try:
        success = await database_service.delete_database(db, name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
        return APIResponse.success_response(f"Database '{name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete database: {str(e)}")
