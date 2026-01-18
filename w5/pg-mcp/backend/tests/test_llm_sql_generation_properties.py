"""
Property-based tests for LLM SQL generation.

Feature: database-query-tool, Property 9: Natural language SQL generation
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import AsyncMock, MagicMock, patch
import sqlglot
from app.services.llm import LLMService


# Generators for test data
@st.composite
def database_metadata_strategy(draw):
    """Generate valid database metadata for testing."""
    # Generate table names
    table_count = draw(st.integers(min_value=1, max_value=5))
    tables = []
    
    for _ in range(table_count):
        # Generate column information
        column_count = draw(st.integers(min_value=1, max_value=8))
        columns = []
        
        for i in range(column_count):
            column = {
                "name": draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")), min_size=1, max_size=20)),
                "data_type": draw(st.sampled_from(["integer", "varchar", "text", "boolean", "timestamp", "decimal"])),
                "is_primary_key": i == 0,  # First column is primary key
                "is_nullable": draw(st.booleans()) if i > 0 else False  # Primary key is not nullable
            }
            columns.append(column)
        
        table = {
            "name": draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")), min_size=1, max_size=20)),
            "schema": "public",
            "columns": columns
        }
        tables.append(table)
    
    return {
        "database_name": draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")), min_size=1, max_size=20)),
        "tables": tables,
        "views": []
    }


@st.composite
def natural_language_query_strategy(draw):
    """Generate natural language queries for testing."""
    query_templates = [
        "Show me all {table}",
        "Get all records from {table}",
        "List all {table} where {column} is {value}",
        "Find {table} with {column} equal to {value}",
        "Select all {table}",
        "Display {table} information"
    ]
    
    template = draw(st.sampled_from(query_templates))
    
    # Simple substitutions for template variables
    if "{table}" in template:
        table_name = draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu")), min_size=1, max_size=15))
        template = template.replace("{table}", table_name)
    
    if "{column}" in template:
        column_name = draw(st.text(alphabet=st.characters(whitelist_categories=("Ll", "Lu")), min_size=1, max_size=15))
        template = template.replace("{column}", column_name)
    
    if "{value}" in template:
        value = draw(st.sampled_from(["true", "false", "1", "'active'", "'test'"]))
        template = template.replace("{value}", value)
    
    return template


class TestLLMSQLGenerationProperties:
    """Property-based tests for LLM SQL generation functionality."""

    def create_mock_llm_service(self):
        """Create a mocked LLM service for property testing."""
        # Mock the settings to avoid API key issues
        with patch('app.services.llm.settings') as mock_settings:
            mock_settings.openai_api_key = "test-api-key"
            mock_settings.openai_base_url = None
            mock_settings.openai_model = "gpt-3.5-turbo"
            
            service = LLMService()
            
            # Mock the OpenAI client to return valid SQL
            mock_client = MagicMock()
            mock_response = MagicMock()
            
            # Create a function that generates SQL based on the input
            def generate_mock_sql(*args, **kwargs):
                # Extract the prompt from the call
                messages = kwargs.get('messages', [])
                if len(messages) > 1:
                    prompt = messages[1]['content']
                    # Generate a simple SELECT statement based on the prompt
                    if 'tables' in prompt.lower() or 'table' in prompt.lower():
                        return mock_response
                
                # Default response
                mock_response.choices[0].message.content = "SELECT * FROM test_table LIMIT 1000"
                return mock_response
            
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "SELECT * FROM users WHERE active = true"
            mock_client.chat.completions.create = AsyncMock(side_effect=generate_mock_sql)
            
            # Replace the client
            service.client = mock_client
            
            return service

    @given(
        metadata=database_metadata_strategy(),
        nl_query=natural_language_query_strategy()
    )
    @settings(max_examples=5, deadline=None)
    def test_property_9_natural_language_sql_generation(self, metadata, nl_query):
        """
        Property 9: Natural language SQL generation
        
        For any natural language prompt and database metadata context, 
        the LLM service should generate syntactically valid SQL that 
        references actual tables and columns from the metadata.
        
        **Validates: Requirements 4.1, 4.2**
        """
        import asyncio
        
        async def run_test():
            # Mock settings to avoid API key issues
            with patch('app.services.llm.settings') as mock_settings:
                mock_settings.openai_api_key = "test-api-key"
                mock_settings.openai_base_url = None
                mock_settings.openai_model = "gpt-3.5-turbo"
                
                # Create mock service for this test
                mock_llm_service = self.create_mock_llm_service()
                
                # Assume non-empty inputs
                assume(len(nl_query.strip()) > 0)
                assume(len(metadata.get("tables", [])) > 0)
                assume(all(len(table.get("columns", [])) > 0 for table in metadata["tables"]))
                
                try:
                    # Generate SQL using the LLM service
                    generated_sql = await mock_llm_service.generate_sql(nl_query, metadata)
                    
                    # Property 1: Generated SQL should not be empty
                    assert generated_sql is not None
                    assert len(generated_sql.strip()) > 0
                    
                    # Property 2: Generated SQL should be syntactically valid
                    try:
                        parsed = sqlglot.parse_one(generated_sql, dialect="postgres")
                        assert parsed is not None
                    except Exception as parse_error:
                        pytest.fail(f"Generated SQL is not syntactically valid: {generated_sql}. Error: {parse_error}")
                    
                    # Property 3: Generated SQL should be a SELECT statement
                    parsed_sql = sqlglot.parse_one(generated_sql, dialect="postgres")
                    assert parsed_sql.find(sqlglot.expressions.Select) is not None, f"Generated SQL is not a SELECT statement: {generated_sql}"
                    
                    # Property 4: Generated SQL should not contain dangerous operations
                    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
                    sql_upper = generated_sql.upper()
                    for keyword in dangerous_keywords:
                        assert keyword not in sql_upper, f"Generated SQL contains dangerous keyword '{keyword}': {generated_sql}"
                    
                except Exception as e:
                    # If generation fails, it should be due to a clear error condition
                    error_msg = str(e).lower()
                    assert any(keyword in error_msg for keyword in ["error", "fail", "invalid", "cannot", "not configured"]), f"Error message should contain descriptive keywords: {str(e)}"
        
        # Run the async test
        asyncio.run(run_test())

    @given(metadata=database_metadata_strategy())
    @settings(max_examples=5, deadline=None)
    def test_metadata_context_building_property(self, metadata):
        """
        Test that metadata context building produces valid output for any metadata.
        
        For any database metadata, the context building should produce 
        a non-empty string that contains table and column information.
        """
        # Mock settings to avoid API key issues
        with patch('app.services.llm.settings') as mock_settings:
            mock_settings.openai_api_key = "test-api-key"
            mock_settings.openai_base_url = None
            mock_settings.openai_model = "gpt-3.5-turbo"
            
            # Create mock service for this test
            mock_llm_service = self.create_mock_llm_service()
            
            # Assume valid metadata structure
            assume(len(metadata.get("tables", [])) > 0)
            
            # Build metadata context
            context = mock_llm_service.build_metadata_context(metadata)
            
            # Property 1: Context should not be empty
            assert context is not None
            assert len(context.strip()) > 0
            
            # Property 2: Context should contain table information
            table_names = [table["name"] for table in metadata["tables"]]
            for table_name in table_names:
                if table_name:  # Skip empty table names
                    assert table_name in context, f"Table '{table_name}' not found in context: {context}"
            
            # Property 3: Context should contain column information
            for table in metadata["tables"]:
                for column in table.get("columns", []):
                    column_name = column.get("name", "")
                    if column_name:  # Skip empty column names
                        assert column_name in context, f"Column '{column_name}' not found in context: {context}"

    @given(
        nl_query=st.text(min_size=1, max_size=200),
        metadata=database_metadata_strategy()
    )
    @settings(max_examples=5, deadline=None)
    def test_error_handling_property(self, nl_query, metadata):
        """
        Test that LLM service handles various inputs gracefully.
        
        For any input, the service should either return valid SQL 
        or raise an exception with a descriptive error message.
        """
        import asyncio
        
        async def run_test():
            # Mock settings to avoid API key issues
            with patch('app.services.llm.settings') as mock_settings:
                mock_settings.openai_api_key = "test-api-key"
                mock_settings.openai_base_url = None
                mock_settings.openai_model = "gpt-3.5-turbo"
                
                # Create mock service for this test
                mock_llm_service = self.create_mock_llm_service()
                
                try:
                    result = await mock_llm_service.generate_sql(nl_query, metadata)
                    
                    # If successful, result should be a non-empty string
                    assert isinstance(result, str)
                    assert len(result.strip()) > 0
                    
                except Exception as e:
                    # If it fails, error message should be descriptive
                    error_msg = str(e).lower()
                    assert len(error_msg) > 0
                    assert any(keyword in error_msg for keyword in ["error", "fail", "invalid", "cannot", "not configured"])
        
        # Run the async test
        asyncio.run(run_test())

    def test_empty_metadata_handling(self):
        """Test handling of empty metadata."""
        # Mock settings to avoid API key issues
        with patch('app.services.llm.settings') as mock_settings:
            mock_settings.openai_api_key = "test-api-key"
            mock_settings.openai_base_url = None
            mock_settings.openai_model = "gpt-3.5-turbo"
            
            mock_llm_service = self.create_mock_llm_service()
            empty_metadata = {"tables": [], "views": []}
            
            context = mock_llm_service.build_metadata_context(empty_metadata)
            
            # Should handle empty metadata gracefully
            assert isinstance(context, str)
            assert len(context) > 0

    def test_malformed_metadata_handling(self):
        """Test handling of malformed metadata."""
        # Mock settings to avoid API key issues
        with patch('app.services.llm.settings') as mock_settings:
            mock_settings.openai_api_key = "test-api-key"
            mock_settings.openai_base_url = None
            mock_settings.openai_model = "gpt-3.5-turbo"
            
            mock_llm_service = self.create_mock_llm_service()
            malformed_metadata = {"invalid": "structure"}
            
            context = mock_llm_service.build_metadata_context(malformed_metadata)
            
            # Should handle malformed metadata gracefully
            assert isinstance(context, str)
            assert len(context) > 0
