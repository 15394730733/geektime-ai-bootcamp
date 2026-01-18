"""
Application startup service for data loading and initialization.

This module handles loading stored database connections on application startup,
initializing the metadata store if needed, and gracefully handling startup errors.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.crud.database import get_databases
from app.models.database import DatabaseConnection
from app.schemas.database import Database
from app.core.init_db import init_database_if_needed

logger = logging.getLogger(__name__)


class StartupService:
    """Service for handling application startup data loading."""

    def __init__(self):
        self._loaded_connections: List[Database] = []
        self._startup_completed = False
        self._startup_errors: List[str] = []

    async def initialize_application(self) -> Dict[str, Any]:
        """
        Initialize the application by setting up database and loading data.
        
        Returns:
            Dict containing startup status and loaded data information.
        """
        startup_result = {
            "success": True,
            "database_initialized": False,
            "connections_loaded": 0,
            "errors": [],
            "warnings": []
        }

        try:
            logger.info("Starting application initialization...")

            # Step 1: Initialize metadata store if needed
            try:
                await init_database_if_needed()
                startup_result["database_initialized"] = True
                logger.info("Database initialization completed successfully")
            except Exception as e:
                error_msg = f"Failed to initialize database: {str(e)}"
                logger.error(error_msg)
                startup_result["errors"].append(error_msg)
                startup_result["success"] = False
                return startup_result

            # Step 2: Load stored database connections
            try:
                connections = await self.load_stored_connections()
                self._loaded_connections = connections
                startup_result["connections_loaded"] = len(connections)
                logger.info(f"Loaded {len(connections)} database connections")
            except Exception as e:
                error_msg = f"Failed to load database connections: {str(e)}"
                logger.error(error_msg)
                startup_result["errors"].append(error_msg)
                # This is not a fatal error - app can still start without connections
                startup_result["warnings"].append("Application started but failed to load existing connections")

            # Step 3: Validate loaded connections (optional health check)
            if self._loaded_connections:
                try:
                    validation_result = await self.validate_loaded_connections()
                    if validation_result["warnings"]:
                        startup_result["warnings"].extend(validation_result["warnings"])
                except Exception as e:
                    warning_msg = f"Connection validation failed: {str(e)}"
                    logger.warning(warning_msg)
                    startup_result["warnings"].append(warning_msg)

            self._startup_completed = True
            self._startup_errors = startup_result["errors"]

            if startup_result["success"]:
                logger.info("Application initialization completed successfully")
            else:
                logger.error("Application initialization completed with errors")

            return startup_result

        except Exception as e:
            error_msg = f"Unexpected error during application initialization: {str(e)}"
            logger.error(error_msg, exc_info=True)
            startup_result["success"] = False
            startup_result["errors"].append(error_msg)
            return startup_result

    async def load_stored_connections(self) -> List[Database]:
        """
        Load all stored database connections from the metadata store.
        
        Returns:
            List of Database objects representing stored connections.
        """
        try:
            async with async_session() as db:
                # Get all database connections from the store
                connections = await get_databases(db)
                
                # Convert to Pydantic models for consistent handling
                database_list = []
                for conn in connections:
                    try:
                        database = Database.model_validate(conn)
                        database_list.append(database)
                    except Exception as e:
                        logger.warning(f"Failed to validate connection '{conn.name}': {str(e)}")
                        continue

                logger.info(f"Successfully loaded {len(database_list)} database connections")
                return database_list

        except Exception as e:
            logger.error(f"Error loading stored connections: {str(e)}")
            raise

    async def validate_loaded_connections(self) -> Dict[str, Any]:
        """
        Validate loaded database connections for basic integrity.
        
        Returns:
            Dict containing validation results and any warnings.
        """
        validation_result = {
            "valid_connections": 0,
            "invalid_connections": 0,
            "warnings": []
        }

        for connection in self._loaded_connections:
            try:
                # Basic validation - check required fields
                if not connection.name or not connection.url:
                    validation_result["invalid_connections"] += 1
                    validation_result["warnings"].append(
                        f"Connection '{connection.name}' has missing required fields"
                    )
                    continue

                # Check URL format (basic validation)
                from urllib.parse import urlparse
                parsed = urlparse(connection.url)
                if not parsed.scheme or not parsed.hostname:
                    validation_result["invalid_connections"] += 1
                    validation_result["warnings"].append(
                        f"Connection '{connection.name}' has invalid URL format"
                    )
                    continue

                validation_result["valid_connections"] += 1

            except Exception as e:
                validation_result["invalid_connections"] += 1
                validation_result["warnings"].append(
                    f"Failed to validate connection '{connection.name}': {str(e)}"
                )

        logger.info(
            f"Connection validation completed: {validation_result['valid_connections']} valid, "
            f"{validation_result['invalid_connections']} invalid"
        )

        return validation_result

    def get_loaded_connections(self) -> List[Database]:
        """
        Get the list of connections loaded during startup.
        
        Returns:
            List of Database objects loaded during startup.
        """
        return self._loaded_connections.copy()

    def is_startup_completed(self) -> bool:
        """
        Check if startup process has completed.
        
        Returns:
            True if startup completed (successfully or with errors), False otherwise.
        """
        return self._startup_completed

    def get_startup_errors(self) -> List[str]:
        """
        Get any errors that occurred during startup.
        
        Returns:
            List of error messages from startup process.
        """
        return self._startup_errors.copy()

    async def get_startup_status(self) -> Dict[str, Any]:
        """
        Get comprehensive startup status information.
        
        Returns:
            Dict containing startup status, loaded connections, and error information.
        """
        return {
            "startup_completed": self._startup_completed,
            "connections_loaded": len(self._loaded_connections),
            "startup_errors": self._startup_errors,
            "loaded_connections": [
                {
                    "name": conn.name,
                    "description": conn.description,
                    "is_active": conn.is_active,
                    "created_at": conn.created_at.isoformat() if conn.created_at else None,
                    # Note: last_connected field doesn't exist in the current schema
                    "last_connected": None
                }
                for conn in self._loaded_connections
            ]
        }


# Global startup service instance
startup_service = StartupService()