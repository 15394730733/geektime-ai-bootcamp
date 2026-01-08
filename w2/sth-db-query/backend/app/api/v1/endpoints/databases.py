"""
Database management endpoints.
"""

from typing import Union
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database import DatabaseService
from app.schemas import database as database_schema
from app.utils.response import APIResponse
from app.core.errors import DatabaseQueryError, get_http_status_code

router = APIRouter()
database_service = DatabaseService()


@router.get("/")
async def get_databases(db: AsyncSession = Depends(get_db)):
    """Get all database connections."""
    try:
        databases = await database_service.list_databases(db)
        return APIResponse.success_response("Databases retrieved successfully", databases)
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")


@router.options("/")
async def options_databases():
    """Handle CORS preflight requests for databases endpoint."""
    return {"message": "OK"}


@router.post("/")
async def create_database(
    database: database_schema.DatabaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new database connection."""
    try:
        # Create new database
        result = await database_service.create_database(db, database)

        # Extract and cache metadata
        try:
            await database_service.refresh_database_metadata(db, result.url, result.id)
            print(f"Successfully extracted metadata for database '{database.name}'")
        except Exception as e:
            # Log error but don't fail the database creation
            print(f"Warning: Failed to extract metadata for database '{database.name}': {str(e)}")

        return APIResponse.success_response("Database created successfully", result)

    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create database: {str(e)}")


@router.put("/{name}")
async def create_or_update_database(
    name: str,
    database: dict,  # 使用dict来接受任意字段
    db: AsyncSession = Depends(get_db)
):
    """Create or update a database connection."""
    try:
        # Check if database already exists
        existing = await database_service.get_database(db, name)

        if existing:
            # Update existing database - create DatabaseUpdate from dict
            update_data = database_schema.DatabaseUpdate(
                url=database.get('url'),
                description=database.get('description')
            )
            result = await database_service.update_database_partial(db, name, update_data)
            if not result:
                raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
            return APIResponse.success_response("Database updated successfully", result)
        else:
            # Create new database - validate required fields
            if 'name' not in database:
                database['name'] = name  # Use name from URL if not provided
                
            # Validate required fields for creation
            required_fields = ['name', 'url']
            missing_fields = [field for field in required_fields if not database.get(field)]
            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required fields for database creation: {', '.join(missing_fields)}"
                )
                
            # Validate that the name in URL matches the name in data
            if name != database['name']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Database name in URL '{name}' must match name in request body '{database['name']}'"
                )

            # Create DatabaseCreate object
            create_data = database_schema.DatabaseCreate(
                name=database['name'],
                url=database['url'],
                description=database.get('description', '')
            )

            # Create new database
            result = await database_service.create_database(db, create_data)

            # Extract and cache metadata
            try:
                await database_service.refresh_database_metadata(db, result.url, result.id)
                print(f"Successfully extracted metadata for database '{name}'")
            except Exception as e:
                # Log error but don't fail the database creation
                print(f"Warning: Failed to extract metadata for database '{name}': {str(e)}")

            return APIResponse.success_response("Database created successfully", result)

    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update database: {str(e)}")


@router.patch("/{name}")
async def update_database(
    name: str,
    database: database_schema.DatabaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing database connection with partial data."""
    try:
        result = await database_service.update_database_partial(db, name, database)
        if not result:
            raise HTTPException(status_code=404, detail=f"Database '{name}' not found")
        return APIResponse.success_response("Database updated successfully", result)

    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update database: {str(e)}")
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


@router.post("/{name}/metadata/ensure")
async def ensure_metadata_persistence(name: str, db: AsyncSession = Depends(get_db)):
    """
    Ensure metadata is persisted for a database connection.
    
    This endpoint checks if metadata exists and refreshes it if needed,
    ensuring compliance with requirement 8.3: metadata updates are saved to SQLite database.
    """
    try:
        result = await database_service.ensure_metadata_persistence(db, name)
        return APIResponse.success_response("Metadata persistence ensured", result)
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ensure metadata persistence: {str(e)}")


@router.post("/{name}/metadata/refresh")
async def force_metadata_refresh(name: str, db: AsyncSession = Depends(get_db)):
    """
    Force a metadata refresh for a database connection.
    
    This ensures that any changes to the database schema are captured
    and persisted in the metadata store.
    """
    try:
        result = await database_service.force_metadata_refresh(db, name)
        return APIResponse.success_response("Metadata refreshed successfully", result)
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh metadata: {str(e)}")


@router.post("/test-connection")
async def test_database_connection(
    database: database_schema.DatabaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Test a database connection without saving it."""
    try:
        # Test the connection using the database service
        result = await database_service.test_connection(database.url)
        
        if result["success"]:
            return APIResponse.success_response("Connection test successful", result)
        else:
            # Return the error information from the test
            error_info = result.get("error_info")
            if error_info and isinstance(error_info, DatabaseQueryError):
                raise HTTPException(
                    status_code=get_http_status_code(error_info),
                    detail={
                        "error": error_info.to_dict(),
                        "message": error_info.user_message
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "CONNECTION_FAILED",
                            "message": result["message"]
                        },
                        "message": result["message"]
                    }
                )
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test database connection: {str(e)}")


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
