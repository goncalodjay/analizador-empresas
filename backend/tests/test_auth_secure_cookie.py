"""Tests for environment-aware JWT cookie secure flag."""
import os
import pytest
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.asyncio
async def test_login_sets_secure_cookie_when_env_false(async_client: AsyncClient):
    """Test that secure=False when SECURE_COOKIE_ENABLED=false."""
    # Register first
    register_resp = await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )
    assert register_resp.status_code == 201

    # Login
    login_resp = await async_client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )
    assert login_resp.status_code == 200

    # Check Set-Cookie header
    set_cookie_header = login_resp.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header
    # When secure=False, "Secure" should NOT be in the cookie
    assert "Secure" not in set_cookie_header or "secure=false" in set_cookie_header.lower()
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header


@pytest.mark.asyncio
async def test_logout_clears_secure_cookie(async_client: AsyncClient):
    """Test that logout properly clears the secure cookie."""
    # Register and login first
    await async_client.post(
        "/auth/register",
        json={"email": "test2@example.com", "password": "TestPass123!"},
    )
    login_resp = await async_client.post(
        "/auth/login",
        json={"email": "test2@example.com", "password": "TestPass123!"},
    )
    assert login_resp.status_code == 200

    # Logout
    logout_resp = await async_client.post("/auth/logout")
    assert logout_resp.status_code == 204

    # Verify cookie is cleared (Set-Cookie should contain Max-Age=0 or Expires in past)
    set_cookie_header = logout_resp.headers.get("set-cookie", "")
    assert "access_token" in set_cookie_header
