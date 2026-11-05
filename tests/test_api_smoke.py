"""Smoke tests for the FastAPI application and its routes."""

EXPECTED_AUTH_ROUTES = [
    ("POST", "/api/v1/auth/token"),
    ("POST", "/api/v1/auth/logout"),
    ("POST", "/api/v1/auth/token/refresh"),
    ("GET", "/api/v1/auth/me"),
]


def test_auth_routes_in_openapi():
    from main import app

    schema = app.openapi()
    for method, path in EXPECTED_AUTH_ROUTES:
        assert path in schema["paths"], f"{path} not in OpenAPI schema"
        assert method.lower() in schema["paths"][path], f"{method} {path} missing"


def test_openapi_schema_components():
    from main import app

    schema = app.openapi()
    assert "LoginRequest" in schema["components"]["schemas"]


async def test_placeholder_endpoint_returns_500_not_404(client):
    """Auth handlers are stubs — they exist and are routed (they will raise inside).

    This guards against routes accidentally disappearing while implementation is pending.
    """
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code != 404
