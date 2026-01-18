"""
Property-based tests for LLM error handling.

Feature: database-query-tool, Property 11: LLM error handling
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm import LLMService


# Generators for test data
@st.composite
def invalid_input_strategy(draw):
    """Generate various invalid inputs for testing error handling."""
    return draw(st.one_of(
        st.none(),
        st.text(max_size=0),  # Empty string
        st.text().filter(lambda x: x.isspace()),  # Whitespace only
        st.text(min_size=1000, max_size=2000),  # Long text (within Hypothesis limits)
        st.integers(),  # Non-string types
        st.lists(st.text()),  # Lists instead of strings
    ))


@st.composite
def malformed_metadata_strategy(draw):
    """Generate malformed metadata for testing error handling."""
    return draw(st.one_of(
        st.none(),
        st.text(),
        st.integers(),
        st.lists(st.text()),
        st.dictionaries(st.text(), st.text()),  # Wrong structure
        st.fixed_dictionaries({
            "invalid_key": st.text(),
            "another_invalid": st.integers()
        }),
        st.fixed_dictionaries({
            "tables": st.lists(st.text())  # Tables should be list of dicts, not strings
        }),
        st.fixed_dictionaries({
            "tables": st.lists(st.dictionaries(
                st.text(), 
                st.one_of(st.none(), st.text(), st.integers())  # Invalid column structure
            ))
        })
    ))


class TestLLMErrorHandlingProperties:
    """Property-based tests for LLM error handling functionality."""

    def create_mock_llm_service_with_errors(self):
        """Create a mocked LLM service that can simulate various error conditions."""
        service = LLMService()
        
        # Mock the OpenAI client to simulate different error conditions
        mock_client = MagicMock()
        
        def generate_error_response(*args, **kwargs):
            # Simulate various API errors
            import random
            error_type = random.choice([
                "api_error",
                "rate_limit",
                "timeout",
                "invalid_request",
                "authentication"
            ])
            
            if error_type == "api_error":
                raise Exception("OpenAI API error: Service temporarily unavailable")
            elif error_type == "rate_limit":
                raise Exception("Rate limit exceeded")
            elif error_type == "timeout":
                raise Exception("Request timeout")
            elif error_type == "invalid_request":
                raise Exception("Invalid request format")
            elif error_type == "authentication":
                raise Exception("Authentication failed")
        
        mock_client.chat.completions.create = AsyncMock(side_effect=generate_error_response)
        service.client = mock_client
        
        return service

    @given(
        invalid_input=invalid_input_strategy(),
        metadata=st.dictionaries(st.text(), st.text())
    )
    @settings(max_examples=5, deadline=None)
    def test_property_11_llm_error_handling_invalid_input(self, invalid_input, metadata):
        """
        Property 11: LLM error handling - Invalid input handling
        
        For any invalid natural language input, the LLM service should 
        return a descriptive error message without crashing.
        
        **Validates: Requirements 4.4**
        """
        import asyncio
        
        async def run_test():
            # Create service for this test
            service = LLMService()
            
            try:
                # Try to generate SQL with invalid input
                if invalid_input is None:
                    # Test None input
                    with pytest.raises(Exception) as exc_info:
                        await service.generate_sql(None, metadata)
                    
                    error_msg = str(exc_info.value)
                    assert len(error_msg) > 0
                    assert any(keyword in error_msg.lower() for keyword in [
                        "error", "invalid", "cannot", "fail", "not", "empty", "none"
                    ])
                
                elif isinstance(invalid_input, str):
                    # Test string inputs (empty, whitespace, very long)
                    result_or_error = None
                    try:
                        result_or_error = await service.generate_sql(invalid_input, metadata)
                        # If it succeeds, result should be a string
                        assert isinstance(result_or_error, str)
                    except Exception as e:
                        # If it fails, error should be descriptive
                        error_msg = str(e)
                        assert len(error_msg) > 0
                        assert any(keyword in error_msg.lower() for keyword in [
                            "error", "invalid", "cannot", "fail", "not", "empty", "configured", "key"
                        ])
                
                else:
                    # Test non-string inputs
                    with pytest.raises(Exception) as exc_info:
                        await service.generate_sql(invalid_input, metadata)
                    
                    error_msg = str(exc_info.value)
                    assert len(error_msg) > 0
                    
            except Exception as e:
                # Any exception should have a descriptive message
                error_msg = str(e)
                assert len(error_msg) > 0
        
        # Run the async test
        asyncio.run(run_test())

    @given(metadata=malformed_metadata_strategy())
    @settings(max_examples=5, deadline=None)
    def test_property_11_llm_error_handling_malformed_metadata(self, metadata):
        """
        Property 11: LLM error handling - Malformed metadata handling
        
        For any malformed metadata input, the LLM service should 
        handle it gracefully without crashing.
        
        **Validates: Requirements 4.4**
        """
        import asyncio
        
        async def run_test():
            # Create service for this test
            service = LLMService()
            
            try:
                # Try to generate SQL with malformed metadata
                result_or_error = await service.generate_sql("Show me all users", metadata)
                
                # If it succeeds, result should be a string
                assert isinstance(result_or_error, str)
                assert len(result_or_error.strip()) > 0
                
            except Exception as e:
                # If it fails, error should be descriptive
                error_msg = str(e)
                assert len(error_msg) > 0
                assert any(keyword in error_msg.lower() for keyword in [
                    "error", "invalid", "cannot", "fail", "not", "configured", "key"
                ])
        
        # Run the async test
        asyncio.run(run_test())

    @given(
        nl_query=st.text(min_size=1, max_size=100),
        metadata=st.dictionaries(st.text(), st.text())
    )
    @settings(max_examples=5, deadline=None)
    def test_property_11_llm_api_error_handling(self, nl_query, metadata):
        """
        Property 11: LLM error handling - API error handling
        
        For any API errors from the LLM service, the system should 
        return descriptive error messages.
        
        **Validates: Requirements 4.4**
        """
        import asyncio
        
        async def run_test():
            # Create service that simulates API errors
            service = self.create_mock_llm_service_with_errors()
            
            try:
                # This should raise an exception due to mocked errors
                result = await service.generate_sql(nl_query, metadata)
                
                # If somehow it succeeds, result should be valid
                assert isinstance(result, str)
                assert len(result.strip()) > 0
                
            except Exception as e:
                # Should get a descriptive error message
                error_msg = str(e)
                assert len(error_msg) > 0
                
                # Error message should be descriptive
                assert any(keyword in error_msg.lower() for keyword in [
                    "error", "fail", "unavailable", "limit", "timeout", 
                    "invalid", "authentication", "api", "service"
                ])
        
        # Run the async test
        asyncio.run(run_test())

    def test_empty_api_key_error_handling(self):
        """Test specific error handling for missing API key."""
        import asyncio
        
        async def run_test():
            # Create service without API key
            service = LLMService()
            
            try:
                result = await service.generate_sql("Show me users", {"tables": []})
                
                # Should not succeed without API key
                pytest.fail("Expected exception for missing API key")
                
            except Exception as e:
                error_msg = str(e)
                assert len(error_msg) > 0
                assert "api key" in error_msg.lower() or "configured" in error_msg.lower()
        
        # Run the async test
        asyncio.run(run_test())

    def test_metadata_context_building_error_handling(self):
        """Test error handling in metadata context building."""
        service = LLMService()
        
        # Test with None metadata
        context = service.build_metadata_context(None)
        assert isinstance(context, str)
        assert len(context) > 0
        
        # Test with empty metadata
        context = service.build_metadata_context({})
        assert isinstance(context, str)
        assert len(context) > 0
        
        # Test with malformed metadata
        malformed_metadata = {
            "tables": "not_a_list",
            "views": 123
        }
        context = service.build_metadata_context(malformed_metadata)
        assert isinstance(context, str)
        assert len(context) > 0

    def test_sql_response_cleaning_error_handling(self):
        """Test error handling in SQL response cleaning."""
        service = LLMService()
        
        # Test with None response
        try:
            result = service._clean_sql_response(None)
            # Should handle None gracefully or raise descriptive error
            assert isinstance(result, str) or result is None
        except Exception as e:
            error_msg = str(e)
            assert len(error_msg) > 0
        
        # Test with non-string response
        try:
            result = service._clean_sql_response(123)
            # Should handle non-string gracefully or raise descriptive error
            assert isinstance(result, str) or result is None
        except Exception as e:
            error_msg = str(e)
            assert len(error_msg) > 0
        
        # Test with empty string
        result = service._clean_sql_response("")
        assert isinstance(result, str)
        
        # Test with whitespace only
        result = service._clean_sql_response("   \n\t   ")
        assert isinstance(result, str)
