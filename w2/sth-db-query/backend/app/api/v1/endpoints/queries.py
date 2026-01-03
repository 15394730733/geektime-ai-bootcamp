"""
Query execution endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database import DatabaseService
from app.schemas import query as query_schema
from app.utils.response import APIResponse

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
    except Exception as e:
        return APIResponse.error_response("Query execution failed", str(e))


@router.post("/{name}/query/natural", response_model=query_schema.NaturalLanguageQueryResult)
async def execute_natural_language_query(name: str, query: query_schema.NaturalLanguageQueryRequest):
    """Execute a natural language query."""
    # TODO: Implement natural language query processing
    pass
