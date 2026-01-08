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


@router.post("/{name}/query")
async def execute_query(
    name: str,
    query: query_schema.QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a SQL query."""
    try:
        result = await database_service.execute_query(db, name, query.sql)
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


@router.post("/{name}/query/natural")
async def execute_natural_language_query(
    name: str, 
    query: query_schema.NaturalLanguageQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a natural language query."""
    try:
        # Get database metadata for context
        metadata = await database_service.get_database_metadata(db, name)
        
        # Generate SQL from natural language
        generated_sql = await llm_service.generate_and_validate_sql(
            query.prompt, 
            metadata
        )
        
        # Execute the generated SQL
        result = await database_service.execute_query(db, name, generated_sql)
        
        # Return both the generated SQL and the results
        response_data = {
            "generatedSql": generated_sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "rowCount": result["row_count"],
            "executionTimeMs": result["execution_time_ms"],
            "truncated": result.get("truncated", False)
        }
        
        return APIResponse.success_response("Natural language query executed successfully", response_data)
        
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
