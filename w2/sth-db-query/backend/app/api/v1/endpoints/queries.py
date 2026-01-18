"""
Query execution endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database import DatabaseService
from app.services.llm import llm_service
from app.schemas import query as query_schema
from app.utils.response import APIResponse
from app.core.errors import DatabaseQueryError, get_http_status_code

router = APIRouter()
database_service = DatabaseService()


@router.post("/{id}/query")
async def execute_query(
    id: str,
    query: query_schema.QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a SQL query."""
    try:
        # Get database by id to get connection details
        database = await database_service.get_database(db, id)
        if not database:
            raise HTTPException(status_code=404, detail=f"Database with id '{id}' not found")
        
        # Execute query using database URL directly
        result = await database_service.execute_query_by_url(database.url, query.sql)
        return APIResponse.success_response("Query executed successfully", result)
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except Exception as e:
        return APIResponse.error_response("Query execution failed", str(e))


@router.post("/{id}/query/natural")
async def execute_natural_language_query(
    id: str, 
    query: query_schema.NaturalLanguageQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate SQL from natural language query without executing it."""
    try:
        # Get database by id to get connection details
        database = await database_service.get_database(db, id)
        if not database:
            raise HTTPException(status_code=404, detail=f"Database with id '{id}' not found")
        
        # Get database metadata for context
        metadata = await database_service.get_database_metadata(db, database.name)
        
        # Generate SQL from natural language
        generated_sql = await llm_service.generate_and_validate_sql(
            query.prompt, 
            metadata
        )
        
        # Return only the generated SQL
        response_data = {
            "generatedSql": generated_sql
        }
        
        return APIResponse.success_response("SQL generated successfully from natural language query", response_data)
        
    except DatabaseQueryError as e:
        raise HTTPException(
            status_code=get_http_status_code(e),
            detail={
                "error": e.to_dict(),
                "message": e.user_message
            }
        )
    except Exception as e:
        return APIResponse.error_response("Natural language query execution failed", str(e))
