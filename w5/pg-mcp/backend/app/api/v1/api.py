"""
API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import databases, queries

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    databases.router,
    prefix="/dbs",
    tags=["databases"]
)

api_router.include_router(
    queries.router,
    prefix="/dbs",
    tags=["queries"]
)
