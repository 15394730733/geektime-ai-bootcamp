"""
Query execution endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.schemas import query as query_schema

router = APIRouter()


@router.post("/{name}/query", response_model=query_schema.QueryResult)
async def execute_query(name: str, query: query_schema.QueryRequest):
    """Execute a SQL query."""
    # TODO: Implement query execution
    pass


@router.post("/{name}/query/natural", response_model=query_schema.NaturalLanguageQueryResult)
async def execute_natural_language_query(name: str, query: query_schema.NaturalLanguageQueryRequest):
    """Execute a natural language query."""
    # TODO: Implement natural language query processing
    pass
