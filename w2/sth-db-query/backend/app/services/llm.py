"""
LLM service integration for natural language to SQL conversion.

This module provides integration with OpenAI-compatible APIs (GLM) for
converting natural language queries to SQL statements.
"""

import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for natural language to SQL conversion using LLM."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.glm_api_key,
            base_url=settings.glm_base_url,
        )
        self.model = "glm-4"  # GLM-4 model for text generation

    async def generate_sql(
        self,
        natural_language_query: str,
        database_schema: Dict[str, Any],
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """
        Generate SQL from natural language query using database schema context.

        Args:
            natural_language_query: User's natural language description
            database_schema: Database metadata including tables and columns
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation (lower = more deterministic)

        Returns:
            Generated SQL query string

        Raises:
            Exception: If SQL generation fails
        """
        try:
            # Build context from database schema
            schema_context = self._build_schema_context(database_schema)

            # Create prompt for SQL generation
            prompt = self._create_sql_generation_prompt(
                natural_language_query,
                schema_context
            )

            # Call LLM API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Generate only the SQL query without any explanation or markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract generated SQL
            generated_sql = response.choices[0].message.content.strip()

            # Clean up the response (remove markdown code blocks if present)
            generated_sql = self._clean_sql_response(generated_sql)

            logger.info(f"Generated SQL for query: {natural_language_query[:50]}...")

            return generated_sql

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise Exception(f"SQL generation failed: {str(e)}")

    def _build_schema_context(self, database_schema: Dict[str, Any]) -> str:
        """
        Build schema context string from database metadata.

        Args:
            database_schema: Database schema information

        Returns:
            Formatted schema context for LLM
        """
        context_parts = []

        # Add table information
        if "tables" in database_schema:
            context_parts.append("Tables:")
            for table in database_schema["tables"]:
                table_name = table.get("name", "")
                schema_name = table.get("schema", "public")
                columns = table.get("columns", [])

                context_parts.append(f"  {schema_name}.{table_name}:")
                for col in columns:
                    col_info = f"    - {col['name']} ({col['data_type']})"
                    if col.get("is_primary_key"):
                        col_info += " [PRIMARY KEY]"
                    if not col.get("is_nullable", True):
                        col_info += " [NOT NULL]"
                    context_parts.append(col_info)

        # Add view information
        if "views" in database_schema:
            context_parts.append("\nViews:")
            for view in database_schema["views"]:
                view_name = view.get("name", "")
                schema_name = view.get("schema", "public")
                columns = view.get("columns", [])

                context_parts.append(f"  {schema_name}.{view_name}:")
                for col in columns:
                    context_parts.append(f"    - {col['name']} ({col['data_type']})")

        return "\n".join(context_parts)

    def _create_sql_generation_prompt(
        self,
        natural_language_query: str,
        schema_context: str
    ) -> str:
        """
        Create the prompt for SQL generation.

        Args:
            natural_language_query: User's query
            schema_context: Database schema information

        Returns:
            Complete prompt for LLM
        """
        prompt = f"""
Given the following database schema:

{schema_context}

Generate a PostgreSQL SELECT query for the following request:
{natural_language_query}

Important rules:
- Only generate SELECT statements
- Use proper table and column names from the schema
- Include appropriate JOINs when needed
- Use table aliases when joining multiple tables
- Ensure the query is syntactically correct
- Do not include any explanation, just the SQL query
- Use double quotes for identifiers if they contain special characters
"""

        return prompt.strip()

    def _clean_sql_response(self, sql_response: str) -> str:
        """
        Clean up the SQL response from LLM.

        Args:
            sql_response: Raw response from LLM

        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks
        sql_response = sql_response.strip()
        if sql_response.startswith("```sql"):
            sql_response = sql_response[6:]
        elif sql_response.startswith("```"):
            sql_response = sql_response[3:]

        if sql_response.endswith("```"):
            sql_response = sql_response[:-3]

        # Clean up and return
        return sql_response.strip()


# Global LLM service instance
llm_service = LLMService()
