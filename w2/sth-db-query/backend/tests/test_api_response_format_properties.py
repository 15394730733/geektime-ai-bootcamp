"""
Property-based tests for API response formatting.

Feature: database-query-tool, Property 23: API response format
Validates: Requirements 9.7
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
import json
import re
from typing import Dict, Any


@composite
def api_endpoints_with_methods(draw):
    """Generate API endpoint and method combinations."""
    endpoints_methods = [
        ("/api/v1/dbs", "GET"),
        ("/api/v1/dbs", "POST"),
        ("/health", "GET"),
    ]
    return draw(st.sampled_from(endpoints_methods))


def is_camel_case(field_name: str) -> bool:
    """Check if a field name follows camelCase convention."""
    if not field_name:
        return False
    
    # Should start with lowercase letter
    if not field_name[0].islower():
        return False
    
    # Should not contain underscores or hyphens
    if '_' in field_name or '-' in field_name:
        return False
    
    # Should be alphanumeric
    if not field_name.replace('_', '').replace('-', '').isalnum():
        return False
    
    return True


def check_camel_case_recursively(data: Any, path: str = "") -> list:
    """
    Recursively check if all field names in a data structure use camelCase.
    Returns a list of violations with their paths.
    """
    violations = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if the key itself is camelCase
            if not is_camel_case(key):
                violations.append(f"Non-camelCase field: {current_path}")
            
            # Recursively check the value
            violations.extend(check_camel_case_recursively(value, current_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            violations.extend(check_camel_case_recursively(item, current_path))
    
    return violations


class TestAPIResponseFormatProperties:
    """Property-based tests for API response format consistency."""

    @given(endpoint_method=api_endpoints_with_methods())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_response_format_consistency(self, client, endpoint_method):
        """
        Property 23: API response format
        For any API endpoint, responses should follow consistent JSON format
        with camelCase field names.
        
        **Validates: Requirements 9.7**
        """
        endpoint, method = endpoint_method
        
        # Make the request
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json={})
        else:
            return  # Skip unsupported methods
        
        # Should return JSON response
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # Some responses might not be JSON (like 404 errors)
            return
        
        # Check that response follows expected structure
        assert isinstance(response_data, dict), "Response should be a JSON object"
        
        # Check for camelCase field names recursively
        violations = check_camel_case_recursively(response_data)
        
        # Allow some exceptions for standard fields
        allowed_exceptions = ["error_code", "stack_trace", "detail"]  # Common error fields
        filtered_violations = [v for v in violations if not any(exc in v for exc in allowed_exceptions)]
        
        assert len(filtered_violations) == 0, f"CamelCase violations found: {filtered_violations}"

    @given(st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum()))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_database_response_format(self, client, database_name):
        """
        Property 23: API response format
        For any database name, database-related API responses should use
        camelCase field names consistently.
        
        **Validates: Requirements 9.7**
        """
        # Test getting a database (will likely return 404, but format should be consistent)
        response = client.get(f"/api/v1/dbs/{database_name}")
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return  # Skip if not JSON
        
        # Check camelCase formatting
        violations = check_camel_case_recursively(response_data)
        
        # Filter out known exceptions
        allowed_exceptions = ["error_code", "stack_trace", "detail"]
        filtered_violations = [v for v in violations if not any(exc in v for exc in allowed_exceptions)]
        
        assert len(filtered_violations) == 0, f"CamelCase violations in database response: {filtered_violations}"

    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(st.text(min_size=1, max_size=10).filter(lambda x: x.isalnum()), min_size=1, max_size=3))
    def test_error_response_format_consistency(self, client, invalid_paths):
        """
        Property 23: API response format
        For any invalid API path, error responses should maintain consistent
        JSON format with camelCase field names.
        
        **Validates: Requirements 9.7**
        """
        # Create an invalid path
        invalid_path = "/api/v1/" + "/".join(invalid_paths)
        
        response = client.get(invalid_path)
        
        # Should return some kind of error
        assert response.status_code >= 400
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            # Some error responses might not be JSON
            return
        
        # Check camelCase formatting in error responses
        violations = check_camel_case_recursively(response_data)
        
        # Allow common error field exceptions
        allowed_exceptions = ["error_code", "stack_trace", "detail", "loc", "msg", "type"]
        filtered_violations = [v for v in violations if not any(exc in v for exc in allowed_exceptions)]
        
        assert len(filtered_violations) == 0, f"CamelCase violations in error response: {filtered_violations}"

    @given(st.dictionaries(st.text(min_size=1, max_size=10), st.text(max_size=50), min_size=1, max_size=3))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_post_request_response_format(self, client, request_data):
        """
        Property 23: API response format
        For any POST request data, the API response should maintain consistent
        camelCase formatting regardless of input format.
        
        **Validates: Requirements 9.7**
        """
        # Make a POST request to databases endpoint
        response = client.post("/api/v1/dbs", json=request_data)
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return  # Skip if not JSON
        
        # Check camelCase formatting
        violations = check_camel_case_recursively(response_data)
        
        # Allow validation error exceptions
        allowed_exceptions = ["error_code", "stack_trace", "detail", "loc", "msg", "type", "input"]
        filtered_violations = [v for v in violations if not any(exc in v for exc in allowed_exceptions)]
        
        assert len(filtered_violations) == 0, f"CamelCase violations in POST response: {filtered_violations}"

    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(api_endpoints_with_methods(), min_size=2, max_size=4))
    def test_response_format_consistency_across_endpoints(self, client, endpoint_methods):
        """
        Property 23: API response format
        For any set of API endpoints, all responses should follow the same
        camelCase formatting conventions consistently.
        
        **Validates: Requirements 9.7**
        """
        all_violations = []
        
        for endpoint, method in endpoint_methods:
            # Make the request
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            else:
                continue
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                continue
            
            # Check camelCase formatting
            violations = check_camel_case_recursively(response_data)
            
            # Filter exceptions
            allowed_exceptions = ["error_code", "stack_trace", "detail", "loc", "msg", "type"]
            filtered_violations = [v for v in violations if not any(exc in v for exc in allowed_exceptions)]
            
            if filtered_violations:
                all_violations.extend([f"{endpoint} {method}: {v}" for v in filtered_violations])
        
        assert len(all_violations) == 0, f"CamelCase violations across endpoints: {all_violations}"

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_health_endpoint_response_format(self, client, origin):
        """
        Property 23: API response format
        For any request to the health endpoint, the response should use
        camelCase field names consistently.
        
        **Validates: Requirements 9.7**
        """
        # Test health endpoint with various origins
        headers = {"Origin": origin} if "://" in origin else {}
        response = client.get("/health", headers=headers)
        
        # Should return 200 for health check
        assert response.status_code == 200
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return
        
        # Check camelCase formatting
        violations = check_camel_case_recursively(response_data)
        
        assert len(violations) == 0, f"CamelCase violations in health response: {violations}"
