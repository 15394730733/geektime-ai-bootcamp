"""
Property-based tests for CORS support.

Feature: database-query-tool, Property 21: API CORS support
Validates: Requirements 9.1
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import composite
from typing import Dict, Any


@composite
def valid_origins(draw):
    """Generate valid origin headers."""
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://example.com",
        "https://app.example.com",
        "http://127.0.0.1:8080",
        "https://mydomain.org",
        "http://frontend.local:4200",
        "https://secure-app.com"
    ]
    return draw(st.sampled_from(origins))


@composite
def api_endpoints(draw):
    """Generate API endpoint paths to test CORS on."""
    endpoints = [
        "/api/v1/dbs",
        "/api/v1/dbs/test-db",
        "/api/v1/dbs/test-db/query",
        "/api/v1/dbs/test-db/query/natural",
        "/health"
    ]
    return draw(st.sampled_from(endpoints))


@composite
def http_methods(draw):
    """Generate HTTP methods that should support CORS."""
    methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    return draw(st.sampled_from(methods))


class TestCORSProperties:
    """Property-based tests for CORS support."""

    @given(origin=valid_origins(), endpoint=api_endpoints())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cors_headers_present_for_all_origins(self, client, origin, endpoint):
        """
        Property 21: API CORS support
        For any valid origin and any API endpoint, CORS headers should be present
        in the response to allow cross-origin requests.
        
        **Validates: Requirements 9.1**
        """
        # Make an OPTIONS request (preflight) with Origin header
        response = client.options(endpoint, headers={"Origin": origin})
        
        # CORS middleware should add headers regardless of status code
        # Some endpoints may return 405 Method Not Allowed for OPTIONS, which is expected
        assert response.status_code in [200, 405], f"Unexpected status code: {response.status_code}"
        
        # Should have CORS headers even for 405 responses
        headers = response.headers
        assert "access-control-allow-origin" in headers
        
        # Should allow all origins (*)
        assert headers["access-control-allow-origin"] == "*"

    @given(origin=valid_origins(), endpoint=api_endpoints(), method=http_methods())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cors_headers_for_different_methods(self, client, origin, endpoint, method):
        """
        Property 21: API CORS support
        For any origin, endpoint, and HTTP method, the API should include
        appropriate CORS headers to support cross-origin requests.
        
        **Validates: Requirements 9.1**
        """
        # Make a request with the specified method and Origin header
        headers = {"Origin": origin}
        
        if method == "GET":
            response = client.get(endpoint, headers=headers)
        elif method == "POST":
            response = client.post(endpoint, headers=headers, json={})
        elif method == "PUT":
            response = client.put(endpoint, headers=headers, json={})
        elif method == "DELETE":
            response = client.delete(endpoint, headers=headers)
        else:  # OPTIONS
            response = client.options(endpoint, headers=headers)
        
        # Should have CORS headers regardless of response status
        response_headers = response.headers
        assert "access-control-allow-origin" in response_headers
        
        # Should allow all origins
        assert response_headers["access-control-allow-origin"] == "*"

    @given(endpoint=api_endpoints())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_preflight_options_requests(self, client, endpoint):
        """
        Property 21: API CORS support
        For any API endpoint, OPTIONS requests (CORS preflight) should be handled
        correctly with appropriate CORS headers.
        
        **Validates: Requirements 9.1**
        """
        # Make a preflight OPTIONS request
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = client.options(endpoint, headers=headers)
        
        # Should return 200 or 405 for preflight requests
        assert response.status_code in [200, 405], f"Unexpected status code: {response.status_code}"
        
        # Should have required CORS headers regardless of status code
        response_headers = response.headers
        assert "access-control-allow-origin" in response_headers
        
        # Should allow all origins
        assert response_headers["access-control-allow-origin"] == "*"
        
        # For successful preflight (200), should have additional headers
        if response.status_code == 200:
            assert "access-control-allow-methods" in response_headers
            assert "access-control-allow-headers" in response_headers

    @given(st.text(min_size=5, max_size=50).filter(lambda x: "://" in x))
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.filter_too_much])
    def test_cors_allows_any_origin(self, client, origin):
        """
        Property 21: API CORS support
        For any origin string, the API should allow cross-origin requests
        by returning appropriate CORS headers.
        
        **Validates: Requirements 9.1**
        """
        # Test with a random origin
        response = client.options("/api/v1/dbs", headers={"Origin": origin})
        
        # Should return 200 or 405 and include CORS headers
        assert response.status_code in [200, 405], f"Unexpected status code: {response.status_code}"
        
        response_headers = response.headers
        assert "access-control-allow-origin" in response_headers
        
        # Should allow all origins (wildcard)
        assert response_headers["access-control-allow-origin"] == "*"

    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(api_endpoints(), min_size=2, max_size=5))
    def test_cors_consistency_across_endpoints(self, client, endpoints):
        """
        Property 21: API CORS support
        For any set of API endpoints, CORS headers should be consistently
        applied across all endpoints.
        
        **Validates: Requirements 9.1**
        """
        origin = "https://test-app.com"
        cors_headers = {}
        
        # Test each endpoint and collect CORS headers
        for endpoint in endpoints:
            response = client.options(endpoint, headers={"Origin": origin})
            
            # Accept both 200 and 405 status codes
            if response.status_code in [200, 405]:
                headers = response.headers
                if "access-control-allow-origin" in headers:
                    cors_headers[endpoint] = headers["access-control-allow-origin"]
        
        # All endpoints should have the same CORS policy
        if cors_headers:
            unique_policies = set(cors_headers.values())
            assert len(unique_policies) == 1, f"Inconsistent CORS policies: {cors_headers}"
            assert "*" in unique_policies, f"Should allow all origins, got: {unique_policies}"

    @given(origin=valid_origins())
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cors_with_credentials_handling(self, client, origin):
        """
        Property 21: API CORS support
        For any origin, when CORS allows all origins (*), credentials should
        be handled appropriately (typically not allowed with wildcard).
        
        **Validates: Requirements 9.1**
        """
        # Make a request with credentials
        headers = {
            "Origin": origin,
            "Access-Control-Request-Credentials": "true"
        }
        
        response = client.options("/api/v1/dbs", headers=headers)
        
        # Should return 200 or 405
        assert response.status_code in [200, 405], f"Unexpected status code: {response.status_code}"
        
        response_headers = response.headers
        assert "access-control-allow-origin" in response_headers
        
        # When using wildcard (*), credentials should not be allowed
        if response_headers["access-control-allow-origin"] == "*":
            # Should not have allow-credentials: true with wildcard origin
            credentials_header = response_headers.get("access-control-allow-credentials", "").lower()
            assert credentials_header != "true", "Cannot allow credentials with wildcard origin"
